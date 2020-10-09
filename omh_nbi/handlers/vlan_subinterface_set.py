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
# VLAN sub-interface handler
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

""" Create a VLAN Sub-Interface.

This handler is triggered by creation a vlan-subif at ONU UNI.

It performs the following sequence:
    - Trigger QoS policy profile sequence if ingress-qos-policy-profile is set
    - Create Bridge Port Configuration Data ME
    - Create and configure VLAN Tagging Filter ME
    - Add entry in Extended VLAN Tagging Operation ME

Once this sequence is provisioned, it will be possible to pass data between ONU UNI and ANI
based on the specified VLAN classification and modification rules.
"""
from typing import Optional
from .omh_types import PacketClassifier, PacketAction
from .omh_handler_utils import create_8021p_svc_mapper, create_mac_bridge_port, create_vlan_tagging_filter_data, set_ext_vlan_tag_op
from omh_nbi.omh_handler import OmhHandler, OMHStatus
from .qos_policy_profile_set import QosPolicyProfile, QosPolicyProfileSetHandler
from database.omci_me_types import omci_me_class
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

class VlanSubInterfaceSetHandler(OmhHandler):
    """ Create/Update a VLAN Sub-Interface """

    def __init__(self, onu: 'OnuDriver', iface_name: str, lower_name: str,
                 classifier: PacketClassifier, packet_action: Optional[PacketAction] = None,
                 qos_profile: Optional[QosPolicyProfile] = None):
        """ Create a VLAN Sub-Interface.

        Args:
            onu: ONU driver
            iface_name: a unique sub-interface name name
            lower_name: a 'lower' interface name. The interface must exist
            classifier: packet classifier
            packet_action: optional packet action
            qos_profile: optional QoS policy profile
        Returns:
            handler completion status
        """
        super().__init__(name='vlan_subinterface', onu=onu,
                         description=' Configure VLAN Sub Interface {}'.format(iface_name))
        self._iface_name = iface_name
        self._lower_name = lower_name
        self._classifier = classifier
        self._packet_action = packet_action
        self._qos_profile = qos_profile

    def run_to_completion(self) -> OMHStatus:
        logger.info(self.info())

        lower_me = self._onu.get_by_name(self._lower_name)
        if lower_me is None:
            return self.logerr_and_return(OMHStatus.ERROR_IN_PARAMETERS,
                                          'lower interface {} is not found'.format(self._lower_name))

        vlan_tag_me = self._onu.get_by_name(self._iface_name)
        if vlan_tag_me is not None:
            return self.logerr_and_return(OMHStatus.ERROR_IN_PARAMETERS,
                                          'interface {} already exists'.format(self._iface_name))

        # Find or create QoS Policy profile
        if self._qos_profile is None:
            qos_profile_name = lower_me.user_attr('qos_profile_name')
            if qos_profile_name is None:
                return self.logerr_and_return(OMHStatus.ERROR_IN_PARAMETERS,
                    "ingress-qos-policy-profile must be set on the sub-interface or it's lower UNI")

                qos_profile_me = self._onu.get_by_name(qos_profile_name)
                if qos_profile_me is None:
                    return self.logerr_and_return(OMHStatus.INTERNAL_ERROR,
                        "qos-policy-profile {} is not found".format(qos_profile_name))

        else:
            # Create 802.1p mapper first, finish creating QoS service profile a bit later
            status = create_8021p_svc_mapper(self, self._qos_profile.name)
            if status != OMHStatus.OK:
                return status
            qos_profile_me = self.last_action.me

        # Create Bridge port config data ME
        status = create_mac_bridge_port(self, qos_profile_me)
        if status != OMHStatus.OK:
            return status
        mac_bridge_port_me = self.last_action.me

        # Packet action can include different stuff. Only 'vlan' action is supported for now
        vlan_action = self._packet_action and self._packet_action.action('vlan') or None

        # Create VLAN Tagging Filter
        status = create_vlan_tagging_filter_data(self, mac_bridge_port_me.inst,
                                                 self._iface_name, self._classifier, vlan_action)
        if status != OMHStatus.OK:
            return status
        vlan_tag_me = self.last_action.me
        vlan_tag_me.set_user_attr('lower', self._lower_name)

        # Now finish creating QoS policy profile
        if self._qos_profile is not None:
            status = self.run_subsidiary(QosPolicyProfileSetHandler(self._onu, self._qos_profile, self._iface_name))
            if status != OMHStatus.OK:
                return status

        # Now create extended VLAN tagging operation entry.
        # EXT VLAN Tagging Oper ME is created per UNI at ONU activation time
        if vlan_action is not None:
            ext_vlan_tag_inst = lower_me.user_attr('ext_vlan_tag_op')
            if ext_vlan_tag_inst is None:
                return self.logerr_and_return(OMHStatus.INTERNAL_ERROR,
                                              "Can't find ext_vlan_tag_op user attribute for interface {}".format(lower_name))
            ext_val_tag_me = self._onu.get(omci_me_class['EXT_VLAN_TAG_OPER_CONFIG_DATA'], ext_vlan_tag_inst, clone=True)
            if ext_val_tag_me is None:
                return self.logerr_and_return(OMHStatus.INTERNAL_ERROR,
                                              "Can't find ext_vlan_tag_op[{}]".format(ext_vlan_tag_inst))
            status = set_ext_vlan_tag_op(self, ext_val_tag_me, self._classifier, vlan_action)
            if status != OMHStatus.OK:
                return status

        return OMHStatus.OK
