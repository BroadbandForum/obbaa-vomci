# Copyright 2020 Broadband Forum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# omci_onu_mib.py : ONU database and MIB
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

"""This module implements per-ONU MIB
"""
from typing import Tuple
from omci_types import *
from database.omci_me import ME
from database.omci_me_types import MeClassMapper
from database.omci_me_types import omci_me_class
from omci_logger import OmciLogger
from collections import OrderedDict
import threading
import copy

logger = OmciLogger.getLogger(__name__)

class OnuMib:
    """ Per-ONU collection of MEs.

    This class is internal and is operated by OnuDriver
    """

    def __init__(self, onu_name: OnuName):
        """ OnuMib Class Constructor.

        Args:
            onu_name: ONU Name
        """
        self._onu_name = onu_name
        self._per_class_dict = {}
        self._lock = threading.Lock()
        self._by_name = {}

    def add(self, me: ME) -> bool:
        """Add ME to the database

        Args:
            me: ME object
        Returns:
            True if successful, False if [me_class, me_inst] already exists in the MIB
        """
        with self._lock:
            if me.me_class not in self._per_class_dict:
                self._per_class_dict[me.me_class] = {me.inst : me}
            else:
                # Some instances for the class already exist
                per_inst_dict = self._per_class_dict[me.me_class]
                if me.inst in per_inst_dict:
                    logger.error("OnuMib.Add %r: ME[%r(%r), %r] already exists in the MIB" %
                                 (self._onu_name, me.me_class, omci_me_class.value(me.me_class), me.inst))
                    return False
                per_inst_dict[me.inst] = me
            if me.user_name is not None:
                self._by_name[me.user_name] = me

        return True

    def set(self, me: ME, log_error: bool = True) -> bool:
        """Update an existing ME in the database.

           The values in me stored in the MIB are merged with values passed in parameters

        Args:
            me: ME object
            log_error: log if doesn't exist in the MIB
        Returns:
            True if successful, False if [me_class, me_inst] doesn't exists in the MIB
        """
        with self._lock:
            if me.me_class not in self._per_class_dict or me.inst not in self._per_class_dict[me.me_class]:
                if log_error:
                    logger.error("OnuMib.Set %r: ME[%r(%r), %r] doesn't exists in the MIB" %
                             (self._onu_name, me.me_class, omci_me_class.value(me.me_class), me.inst))
                return None                
            per_inst_dict = self._per_class_dict[me.me_class]
            old_me = per_inst_dict[me.inst]
            if old_me.user_name is not None and old_me.user_name in self._by_name:
                del self._by_name[old_me.user_name]
            old_me.merge(me)
            me = old_me
            per_inst_dict[me.inst] = me
            if me.user_name is not None:
                self._by_name[me.user_name] = me
        return True

    def delete(self, me_class: int, inst: int) -> bool:
        """Delete ME from the database

        Args:
            me_class: ME object class
            inst: ME object instance
        Returns:
            True if successful, False if [me_class, me_inst] doesn't exist in the MIB
        """
        with self._lock:
            if me_class not in self._per_class_dict:
                logger.error("OnuMib.Delete %r: ME class %r(%r) doesn't exist in the MIB" %
                             (self._onu_name, me_class, omci_me_class.value(me_class)))
                return False
            # Some instances for the class already exist
            per_inst_dict = self._per_class_dict[me_class]
            if inst not in per_inst_dict:
                logger.error("OnuMib.Delete %r: ME[%r(%r), %d] doesn't exist in the MIB" %
                             (self._onu_name, me_class, omci_me_class.value(me_class), inst))
                return False
            me = per_inst_dict[inst]
            del per_inst_dict[inst]
            if len(per_inst_dict) == 0:
                del self._per_class_dict[me_class]
            if me.user_name is not None and me.user_name in self._by_name:
                del self._by_name[me.user_name]
        return True

    def get(self, me_class: int, inst: int, log_error: bool = True, clone: bool = False) -> ME:
        """Get ME from the database

        Args:
            me_class: ME object class
            inst: ME object instance
            clone: True-return a deep copy of the ME stored in the MIB,
                   False-return the original ME
        Returns:
            ME if successful, None if [me_class, me_inst] doesn't exist in the MIB
        """
        with self._lock:
            if me_class not in self._per_class_dict:
                if log_error:
                    logger.warning("OnuMib.Get %r: ME class %r(%r) doesn't exist in the MIB" %
                                 (self._onu_name, me_class, omci_me_class.value(me_class)))
                return None
            # Some instances for the class already exist
            per_inst_dict = self._per_class_dict[me_class]
            if inst not in per_inst_dict:
                if log_error:
                    logger.warning("OnuMib.Get %r: ME[%r(%r), %r] doesn't exist in the MIB" %
                                 (self._onu_name, me_class, omci_me_class.value(me_class), inst))
                return None
            me = per_inst_dict[inst]
            return clone and copy.deepcopy(me) or me

    def get_by_name(self, name: str, clone: bool = False) -> ME:
        """ Get ME by name

        Args:
            name: name associated with an ME using me.user_name
            clone: True-return a deep copy of the ME stored in the MIB,
                   False-return the original ME
        Returns:
            ME instance or None if not found
        """
        if name not in self._by_name:
            return None
        me = self._by_name[name]
        return clone and copy.deepcopy(me) or me

    def get_first(self, me_class: int) -> ME:
        """Get first ME with specific ME class

        Args:
            me_class: ME object class
        Returns:
            ME if successful, None if there are no instances of me_class
        """
        with self._lock:
            if me_class not in self._per_class_dict:
                return None
            # Some instances for the class already exist
            return list(OrderedDict(self._per_class_dict[me_class]).values())[0]

    def get_all_instance_ids(self, me_class: int) -> Tuple[int, ...]:
        """Get tuple including all instance ids of the specified me_class

        Args:
            me_class: ME object class
        Returns:
            tuple of all instance ids of the specified me_class
        """
        if me_class not in self._per_class_dict:
            return tuple()
        return tuple(self._per_class_dict[me_class].keys())

    def get_all_instances(self, me_class: int) -> Tuple[ME, ...]:
        """Get tuple including all MEs of the specified ma_class
        Args:
            me_class: ME object class
        Returns:
            tuple of all MEs of the specified me_class
        """
        if me_class not in self._per_class_dict:
            return tuple()

        return tuple(self._per_class_dict[me_class].values())

    def get_all_me_classes(self) -> Tuple[int,...]:
        """Get tuple including all ME classes

           Returns:
               tuple of all ME classes
        """
        return tuple(self._per_class_dict.keys())

    def clear(self):
        """Clear ONU MIB"""
        with self._lock:
            self._per_class_dict = {}
            self._by_name = {}

    def _merge_me_class(self, cl):
        for cand_me in cl.values():
            old_me = self.get(cand_me.me_class, cand_me.inst, log_error=False)
            if old_me is not None:
                self.set(cand_me)
            else:
                self.add(cand_me)

    def merge(self, candidate: 'OnuMib', me_class: int):
        """ Merge values from candidate into this MIB """
        if me_class is None:
            for cl in candidate._per_class_dict.values():
                self._merge_me_class(cl)
        else:
            if me_class in candidate._per_class_dict:
                self._merge_me_class(candidate._per_class_dict[me_class])
