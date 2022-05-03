""" Set up ANI port handler.

 This handler is triggered by creation of YANG object representing ONU ANI.

"""

from omh_nbi.omh_handler import OmhHandler, OMHStatus
from omh_nbi.onu_driver import OnuDriver
from database.omci_me import ME
from .omh_handler_utils import get_ani
from database.omci_me_types import *
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)



class AniSetHandler(OmhHandler):
    def __init__(self, onu: 'OnuDriver', ani_name: str, ani_id: int, hd_name: str):
        """ Set ANI port.

        Args:
            ani_name : ANI interface name in the YANG model
            ani_id: 0-based ANI index ???. Usually it is determined by parent-rel-pos attribute in the
                    parent hardware component. Note that unlike parent-rel-pos, ani_id is 0-based.
                    The corresponding ME of type 'ANI_G' - 263 must exist in the ONU MIB.
        
        Returns:
            handler completion status
        """
        super().__init__(name='set_ani', onu = onu, description='set_ani: {}.{}-{}-{}'.format(onu.onu_id, ani_id, ani_name,hd_name))
        self._ani_name = ani_name
        self._ani_id = ani_id
        self._hd_name = hd_name

    def run_to_completion(self) -> OMHStatus:
        
        logger.info(self.info())

        # Do nothing if ANI is already in the local MIB
        if self._onu.get_by_name(self._ani_name) is not None:
             logger.info('{} - Already configured'.format(self.info()))
             return OMHStatus.OK

        #
        # At this point ONU MIB is freshly populated. Start the initial provisioning
        #
    
        ani_me = get_ani(self._onu, self._ani_id)
        if ani_me is None:
            return self.logerr_and_return(OMHStatus.ERROR_IN_PARAMETERS,
                                          'ANI {} is not found'.format(self._ani_id))


    
        ani_me.user_name = self._ani_name
        ani_me.hd_name = self._hd_name
        self._onu.set(ani_me)

        return OMHStatus.OK
