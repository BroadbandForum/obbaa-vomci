import sqlite3
from sqlite3 import Error
import omci_logger
logger = omci_logger.OmciLogger.getLogger(__name__)

class DB:
    create_table_query = '''
CREATE TABLE IF NOT EXISTS configurations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name varchar not NULL,
  configuration VARCHAR not NULL,
  t TIMESTAMP not NULL DEFAULT CURRENT_TIMESTAMP
);
'''

    insert_cofiguration_query = 'INSERT INTO configurations (name, configuration) VALUES (?, ?);'

    get_configuration_query =  '''
SELECT configuration FROM configurations WHERE name = ? AND 
t= (SELECT MAX(t) FROM configurations WHERE name = ?);
'''

    delete_cofigurations_query = 'DELETE FROM configurations WHERE name = ?;'

    clear_database_query = 'DELETE FROM configurations;'

    drop_database_query = 'DROP TABLE IF EXISTS configurations;'

    select_all_query = 'SELECT * FROM configurations;'

    def __init__(self, name):
        self._db_name = name
        self.create_database()

    def create_database(self):
        try:
            conn = sqlite3.connect(self._db_name)
            conn.cursor().execute(DB.create_table_query)
            conn.commit()
        except Error as e:
            logger.error(e)
            conn.rollback()
        finally:
            conn.close()

    def insert_configuration(self, name: str, configuration: str):
        try:
            conn = sqlite3.connect(self._db_name)
            conn.cursor().execute(DB.insert_cofiguration_query, (name, configuration))
            conn.commit()
        except Error as e:
            logger.error(e)
            conn.rollback()
        finally:
            conn.close()

    def get_configuration(self, name: str) -> str:
        try:
            conn = sqlite3.connect(self._db_name)
            cursor = conn.cursor()
            cursor.execute(DB.get_configuration_query, (name, name))
            ret = cursor.fetchone()
            if ret is not None:
                ret = ret[0]
        except Error as e:
            logger.error(e)
            ret = None
        finally:
            conn.close()
            return ret

    def delete_configurations(self, name: str):
        try:
            conn = sqlite3.connect(self._db_name)
            cursor = conn.cursor()
            cursor.execute(DB.delete_cofigurations_query, (name, ))
            conn.commit()
        except Error as e:
            logger.error(e)
            conn.rollback()
        finally:
            conn.close()

    def clear_database(self):
        try:
            conn = sqlite3.connect(self._db_name)
            conn.cursor().execute(DB.clear_database_query)
            conn.commit()
        except Error as e:
            logger.error(e)
            conn.rollback()
        finally:
            conn.close()

    def drop_database(self):
        try:
            conn = sqlite3.connect(self._db_name)
            conn.cursor().execute(DB.drop_database_query)
            conn.commit()
        except Error as e:
            logger.error(e)
            conn.rollback()
        finally:
            conn.close()

    def get_all(self):
        try:
            conn = sqlite3.connect(self._db_name)
            cursor = conn.cursor()
            cursor.execute(DB.select_all_query)
            ret = cursor.fetchall()
        except Error as e:
            logger.error(e)
            ret = None
        finally:
            conn.close()
            return ret
