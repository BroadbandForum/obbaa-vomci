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
# QoS policy profile handler
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

""" Create a QoS policy profile.

This handler is triggered by creation a UNI or VLAN sub-interface
containing ingress-qos-policy-profile attribute.

It creates Create a IEEE 802.1p mapper service profile ME and
GEM Interworking TP MEs for every GEM port associated with the
interface.
"""
from database.omci_me_types import *
from omh_nbi.omh_handler import OmhHandler, OMHStatus
from .omh_handler_utils import create_8021p_svc_mapper, set_8021p_mapper
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

class QosPolicyProfile:
    """ QoS Policy profile """

    def __init__(self, name: str):
        self._name = name
        self._pbit_to_tc_map = [None] * 8

    @property
    def name(self):
        return self._name

    def tc(self, pbit: int) -> Union[int, None]:
        """ Get a Traffic Class (TC) value for a pbit
        Args: pbit
        Returns: tc. Can be an integer [0..7] or None
        """
        assert 0 <= pbit <= 7
        return self._pbit_to_tc_map[pbit]

    def tc_set(self, pbit: int, tc: int):
        """ Set Traffic Class (TC) value for a pbit
        Args:
            pbit: 0..7
            tc: 0..7
        """
        assert 0 <= pbit <= 7
        assert 0 <= tc <= 7
        self._pbit_to_tc_map[pbit] = tc

    def pbits_by_tc(self, tc: int) -> Tuple[int, ...]:
        """ Get all PBITS that map to the specified TC """
        pbits = []
        for pbit in range(len(self._pbit_to_tc_map)):
            if tc == self._pbit_to_tc_map[pbit]:
                pbits.append(pbit)
        return tuple(pbits)


class QosPolicyProfileSetHandler(OmhHandler):
    """ Create/Update a IEEE 802.1p mapper service profile and
        0..8 GEM Port Interworking TP MEs, depending on the number
        of pre-provisioned GEM ports
    """

    def __init__(self, onu: 'OnuDriver', profile: QosPolicyProfile, iface_name: str):
        """ Create a QoS policy profile.
        This handler creates a IEEE 802.1p mapper service profile referring to GEM port IW TP entries
        per traffic class.

        Args:
            onu: ONU driver
            profile: QoS policy profile
            iface_name: a UNI or a VLAN sub-interface name
        Returns:
            handler completion status
        """
        super().__init__(name='qos_profile_create', onu=onu,
                         description=' Configure QoS Policy Profile {}'.format(profile._name))
        self._profile = profile
        self._iface_name = iface_name

    def run_to_completion(self) -> OMHStatus:
        logger.info(self.info())

        iface_me = self._onu.get_by_name(self._iface_name, clone=True)
        if iface_me is None:
            return self.logerr_and_return(OMHStatus.ERROR_IN_PARAMETERS,
                                          'UNI or VLAN sub-interface {} is not found'.format(self._iface_name))

        # Check if profile doesn't exist yet. Create if not
        profile_me = self._onu.get_by_name(self._profile.name)
        if profile_me is None:
            status = create_8021p_svc_mapper(self, self._profile.name)
            if status != OMHStatus.OK:
                return status
            profile_me = self.last_action.me

        iface_me.set_user_attr('qos_profile_name', self._profile.name)

        # Now go over GEM ports associated with the interface, create GEM Port IW TP if necessary
        # and associate with the profile

        # First find a UNI if interface associated with the profile is vlan subif
        uni_me = iface_me
        uni_name = uni_me.user_attr('lower')
        while uni_name is not None:
            uni_me = self._onu.get_by_name(uni_name)
            if uni_me is None:
                return self.logerr_and_return(OMHStatus.INTERNAL_ERROR,
                                              'Interface {} is not found'.format(uni_name))
            uni_name = uni_me.user_attr('lower')
        uni_name = uni_me.user_name
        if uni_name is None:
            return self.logerr_and_return(
                OMHStatus.INTERNAL_ERROR,
                " {} - UNI under {} doesn't have a name".format(self._profile.name, self._iface_name))

        # Now go over all GEM ports associated with the UNI and setup the mapper
        return set_8021p_mapper(self, profile_me, self._profile, uni_name)
