from omci_types import RawMessage
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

class NotificationHandler():
    # def __init__(self, name: str, onu: 'OnuDriver', description: str = None):
    #     super().__init__(name, onu, description)

    def recv(self, msg: RawMessage):
        logger.error("Notification handler not implemented")

    def decode(self, msg: RawMessage):
        logger.error("Error decode")