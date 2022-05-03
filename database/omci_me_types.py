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
# omci_me_types.py : OMCI ME classes.
#
# This file is auto-generated, please don't edit.
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

#
# OMCI types and classes
#

from omci_types import *
from database.omci_me import *

""" OMCI message type """
omci_msg_type = EnumDatum(1,
   (('CREATE', 4),
    ('DELETE', 6),
    ('SET', 8),
    ('GET', 9),
    ('GET_ALL_ALARMS', 11),
    ('GET_ALL_ALARMS_NEXT', 12),
    ('MIB_UPLOAD', 13),
    ('MIB_UPLOAD_NEXT', 14),
    ('MIB_RESET', 15),
    ('ALARM', 16),
    ('AVC', 17),
    ('TEST', 18),
    ('START_SW_DOWNLOAD', 19),
    ('DOWNLOAD_SECTION', 20),
    ('END_SW_DOWNLOAD', 21),
    ('ACTIVATE_SW', 22),
    ('COMMIT_SW', 23),
    ('SYNC_TIME', 24),
    ('REBOOT', 25),
    ('GET_NEXT', 26),
    ('TEST_RESULT', 27),
    ('GET_CURRENT_DATA', 28),
    ('SET_TABLE', 29)))

""" OMCI Message Set type (device identifier) """
omci_msg_set_type = EnumDatum(1,
  (('BASELINE', 0xA),
   ('EXTENDED', 0xB)))

""" OMCI Message status """
omci_status = EnumDatum(1,
  (('OK', 0),
   ('COMMAND_PROCESSING_ERROR', 1),
   ('COMMAND_NOT_SUPPORTED', 2),
   ('PARAMETER_ERROR', 3),
   ('UNKNOWN_MANAGED_ENTITY', 4),
   ('UNKNOWN_MANAGED_ENTITY_INSTANCE', 5),
   ('DEVICE_BUSY', 6),
   ('INSTANCE_EXISTS', 7),
   ('ATTRIBUTES_FAILED_OR_UNKNOWN', 9)))

""" OMCI NULL pointer """
OMCI_NULL_PTR = 0xffff

""" All ME class Ids """
omci_me_class = EnumDatum(
    1,
    (
        ('GAL_ETH_PROF', 272),
        ('GEM_IW_TP', 266),
        ('GEM_PORT_NET_CTP', 268),
        ('IEEE_8021_P_MAPPER_SVC_PROF', 130),
        ('MAC_BRIDGE_PORT_CONFIG_DATA', 47),
        ('MAC_BRIDGE_SVC_PROF', 45),
        ('VLAN_TAG_FILTER_DATA', 84),
        ('TCONT', 262),
        ('EXT_VLAN_TAG_OPER_CONFIG_DATA', 171),
        ('PRIORITY_QUEUE_G', 277),
        ('MCAST_GEM_IW_TP', 281),
        ('MCAST_OPERATIONS_PROFILE', 309),
        ('MCAST_SUBSCRIBER_CONFIG_INFO', 310),
        ('PPTP_ETH_UNI', 11),
        ('VIRTUAL_ETH_INTF_POINT', 329),
        ('ONU_DATA', 2),
        ('ONU_G', 256),
        ('ONU2_G', 257),
        ('SW_IMAGE', 7),
        ('ANI_G', 263),
        ('GEM_PORT_NET_CTP_PM', 341),
        ('ETH_FRAME_UPSTREAM_PM', 322),
        ('ETH_FRAME_DOWNSTREAM_PM', 321),
        ('FEC_PM', 312),
        ('XGPON_TC_PM', 344),
        ('IP_HOST_CONFIG_DATA', 134),
        ('VOIP_LINE_STATUS', 141),
        ('VOIP_MEDIA_PROFILE', 142),
        ('SIP_USER_DATA', 153),
        ('SIP_AGENT_CONFIG_DATA', 150),
        ('NETWORK_ADDRESS', 137),
        ('LARGE_STRING', 157),
        ('AUTHENTICATION_SECURITY_METHOD', 148),
        ('VOICE_SERVICE_PROFILE', 58),
        ('VOIP_CONFIG_DATA', 138),
        ('VOIP_VOICE_CTP', 139),
        ('TCP_UDP_CONFIG_DATA', 136),
        ('NETWORK_DIAL_PLAN_TABLE', 145),
        ('RTP_PROFILE_DATA', 143),
        ('POTS_UNI', 53),
        ('CIRCUIT_PACK', 6),
        ('ENHANCED_SECURITY_CONTROL', 332),
    ))


#################
# gal_eth_prof: GAL Ethernet Profile
#################



class gal_eth_prof_me(ME):
    """ GAL_ETH_PROF (272) - GAL Ethernet Profile. """
    me_class = 272
    name = 'GAL_ETH_PROF'
    description = 'GAL Ethernet Profile'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'max_gem_payload_size', 'Max GEM payload Size', 'RWC', 'M', NumberDatum(2)),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            max_gem_payload_size = None
        ):
        """ GAL_ETH_PROF ME Constructor.

        Args:
            inst : ME instance.
            max_gem_payload_size : Attribute #1. Max GEM payload Size.
        """
        super(gal_eth_prof_me, self).__init__(inst)
        if max_gem_payload_size is not None:
            self.set_attr_value(1, max_gem_payload_size)


#################
# gem_iw_tp: GEM Interworking Termination Point
#################

gem_iw_tp_iw_opt = EnumDatum(
    1,
    (
        ('CIRCUIT_EMULATED_TDM', 0x0),
        ('MAC_BRIDGED_LAN', 0x1),
        ('RESERVED_2', 0x2),
        ('RESERVED_3', 0x3),
        ('VIDEO_RETURN_PATH', 0x4),
        ('IEEE_8021_P_MAPPER', 0x5),
        ('DS_BROADCAST', 0x6),
        ('MPLS_TW_TDM_SVC', 0x7),
    )
)

gem_iw_tp_oper_state = EnumDatum(
    1,
    (
        ('ENABLED', 0x0),
        ('DISABLED', 0x1),
    )
)

gem_iw_tp_gal_lpbk_config = EnumDatum(
    1,
    (
        ('NO_LOOPBACK', 0x0),
        ('LOOPBACK_DS', 0x1),
    )
)



class gem_iw_tp_me(ME):
    """ GEM_IW_TP (266) - GEM Interworking Termination Point. """
    me_class = 266
    name = 'GEM_IW_TP'
    description = 'GEM Interworking Termination Point'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'gem_port_net_ctp_conn_ptr', 'GEM port network CTP connectivity pointer', 'RWC', 'M', NumberDatum(2)),
        Attr(2, 'iw_opt', 'Interworking option', 'RWC', 'M', gem_iw_tp_iw_opt),
        Attr(3, 'svc_prof_ptr', 'Service profile pointer', 'RWC', 'M', NumberDatum(2)),
        Attr(4, 'iw_tp_ptr', 'Interworking termination point pointer', 'RWC', 'M', NumberDatum(2)),
        Attr(5, 'pptp_count', 'PPTP Counter', 'R', 'O', NumberDatum(1)),
        Attr(6, 'oper_state', 'Operational State', 'R', 'O', gem_iw_tp_oper_state),
        Attr(7, 'gal_prof_ptr', 'GAL Profile Pointer', 'RWC', 'M', NumberDatum(2)),
        Attr(8, 'gal_lpbk_config', 'GAL Loopback Config', 'RW', 'M', gem_iw_tp_gal_lpbk_config),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            gem_port_net_ctp_conn_ptr = None,
            iw_opt = None,
            svc_prof_ptr = None,
            iw_tp_ptr = None,
            gal_prof_ptr = None,
            gal_lpbk_config = None
        ):
        """ GEM_IW_TP ME Constructor.

        Args:
            inst : ME instance.
            gem_port_net_ctp_conn_ptr : Attribute #1. GEM port network CTP connectivity pointer.
            iw_opt : Attribute #2. Interworking option.
            svc_prof_ptr : Attribute #3. Service profile pointer.
            iw_tp_ptr : Attribute #4. Interworking termination point pointer.
            gal_prof_ptr : Attribute #7. GAL Profile Pointer.
            gal_lpbk_config : Attribute #8. GAL Loopback Config.
        """
        super(gem_iw_tp_me, self).__init__(inst)
        if gem_port_net_ctp_conn_ptr is not None:
            self.set_attr_value(1, gem_port_net_ctp_conn_ptr)
        if iw_opt is not None:
            self.set_attr_value(2, iw_opt)
        if svc_prof_ptr is not None:
            self.set_attr_value(3, svc_prof_ptr)
        if iw_tp_ptr is not None:
            self.set_attr_value(4, iw_tp_ptr)
        if gal_prof_ptr is not None:
            self.set_attr_value(7, gal_prof_ptr)
        if gal_lpbk_config is not None:
            self.set_attr_value(8, gal_lpbk_config)


#################
# gem_port_net_ctp: GEM Port Network CTP
#################

gem_port_net_ctp_direction = EnumDatum(
    1,
    (
        ('UNI_TO_ANI', 0x1),
        ('ANI_TO_UNI', 0x2),
        ('BIDIRECTIONAL', 0x3),
    )
)

gem_port_net_ctp_encryption_key_ring = EnumDatum(
    1,
    (
        ('NO_ENCRYPTION', 0x0),
        ('UNICAST_ENCRYPTION_BOTH_DIR', 0x1),
        ('BROADCAST_ENCRYPTION', 0x2),
        ('UNICAST_ENCRYPTION_DS', 0x3),
    )
)



class gem_port_net_ctp_me(ME):
    """ GEM_PORT_NET_CTP (268) - GEM Port Network CTP. """
    me_class = 268
    name = 'GEM_PORT_NET_CTP'
    description = 'GEM Port Network CTP'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'port_id', 'Port ID', 'RWC', 'M', NumberDatum(2)),
        Attr(2, 'tcont_ptr', 'TCONT Pointer', 'RWC', 'M', NumberDatum(2)),
        Attr(3, 'direction', 'Direction', 'RWC', 'M', gem_port_net_ctp_direction),
        Attr(4, 'traffic_mgmt_ptr_us', 'Traffic Management Pointer for US', 'RWC', 'M', NumberDatum(2)),
        Attr(5, 'traffic_desc_prof_ptr_us', 'Traffic Descriptor Profile Pointer for US', 'RWC', 'O', NumberDatum(2)),
        Attr(6, 'uni_count', 'Uni counter', 'R', 'O', NumberDatum(1)),
        Attr(7, 'pri_queue_ptr_ds', 'Priority Queue Pointer for downstream', 'RWC', 'M', NumberDatum(2)),
        Attr(8, 'encryption_state', 'Encryption State', 'R', 'O', NumberDatum(1)),
        Attr(9, 'traffic_desc_prof_ptr_ds', 'Traffic Descriptor profile pointer for DS', 'RWC', 'O', NumberDatum(2)),
        Attr(10, 'encryption_key_ring', 'Encryption Key Ring', 'RWC', 'O', gem_port_net_ctp_encryption_key_ring),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            port_id = None,
            tcont_ptr = None,
            direction = None,
            traffic_mgmt_ptr_us = None,
            traffic_desc_prof_ptr_us = None,
            pri_queue_ptr_ds = None,
            traffic_desc_prof_ptr_ds = None,
            encryption_key_ring = None
        ):
        """ GEM_PORT_NET_CTP ME Constructor.

        Args:
            inst : ME instance.
            port_id : Attribute #1. Port ID.
            tcont_ptr : Attribute #2. TCONT Pointer.
            direction : Attribute #3. Direction.
            traffic_mgmt_ptr_us : Attribute #4. Traffic Management Pointer for US.
            traffic_desc_prof_ptr_us : Attribute #5. Traffic Descriptor Profile Pointer for US.
            pri_queue_ptr_ds : Attribute #7. Priority Queue Pointer for downstream.
            traffic_desc_prof_ptr_ds : Attribute #9. Traffic Descriptor profile pointer for DS.
            encryption_key_ring : Attribute #10. Encryption Key Ring.
        """
        super(gem_port_net_ctp_me, self).__init__(inst)
        if port_id is not None:
            self.set_attr_value(1, port_id)
        if tcont_ptr is not None:
            self.set_attr_value(2, tcont_ptr)
        if direction is not None:
            self.set_attr_value(3, direction)
        if traffic_mgmt_ptr_us is not None:
            self.set_attr_value(4, traffic_mgmt_ptr_us)
        if traffic_desc_prof_ptr_us is not None:
            self.set_attr_value(5, traffic_desc_prof_ptr_us)
        if pri_queue_ptr_ds is not None:
            self.set_attr_value(7, pri_queue_ptr_ds)
        if traffic_desc_prof_ptr_ds is not None:
            self.set_attr_value(9, traffic_desc_prof_ptr_ds)
        if encryption_key_ring is not None:
            self.set_attr_value(10, encryption_key_ring)


#################
# ieee_8021_p_mapper_svc_prof: IEEE 802.1p mapper service profile
#################

ieee_8021_p_mapper_svc_prof_unmarked_frame_opt = EnumDatum(
    1,
    (
        ('DERIVE_IMPLIED_PCP', 0x0),
        ('SET_IMPLIED_PCP', 0x1),
    )
)

ieee_8021_p_mapper_svc_prof_mapper_tp_type = EnumDatum(
    1,
    (
        ('BRIDGING_MAPPING', 0x0),
        ('PPTP_ETH_UNI', 0x1),
        ('IP_HOST_CONFIG_DATA', 0x2),
        ('ETH_FLOW_TP', 0x3),
        ('PPTP_XDSL_UNI', 0x4),
        ('RESERVED', 0x5),
        ('PPTP_MOCA_UNI', 0x6),
        ('VIRTUAL_ETH_INTERFACE_POINT', 0x7),
        ('INTERWORKING_VCC_TP', 0x8),
    )
)



class ieee_8021_p_mapper_svc_prof_me(ME):
    """ IEEE_8021_P_MAPPER_SVC_PROF (130) - IEEE 802.1p mapper service profile. """
    me_class = 130
    name = 'IEEE_8021_P_MAPPER_SVC_PROF'
    description = 'IEEE 802.1p mapper service profile'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'tp_ptr', 'TP pointer', 'RWC', 'M', NumberDatum(2)),
        Attr(2, 'interwork_tp_ptr_pri_0', 'Interwork TP pointer for P-bit priority 0:', 'RWC', 'M', NumberDatum(2)),
        Attr(3, 'interwork_tp_ptr_pri_1', 'Interwork TP pointer for P-bit priority 1', 'RWC', 'M', NumberDatum(2)),
        Attr(4, 'interwork_tp_ptr_pri_2', 'Interwork TP pointer for P-bit priority 2', 'RWC', 'M', NumberDatum(2)),
        Attr(5, 'interwork_tp_ptr_pri_3', 'Interwork TP pointer for P-bit priority 3', 'RWC', 'M', NumberDatum(2)),
        Attr(6, 'interwork_tp_ptr_pri_4', 'Interwork TP pointer for P-bit priority 4', 'RWC', 'M', NumberDatum(2)),
        Attr(7, 'interwork_tp_ptr_pri_5', 'Interwork TP pointer for P-bit priority 5', 'RWC', 'M', NumberDatum(2)),
        Attr(8, 'interwork_tp_ptr_pri_6', 'Interwork TP pointer for P-bit priority 6', 'RWC', 'M', NumberDatum(2)),
        Attr(9, 'interwork_tp_ptr_pri_7', 'Interwork TP pointer for P-bit priority 7', 'RWC', 'M', NumberDatum(2)),
        Attr(10, 'unmarked_frame_opt', 'Unmarked Frame option', 'RWC', 'M', ieee_8021_p_mapper_svc_prof_unmarked_frame_opt),
        Attr(11, 'dscp_to_pbit_mapping', 'DSCP to P-bit mapping', 'RW', 'M', BytesDatum(24)),
        Attr(12, 'default_pbit_assumption', 'Default P-bit assumption', 'RWC', 'M', NumberDatum(1)),
        Attr(13, 'mapper_tp_type', 'TP Type', 'RWC', 'O', ieee_8021_p_mapper_svc_prof_mapper_tp_type),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            tp_ptr = None,
            interwork_tp_ptr_pri_0 = None,
            interwork_tp_ptr_pri_1 = None,
            interwork_tp_ptr_pri_2 = None,
            interwork_tp_ptr_pri_3 = None,
            interwork_tp_ptr_pri_4 = None,
            interwork_tp_ptr_pri_5 = None,
            interwork_tp_ptr_pri_6 = None,
            interwork_tp_ptr_pri_7 = None,
            unmarked_frame_opt = None,
            dscp_to_pbit_mapping = None,
            default_pbit_assumption = None,
            mapper_tp_type = None
        ):
        """ IEEE_8021_P_MAPPER_SVC_PROF ME Constructor.

        Args:
            inst : ME instance.
            tp_ptr : Attribute #1. TP pointer.
            interwork_tp_ptr_pri_0 : Attribute #2. Interwork TP pointer for P-bit priority 0:.
            interwork_tp_ptr_pri_1 : Attribute #3. Interwork TP pointer for P-bit priority 1.
            interwork_tp_ptr_pri_2 : Attribute #4. Interwork TP pointer for P-bit priority 2.
            interwork_tp_ptr_pri_3 : Attribute #5. Interwork TP pointer for P-bit priority 3.
            interwork_tp_ptr_pri_4 : Attribute #6. Interwork TP pointer for P-bit priority 4.
            interwork_tp_ptr_pri_5 : Attribute #7. Interwork TP pointer for P-bit priority 5.
            interwork_tp_ptr_pri_6 : Attribute #8. Interwork TP pointer for P-bit priority 6.
            interwork_tp_ptr_pri_7 : Attribute #9. Interwork TP pointer for P-bit priority 7.
            unmarked_frame_opt : Attribute #10. Unmarked Frame option.
            dscp_to_pbit_mapping : Attribute #11. DSCP to P-bit mapping.
            default_pbit_assumption : Attribute #12. Default P-bit assumption.
            mapper_tp_type : Attribute #13. TP Type.
        """
        super(ieee_8021_p_mapper_svc_prof_me, self).__init__(inst)
        if tp_ptr is not None:
            self.set_attr_value(1, tp_ptr)
        if interwork_tp_ptr_pri_0 is not None:
            self.set_attr_value(2, interwork_tp_ptr_pri_0)
        if interwork_tp_ptr_pri_1 is not None:
            self.set_attr_value(3, interwork_tp_ptr_pri_1)
        if interwork_tp_ptr_pri_2 is not None:
            self.set_attr_value(4, interwork_tp_ptr_pri_2)
        if interwork_tp_ptr_pri_3 is not None:
            self.set_attr_value(5, interwork_tp_ptr_pri_3)
        if interwork_tp_ptr_pri_4 is not None:
            self.set_attr_value(6, interwork_tp_ptr_pri_4)
        if interwork_tp_ptr_pri_5 is not None:
            self.set_attr_value(7, interwork_tp_ptr_pri_5)
        if interwork_tp_ptr_pri_6 is not None:
            self.set_attr_value(8, interwork_tp_ptr_pri_6)
        if interwork_tp_ptr_pri_7 is not None:
            self.set_attr_value(9, interwork_tp_ptr_pri_7)
        if unmarked_frame_opt is not None:
            self.set_attr_value(10, unmarked_frame_opt)
        if dscp_to_pbit_mapping is not None:
            self.set_attr_value(11, dscp_to_pbit_mapping)
        if default_pbit_assumption is not None:
            self.set_attr_value(12, default_pbit_assumption)
        if mapper_tp_type is not None:
            self.set_attr_value(13, mapper_tp_type)


#################
# mac_bridge_port_config_data: MAC Bridge Port Configuration Data
#################

mac_bridge_port_config_data_tp_type = EnumDatum(
    1,
    (
        ('PHY_PATH_TP_ETH_UNI', 0x1),
        ('INTERWORKING_VCC_TP', 0x2),
        ('IEEE_8021_P_MAPPER_SVC_PROF', 0x3),
        ('IP_HOST_CONFIG_DATA', 0x4),
        ('GEM_INTERWORKING_TP', 0x5),
        ('MULTICAST_GEM_INTERWORKING_TP', 0x6),
        ('PHY_PATH_TP_XDSL_UNI_PART_1', 0x7),
        ('PHY_PATH_TP_VDSL_UNI', 0x8),
        ('ETH_FLOW_TP', 0x9),
        ('RESERVED_TP', 0xa),
        ('VIRTUAL_ETH_INTERFACE_POINT', 0xb),
        ('PHY_PATH_TO_MOCA_UNI', 0xc),
    )
)



class mac_bridge_port_config_data_me(ME):
    """ MAC_BRIDGE_PORT_CONFIG_DATA (47) - MAC Bridge Port Configuration Data. """
    me_class = 47
    name = 'MAC_BRIDGE_PORT_CONFIG_DATA'
    description = 'MAC Bridge Port Configuration Data'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'bridge_id_ptr', 'Bridge Id Pointer', 'RWC', 'M', NumberDatum(2)),
        Attr(2, 'port_num', 'Port num', 'RWC', 'M', NumberDatum(1)),
        Attr(3, 'tp_type', 'TP Type', 'RWC', 'M', mac_bridge_port_config_data_tp_type),
        Attr(4, 'tp_ptr', 'TP Pointer', 'RWC', 'M', NumberDatum(2)),
        Attr(5, 'port_pri', 'Port Priority', 'RWC', 'O', NumberDatum(2)),
        Attr(6, 'port_path_cost', 'Port Path Cost', 'RWC', 'M', NumberDatum(2)),
        Attr(7, 'port_spanning_tree_ind', 'Port Path Cost', 'RWC', 'M', NumberDatum(1)),
        Attr(8, 'deprecated_1', 'Deprecated 1', 'RWC', 'O', NumberDatum(1)),
        Attr(9, 'deprecated_2', 'Deprecated 2', 'RWC', 'O', NumberDatum(1)),
        Attr(10, 'port_mac_addr', 'Port MAC Addr', 'R', 'O', BytesDatum(6)),
        Attr(11, 'outbound_td_ptr', 'Outbound TD Pointer', 'RW', 'O', NumberDatum(2)),
        Attr(12, 'inbound_td_ptr', 'Inbound TD Pointer', 'RW', 'O', NumberDatum(2)),
        Attr(13, 'mac_learning_depth', 'MAC Learning Depth', 'RWC', 'O', NumberDatum(1)),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            bridge_id_ptr = None,
            port_num = None,
            tp_type = None,
            tp_ptr = None,
            port_pri = None,
            port_path_cost = None,
            port_spanning_tree_ind = None,
            deprecated_1 = None,
            deprecated_2 = None,
            outbound_td_ptr = None,
            inbound_td_ptr = None,
            mac_learning_depth = None
        ):
        """ MAC_BRIDGE_PORT_CONFIG_DATA ME Constructor.

        Args:
            inst : ME instance.
            bridge_id_ptr : Attribute #1. Bridge Id Pointer.
            port_num : Attribute #2. Port num.
            tp_type : Attribute #3. TP Type.
            tp_ptr : Attribute #4. TP Pointer.
            port_pri : Attribute #5. Port Priority.
            port_path_cost : Attribute #6. Port Path Cost.
            port_spanning_tree_ind : Attribute #7. Port Path Cost.
            deprecated_1 : Attribute #8. Deprecated 1.
            deprecated_2 : Attribute #9. Deprecated 2.
            outbound_td_ptr : Attribute #11. Outbound TD Pointer.
            inbound_td_ptr : Attribute #12. Inbound TD Pointer.
            mac_learning_depth : Attribute #13. MAC Learning Depth.
        """
        super(mac_bridge_port_config_data_me, self).__init__(inst)
        if bridge_id_ptr is not None:
            self.set_attr_value(1, bridge_id_ptr)
        if port_num is not None:
            self.set_attr_value(2, port_num)
        if tp_type is not None:
            self.set_attr_value(3, tp_type)
        if tp_ptr is not None:
            self.set_attr_value(4, tp_ptr)
        if port_pri is not None:
            self.set_attr_value(5, port_pri)
        if port_path_cost is not None:
            self.set_attr_value(6, port_path_cost)
        if port_spanning_tree_ind is not None:
            self.set_attr_value(7, port_spanning_tree_ind)
        if deprecated_1 is not None:
            self.set_attr_value(8, deprecated_1)
        if deprecated_2 is not None:
            self.set_attr_value(9, deprecated_2)
        if outbound_td_ptr is not None:
            self.set_attr_value(11, outbound_td_ptr)
        if inbound_td_ptr is not None:
            self.set_attr_value(12, inbound_td_ptr)
        if mac_learning_depth is not None:
            self.set_attr_value(13, mac_learning_depth)


#################
# mac_bridge_svc_prof: MAC Bridge Service Profile
#################



class mac_bridge_svc_prof_me(ME):
    """ MAC_BRIDGE_SVC_PROF (45) - MAC Bridge Service Profile. """
    me_class = 45
    name = 'MAC_BRIDGE_SVC_PROF'
    description = 'MAC Bridge Service Profile'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'spanning_tree_ind', 'Spanning Tree Indication (bool)', 'RWC', 'M', NumberDatum(1)),
        Attr(2, 'learning_ind', 'Learning Indication (bool)', 'RWC', 'M', NumberDatum(1)),
        Attr(3, 'port_bridging_ind', 'Port Bridging Indication (bool)', 'RWC', 'M', NumberDatum(1)),
        Attr(4, 'pri', 'Priority', 'RWC', 'M', NumberDatum(2)),
        Attr(5, 'max_age', 'Max Age', 'RWC', 'M', NumberDatum(2)),
        Attr(6, 'hello_time', 'Hello Time', 'RWC', 'M', NumberDatum(2)),
        Attr(7, 'forward_delay', 'Forward Delay', 'RWC', 'M', NumberDatum(2)),
        Attr(8, 'unknown_mac_addr_discard', 'Unknown MAC Address Discard (Bool)', 'RWC', 'M', NumberDatum(1)),
        Attr(9, 'mac_learning_depth', 'MAC Learning Depth', 'RWC', 'O', NumberDatum(1)),
        Attr(10, 'dynamic_filtering_ageing_time', 'Dynamic Filtering Ageing Time', 'RWC', 'O', NumberDatum(4)),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            spanning_tree_ind = None,
            learning_ind = None,
            port_bridging_ind = None,
            pri = None,
            max_age = None,
            hello_time = None,
            forward_delay = None,
            unknown_mac_addr_discard = None,
            mac_learning_depth = None,
            dynamic_filtering_ageing_time = None
        ):
        """ MAC_BRIDGE_SVC_PROF ME Constructor.

        Args:
            inst : ME instance.
            spanning_tree_ind : Attribute #1. Spanning Tree Indication (bool).
            learning_ind : Attribute #2. Learning Indication (bool).
            port_bridging_ind : Attribute #3. Port Bridging Indication (bool).
            pri : Attribute #4. Priority.
            max_age : Attribute #5. Max Age.
            hello_time : Attribute #6. Hello Time.
            forward_delay : Attribute #7. Forward Delay.
            unknown_mac_addr_discard : Attribute #8. Unknown MAC Address Discard (Bool).
            mac_learning_depth : Attribute #9. MAC Learning Depth.
            dynamic_filtering_ageing_time : Attribute #10. Dynamic Filtering Ageing Time.
        """
        super(mac_bridge_svc_prof_me, self).__init__(inst)
        if spanning_tree_ind is not None:
            self.set_attr_value(1, spanning_tree_ind)
        if learning_ind is not None:
            self.set_attr_value(2, learning_ind)
        if port_bridging_ind is not None:
            self.set_attr_value(3, port_bridging_ind)
        if pri is not None:
            self.set_attr_value(4, pri)
        if max_age is not None:
            self.set_attr_value(5, max_age)
        if hello_time is not None:
            self.set_attr_value(6, hello_time)
        if forward_delay is not None:
            self.set_attr_value(7, forward_delay)
        if unknown_mac_addr_discard is not None:
            self.set_attr_value(8, unknown_mac_addr_discard)
        if mac_learning_depth is not None:
            self.set_attr_value(9, mac_learning_depth)
        if dynamic_filtering_ageing_time is not None:
            self.set_attr_value(10, dynamic_filtering_ageing_time)


#################
# vlan_tag_filter_data: VLAN Tagging Filter Data
#################

vlan_tag_filter_data_forward_oper = EnumDatum(
    1,
    (
        ('TAGGED_BRIDGING_A_NO_INVESTIGATION_UNTAGGED_BRIDGING_A', 0x0),
        ('TAGGED_DISCARDING_C_UNTAGGED_BRIDGING_A', 0x1),
        ('TAGGED_BRIDGING_A_NO_INVESTIGATION_UNTAGGED_DISCARDING_C', 0x2),
        ('TAGGED_ACTION_H_VID_INVESTIGATION_UNTAGGED_BRIDGING_A', 0x3),
        ('TAGGED_ACTION_H_VID_INVESTIGATION_UNTAGGED_DISCARDING_C', 0x4),
        ('TAGGED_ACTION_G_VID_INVESTIGATION_UNTAGGED_BRIDGING_A', 0x5),
        ('TAGGED_ACTION_G_VID_INVESTIGATION_UNTAGGED_DISCARDING_C', 0x6),
        ('TAGGED_ACTION_H_PRI_INVESTIGATION_UNTAGGED_BRIDGING_A', 0x7),
        ('TAGGED_ACTION_H_PRI_INVESTIGATION_UNTAGGED_DISCARDING_C', 0x8),
        ('TAGGED_ACTION_G_PRI_INVESTIGATION_UNTAGGED_BRIDGING_A', 0x9),
        ('TAGGED_ACTION_G_PRI_INVESTIGATION_UNTAGGED_DISCARDING_C', 0xa),
        ('TAGGED_ACTION_H_TCI_INVESTIGATION_UNTAGGED_BRIDGING_A', 0xb),
        ('TAGGED_ACTION_H_TCI_INVESTIGATION_UNTAGGED_DISCARDING_C', 0xc),
        ('TAGGED_ACTION_G_TCI_INVESTIGATION_UNTAGGED_BRIDGING_A', 0xd),
        ('TAGGED_ACTION_G_TCI_INVESTIGATION_UNTAGGED_DISCARDING_C', 0xe),
        ('TAGGED_ACTION_H_VID_INVESTIGATION_UNTAGGED_BRIDGING_A_DUP', 0xf),
        ('TAGGED_ACTION_H_VID_INVESTIGATION_UNTAGGED_DISCARDING_C_DUP', 0x10),
        ('TAGGED_ACTION_H_PRI_INVESTIGATION_UNTAGGED_BRIDGING_A_DUP', 0x11),
        ('TAGGED_ACTION_H_PRI_INVESTIGATION_UNTAGGED_DISCARDING_C_DUP', 0x12),
        ('TAGGED_ACTION_H_TCI_INVESTIGATION_UNTAGGED_BRIDGING_A_DUP', 0x13),
        ('TAGGED_ACTION_H_TCI_INVESTIGATION_UNTAGGED_DISCARDING_C_DUP', 0x14),
        ('TAGGED_BRIDGING_A_NO_INVESTIGATION_UNTAGGED_DISCARDING_C_DUP', 0x15),
        ('TAGGED_ACTION_J_VID_INVESTIGATION_UNTAGGED_BRIDGING_A', 0x16),
        ('TAGGED_ACTION_J_VID_INVESTIGATION_UNTAGGED_DISCARDING_C', 0x17),
        ('TAGGED_ACTION_J_PRI_INVESTIGATION_UNTAGGED_BRIDGING_A', 0x18),
        ('TAGGED_ACTION_J_PRI_INVESTIGATION_UNTAGGED_DISCARDING_C', 0x19),
        ('TAGGED_ACTION_J_TCI_INVESTIGATION_UNTAGGED_BRIDGING_A', 0x1a),
        ('TAGGED_ACTION_J_TCI_INVESTIGATION_UNTAGGED_DISCARDING_C', 0x1b),
        ('TAGGED_ACTION_VID_INVESTIGATION_H_UNTAGGED_BRIDGING_A', 0x1c),
        ('TAGGED_ACTION_VID_INVESTIGATION_H_UNTAGGED_DISCARDING_C', 0x1d),
        ('TAGGED_ACTION_PRI_INVESTIGATION_H_UNTAGGED_BRIDGING_A', 0x1e),
        ('TAGGED_ACTION_PRI_INVESTIGATION_H_UNTAGGED_DISCARDING_C', 0x1f),
        ('TAGGED_ACTION_TCI_INVESTIGATION_H_UNTAGGED_BRIDGING_A', 0x20),
        ('TAGGED_ACTION_TCI_INVESTIGATION_H_UNTAGGED_DISCARDING_C', 0x21),
    )
)



class vlan_tag_filter_data_me(ME):
    """ VLAN_TAG_FILTER_DATA (84) - VLAN Tagging Filter Data. """
    me_class = 84
    name = 'VLAN_TAG_FILTER_DATA'
    description = 'VLAN Tagging Filter Data'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'vlan_filter_list', 'VLAN Filter List', 'RWC', 'M', BytesDatum(24)),
        Attr(2, 'forward_oper', 'Forward Operation', 'RWC', 'M', vlan_tag_filter_data_forward_oper),
        Attr(3, 'num_of_entries', 'number of entries', 'RWC', 'M', NumberDatum(1)),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            vlan_filter_list = None,
            forward_oper = None,
            num_of_entries = None
        ):
        """ VLAN_TAG_FILTER_DATA ME Constructor.

        Args:
            inst : ME instance.
            vlan_filter_list : Attribute #1. VLAN Filter List.
            forward_oper : Attribute #2. Forward Operation.
            num_of_entries : Attribute #3. number of entries.
        """
        super(vlan_tag_filter_data_me, self).__init__(inst)
        if vlan_filter_list is not None:
            self.set_attr_value(1, vlan_filter_list)
        if forward_oper is not None:
            self.set_attr_value(2, forward_oper)
        if num_of_entries is not None:
            self.set_attr_value(3, num_of_entries)


#################
# tcont: T-CONT
#################

tcont_policy = EnumDatum(
    1,
    (
        ('NULL', 0x0),
        ('STRICT_PRIORITY', 0x1),
        ('WRR', 0x2),
    )
)



class tcont_me(ME):
    """ TCONT (262) - T-CONT. """
    me_class = 262
    name = 'TCONT'
    description = 'T-CONT'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'alloc_id', 'Alloc-ID', 'RW', 'M', NumberDatum(2)),
        Attr(2, 'deprecated', 'Deprecated', 'RW', 'M', NumberDatum(1)),
        Attr(3, 'policy', 'Policy', 'RW', 'M', tcont_policy),
    )
    num_attrs = len(attrs)
    actions = ('set', 'get')

    def __init__(self,
            inst : int,
            alloc_id = None,
            deprecated = None,
            policy = None
        ):
        """ TCONT ME Constructor.

        Args:
            inst : ME instance.
            alloc_id : Attribute #1. Alloc-ID.
            deprecated : Attribute #2. Deprecated.
            policy : Attribute #3. Policy.
        """
        super(tcont_me, self).__init__(inst)
        if alloc_id is not None:
            self.set_attr_value(1, alloc_id)
        if deprecated is not None:
            self.set_attr_value(2, deprecated)
        if policy is not None:
            self.set_attr_value(3, policy)


#################
# ext_vlan_tag_oper_config_data: Extended VLAN Tagging Operation Configuration Data
#################

ext_vlan_tag_oper_config_data_assoc_type = EnumDatum(
    1,
    (
        ('MAC_BRIDGE_PORT_CFG_DATA', 0x0),
        ('IEEE_8021P_MAPPER_SERVICE_PROFILE', 0x1),
        ('PPTP_ETH_UNI', 0x2),
        ('IP_HOST_CFG_DATA', 0x3),
        ('PPTP_XDSL_UNI', 0x4),
        ('GEM_IWTP', 0x5),
        ('MCAST_GEM_IWTP', 0x6),
        ('PPTP_MOCA_UNI', 0x7),
        ('RESERVED', 0x8),
        ('ETH_FLOW_TP', 0x9),
        ('VEIP', 0xa),
        ('MPLS_PSEUDOWIRE_TP', 0xb),
    )
)

ext_vlan_tag_oper_config_data_ds_mode = EnumDatum(
    1,
    (
        ('US_INVERSE', 0x0),
        ('FORWARD_UNMODIFIED', 0x1),
        ('MATCH_INVERSE_ON_VID_PBIT_DEFAULT_FORWARD', 0x2),
        ('MATCH_INVERSE_ON_VID_DEFAULT_FORWARD', 0x3),
        ('MATCH_INVERSE_ON_PBIT_DEFAULT_FORWARD', 0x4),
        ('MATCH_INVERSE_ON_VID_PBIT_DEFAULT_DISCARD', 0x5),
        ('MATCH_INVERSE_ON_VID_DEFAULT_DISCARD', 0x6),
        ('MATCH_INVERSE_ON_PBIT_DEFAULT_DISCARD', 0x7),
        ('DISCARD_ALL', 0x8),
    )
)



class ext_vlan_tag_oper_config_data_outer_filter_word(BitStructDatum):
    fields = (
        BitField('filter_outer_priority', 'Filter outer priority', width=4),
        BitField('filter_outer_vid', 'Filter outer VID', width=13),
        BitField('filter_outer_tpid', 'Filter outer TPID/DEI', width=3),
        BitField('pad', 'Padding', width=12),
    )
    def __init__(self, default: AttrValue = None, fixed: AttrValue = None, size = 4):
        super().__init__(size, default=default, fixed=fixed)

class ext_vlan_tag_oper_config_data_inner_filter_word(BitStructDatum):
    fields = (
        BitField('filter_inner_priority', 'Filter inner priority', width=4),
        BitField('filter_inner_vid', 'Filter inner VID', width=13),
        BitField('filter_inner_tpid', 'Filter inner TPID/DEI', width=3),
        BitField('pad', 'Padding', width=8),
        BitField('filter_ether_type', 'Filter Ethertype', width=4),
    )
    def __init__(self, default: AttrValue = None, fixed: AttrValue = None, size = 4):
        super().__init__(size, default=default, fixed=fixed)

class ext_vlan_tag_oper_config_data_outer_treatment_word(BitStructDatum):
    fields = (
        BitField('treatment', 'Treatment', width=2),
        BitField('pad', 'Padding', width=10),
        BitField('treatment_outer_priority', 'Treatment outer priority', width=4),
        BitField('treatment_outer_vid', 'Treatment outer VID', width=13),
        BitField('treatment_outer_tpid', 'Treatment outer TPID/DEI', width=3),
    )
    def __init__(self, default: AttrValue = None, fixed: AttrValue = None, size = 4):
        super().__init__(size, default=default, fixed=fixed)

class ext_vlan_tag_oper_config_data_inner_treatment_word(BitStructDatum):
    fields = (
        BitField('pad', 'Padding', width=12),
        BitField('treatment_inner_priority', 'Treatment inner priority', width=4),
        BitField('treatment_inner_vid', 'Treatment inner VID', width=13),
        BitField('treatment_inner_tpid', 'Treatment inner TPID/DEI', width=3),
    )
    def __init__(self, default: AttrValue = None, fixed: AttrValue = None, size = 4):
        super().__init__(size, default=default, fixed=fixed)


class ext_vlan_tag_oper_config_data_rx_frame_vlan_tag_oper_table(StructDatum):
    fields = (
        StructField('outer_filter_word', 'Outer filter word', field_type=ext_vlan_tag_oper_config_data_outer_filter_word()),
        StructField('inner_filter_word', 'Inner filter word', field_type=ext_vlan_tag_oper_config_data_inner_filter_word()),
        StructField('outer_treatment_word', 'Outer treatment word', field_type=ext_vlan_tag_oper_config_data_outer_treatment_word()),
        StructField('inner_treatment_word', 'Inner treatment word', field_type=ext_vlan_tag_oper_config_data_inner_treatment_word()),
    )
    def __init__(self, default: AttrValue = None, fixed: AttrValue = None, size = 16):
        super().__init__(size, default=default, fixed=fixed)

class ext_vlan_tag_oper_config_data_me(ME):
    """ EXT_VLAN_TAG_OPER_CONFIG_DATA (171) - Extended VLAN Tagging Operation Configuration Data. """
    me_class = 171
    name = 'EXT_VLAN_TAG_OPER_CONFIG_DATA'
    description = 'Extended VLAN Tagging Operation Configuration Data'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'assoc_type', 'Association Type', 'RWC', 'M', ext_vlan_tag_oper_config_data_assoc_type),
        Attr(2, 'rx_frame_vlan_tag_oper_table_max_size', 'Rx Frame VLAN Tagging Operation Table Max Size', 'R', 'M', NumberDatum(2)),
        Attr(3, 'input_tpid', 'Input TPID', 'RW', 'M', NumberDatum(2)),
        Attr(4, 'output_tpid', 'Output TPID', 'RW', 'M', NumberDatum(2)),
        Attr(5, 'ds_mode', 'Downstream Mode', 'RW', 'M', ext_vlan_tag_oper_config_data_ds_mode),
        Attr(6, 'rx_frame_vlan_tag_oper_table', 'Downstream Mode', 'RW', 'M', ext_vlan_tag_oper_config_data_rx_frame_vlan_tag_oper_table()),
        Attr(7, 'assoc_me_ptr', 'Associated ME Pointer', 'RWC', 'M', NumberDatum(2)),
        Attr(8, 'dscp_to_pbit_mapping', 'DSCP to P-bit Mapping', 'RW', 'O', BytesDatum(24)),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            assoc_type = None,
            input_tpid = None,
            output_tpid = None,
            ds_mode = None,
            rx_frame_vlan_tag_oper_table = None,
            assoc_me_ptr = None,
            dscp_to_pbit_mapping = None
        ):
        """ EXT_VLAN_TAG_OPER_CONFIG_DATA ME Constructor.

        Args:
            inst : ME instance.
            assoc_type : Attribute #1. Association Type.
            input_tpid : Attribute #3. Input TPID.
            output_tpid : Attribute #4. Output TPID.
            ds_mode : Attribute #5. Downstream Mode.
            rx_frame_vlan_tag_oper_table : Attribute #6. Downstream Mode.
            assoc_me_ptr : Attribute #7. Associated ME Pointer.
            dscp_to_pbit_mapping : Attribute #8. DSCP to P-bit Mapping.
        """
        super(ext_vlan_tag_oper_config_data_me, self).__init__(inst)
        if assoc_type is not None:
            self.set_attr_value(1, assoc_type)
        if input_tpid is not None:
            self.set_attr_value(3, input_tpid)
        if output_tpid is not None:
            self.set_attr_value(4, output_tpid)
        if ds_mode is not None:
            self.set_attr_value(5, ds_mode)
        if rx_frame_vlan_tag_oper_table is not None:
            self.set_attr_value(6, rx_frame_vlan_tag_oper_table)
        if assoc_me_ptr is not None:
            self.set_attr_value(7, assoc_me_ptr)
        if dscp_to_pbit_mapping is not None:
            self.set_attr_value(8, dscp_to_pbit_mapping)


#################
# priority_queue_g: priority queue-G
#################

priority_queue_g_drop_precedence_colour_marking = EnumDatum(
    1,
    (
        ('NO_MARKING', 0x0),
        ('INTERNAL_MARKING', 0x1),
        ('DEI', 0x2),
        ('PCP_8_P_0_D', 0x3),
        ('PCP_7_P_1_D', 0x4),
        ('PCP_6_P_2_D', 0x5),
        ('PCP_5_P_3_D', 0x6),
        ('DSCP_AF_CLASS', 0x7),
    )
)



class priority_queue_g_me(ME):
    """ PRIORITY_QUEUE_G (277) - priority queue-G. """
    me_class = 277
    name = 'PRIORITY_QUEUE_G'
    description = 'priority queue-G'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'queue_config_opt', 'Queue configuration option', 'R', 'M', NumberDatum(1)),
        Attr(2, 'max_queue_size', 'Maximum queue size', 'R', 'M', NumberDatum(2)),
        Attr(3, 'allocated_queue_size', 'Allocated queue size', 'RW', 'M', NumberDatum(2)),
        Attr(4, 'discard_counter_reset_interval', 'Discard-block counter reset interval', 'RW', 'O', NumberDatum(2)),
        Attr(5, 'discard_threshold', 'Threshold value for discarded blocks due to buffer overflow', 'RW', 'O', NumberDatum(2)),
        Attr(6, 'related_port', 'Related port', 'RW', 'M', BytesDatum(4)),
        Attr(7, 'traffic_scheduler_ptr', 'Traffic scheduler pointer', 'RW', 'M', NumberDatum(2)),
        Attr(8, 'weight', 'Weight', 'RW', 'M', NumberDatum(1)),
        Attr(9, 'back_pressure_oper', 'Back pressure operation', 'RW', 'M', NumberDatum(2)),
        Attr(10, 'back_pressure_time', 'Back pressure time', 'RW', 'M', NumberDatum(4)),
        Attr(11, 'back_pressure_occur_queue_thr', 'Back pressure occur queue threshold', 'RW', 'M', NumberDatum(2)),
        Attr(12, 'back_pressure_clear_queue_thr', 'Back pressure clear queue threshold', 'RW', 'M', NumberDatum(2)),
        Attr(13, 'packet_drop_queue_thr', 'Packet drop queue thr', 'RW', 'O', BytesDatum(8)),
        Attr(14, 'packet_drop_max_p', 'Packet drop max_p', 'RW', 'O', NumberDatum(2)),
        Attr(15, 'queue_drop_w_q', 'Queue drop w_q', 'RW', 'O', NumberDatum(1)),
        Attr(16, 'drop_precedence_colour_marking', 'Drop precedence colour marking', 'RW', 'O', priority_queue_g_drop_precedence_colour_marking),
    )
    num_attrs = len(attrs)
    actions = ('set', 'get')

    def __init__(self,
            inst : int,
            allocated_queue_size = None,
            discard_counter_reset_interval = None,
            discard_threshold = None,
            related_port = None,
            traffic_scheduler_ptr = None,
            weight = None,
            back_pressure_oper = None,
            back_pressure_time = None,
            back_pressure_occur_queue_thr = None,
            back_pressure_clear_queue_thr = None,
            packet_drop_queue_thr = None,
            packet_drop_max_p = None,
            queue_drop_w_q = None,
            drop_precedence_colour_marking = None
        ):
        """ PRIORITY_QUEUE_G ME Constructor.

        Args:
            inst : ME instance.
            allocated_queue_size : Attribute #3. Allocated queue size.
            discard_counter_reset_interval : Attribute #4. Discard-block counter reset interval.
            discard_threshold : Attribute #5. Threshold value for discarded blocks due to buffer overflow.
            related_port : Attribute #6. Related port.
            traffic_scheduler_ptr : Attribute #7. Traffic scheduler pointer.
            weight : Attribute #8. Weight.
            back_pressure_oper : Attribute #9. Back pressure operation.
            back_pressure_time : Attribute #10. Back pressure time.
            back_pressure_occur_queue_thr : Attribute #11. Back pressure occur queue threshold.
            back_pressure_clear_queue_thr : Attribute #12. Back pressure clear queue threshold.
            packet_drop_queue_thr : Attribute #13. Packet drop queue thr.
            packet_drop_max_p : Attribute #14. Packet drop max_p.
            queue_drop_w_q : Attribute #15. Queue drop w_q.
            drop_precedence_colour_marking : Attribute #16. Drop precedence colour marking.
        """
        super(priority_queue_g_me, self).__init__(inst)
        if allocated_queue_size is not None:
            self.set_attr_value(3, allocated_queue_size)
        if discard_counter_reset_interval is not None:
            self.set_attr_value(4, discard_counter_reset_interval)
        if discard_threshold is not None:
            self.set_attr_value(5, discard_threshold)
        if related_port is not None:
            self.set_attr_value(6, related_port)
        if traffic_scheduler_ptr is not None:
            self.set_attr_value(7, traffic_scheduler_ptr)
        if weight is not None:
            self.set_attr_value(8, weight)
        if back_pressure_oper is not None:
            self.set_attr_value(9, back_pressure_oper)
        if back_pressure_time is not None:
            self.set_attr_value(10, back_pressure_time)
        if back_pressure_occur_queue_thr is not None:
            self.set_attr_value(11, back_pressure_occur_queue_thr)
        if back_pressure_clear_queue_thr is not None:
            self.set_attr_value(12, back_pressure_clear_queue_thr)
        if packet_drop_queue_thr is not None:
            self.set_attr_value(13, packet_drop_queue_thr)
        if packet_drop_max_p is not None:
            self.set_attr_value(14, packet_drop_max_p)
        if queue_drop_w_q is not None:
            self.set_attr_value(15, queue_drop_w_q)
        if drop_precedence_colour_marking is not None:
            self.set_attr_value(16, drop_precedence_colour_marking)


#################
# mcast_gem_iw_tp: Multicast GEM interworking termination point
#################

mcast_gem_iw_tp_iw_opt = EnumDatum(
    1,
    (
        ('NO_OP', 0x0),
        ('MAC_BRIDGED_LAN', 0x1),
        ('RESERVED', 0x3),
        ('IEEE_8021_P_MAPPER', 0x5),
    )
)

mcast_gem_iw_tp_oper_state = EnumDatum(
    1,
    (
        ('ENABLED', 0x0),
        ('DISABLED', 0x1),
    )
)




class mcast_gem_iw_tp_ipv_4_mcast_addr_table(StructDatum):
    fields = (
        StructField('gem_port_id', 'GEM Port ID', field_type=NumberDatum(2)),
        StructField('secondary_key', 'Secondary Key', field_type=NumberDatum(2)),
        StructField('mcast_addr_range_start', 'IP multicast destination address range start', field_type=NumberDatum(4)),
        StructField('mcast_addr_range_stop', 'IP multicast destination address range stop', field_type=NumberDatum(4)),
    )
    def __init__(self, default: AttrValue = None, fixed: AttrValue = None, size = 12):
        super().__init__(size, default=default, fixed=fixed)


class mcast_gem_iw_tp_ipv_6_mcast_addr_table(StructDatum):
    fields = (
        StructField('gem_port_id', 'GEM Port ID', field_type=NumberDatum(2)),
        StructField('secondary_key', 'Secondary Key', field_type=NumberDatum(2)),
        StructField('mcast_addr_range_start_lsb', 'LSB of IP multicast destination address range start', field_type=NumberDatum(4)),
        StructField('mcast_addr_range_stop_lsb', 'LSB of IP multicast destination address range stop', field_type=NumberDatum(4)),
        StructField('mcast_addr_range_msb', 'Most significant bytes; IP destination address', field_type=BytesDatum(12)),
    )
    def __init__(self, default: AttrValue = None, fixed: AttrValue = None, size = 24):
        super().__init__(size, default=default, fixed=fixed)

class mcast_gem_iw_tp_me(ME):
    """ MCAST_GEM_IW_TP (281) - Multicast GEM interworking termination point. """
    me_class = 281
    name = 'MCAST_GEM_IW_TP'
    description = 'Multicast GEM interworking termination point'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'gem_port_net_ctp_conn_ptr', 'GEM port network CTP connectivity pointer', 'RC', 'M', NumberDatum(2)),
        Attr(2, 'iw_opt', 'Interworking option', 'RWC', 'M', mcast_gem_iw_tp_iw_opt),
        Attr(3, 'svc_prof_ptr', 'Service profile pointer', 'RWC', 'M', NumberDatum(2)),
        Attr(4, 'not_used_1', 'Not used 1', 'RWC', 'M', NumberDatum(2)),
        Attr(5, 'pptp_counter', 'PPTP Counter', 'R', 'O', NumberDatum(1)),
        Attr(6, 'oper_state', 'Operational state', 'R', 'O', mcast_gem_iw_tp_oper_state),
        Attr(7, 'gal_prof_ptr', 'GAL profile pointer', 'RWC', 'M', NumberDatum(2)),
        Attr(8, 'not_used_2', 'Not used 2', 'RWC', 'M', NumberDatum(1)),
        Attr(9, 'ipv_4_mcast_addr_table', 'IPv4 multicast address table', 'RW', 'M', mcast_gem_iw_tp_ipv_4_mcast_addr_table()),
        Attr(10, 'ipv_6_mcast_addr_table', 'IPv6 multicast address table', 'RW', 'O', mcast_gem_iw_tp_ipv_6_mcast_addr_table()),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get', 'get_next')

    def __init__(self,
            inst : int,
            gem_port_net_ctp_conn_ptr = None,
            iw_opt = None,
            svc_prof_ptr = None,
            not_used_1 = None,
            gal_prof_ptr = None,
            not_used_2 = None,
            ipv_4_mcast_addr_table = None,
            ipv_6_mcast_addr_table = None
        ):
        """ MCAST_GEM_IW_TP ME Constructor.

        Args:
            inst : ME instance.
            gem_port_net_ctp_conn_ptr : Attribute #1. GEM port network CTP connectivity pointer.
            iw_opt : Attribute #2. Interworking option.
            svc_prof_ptr : Attribute #3. Service profile pointer.
            not_used_1 : Attribute #4. Not used 1.
            gal_prof_ptr : Attribute #7. GAL profile pointer.
            not_used_2 : Attribute #8. Not used 2.
            ipv_4_mcast_addr_table : Attribute #9. IPv4 multicast address table.
            ipv_6_mcast_addr_table : Attribute #10. IPv6 multicast address table.
        """
        super(mcast_gem_iw_tp_me, self).__init__(inst)
        if gem_port_net_ctp_conn_ptr is not None:
            self.set_attr_value(1, gem_port_net_ctp_conn_ptr)
        if iw_opt is not None:
            self.set_attr_value(2, iw_opt)
        if svc_prof_ptr is not None:
            self.set_attr_value(3, svc_prof_ptr)
        if not_used_1 is not None:
            self.set_attr_value(4, not_used_1)
        if gal_prof_ptr is not None:
            self.set_attr_value(7, gal_prof_ptr)
        if not_used_2 is not None:
            self.set_attr_value(8, not_used_2)
        if ipv_4_mcast_addr_table is not None:
            self.set_attr_value(9, ipv_4_mcast_addr_table)
        if ipv_6_mcast_addr_table is not None:
            self.set_attr_value(10, ipv_6_mcast_addr_table)


#################
# mcast_operations_profile: Multicast Operations Profile
#################

mcast_operations_profile_igmp_version = EnumDatum(
    1,
    (
        ('DEPRECATED', 0x1),
        ('IGMP_VERSION_2', 0x2),
        ('IGMP_VERSION_3', 0x3),
        ('MLD_VERSION_1', 0x10),
        ('MLD_VERSION_2', 0x11),
    )
)

mcast_operations_profile_igmp_function = EnumDatum(
    1,
    (
        ('TRANSPARENT_IGMP_SNOOPING', 0x0),
        ('SPR', 0x1),
        ('IGMP_PROXY', 0x2),
    )
)

mcast_operations_profile_upstream_igmp_tag_control = EnumDatum(
    1,
    (
        ('PASS_IGMP_MLD_TRANSPARENT', 0x0),
        ('ADD_VLAN_TAG', 0x1),
        ('REPLACE_VLAN_TAG', 0x2),
        ('REPLACE_VLAN_ID', 0x3),
    )
)


mcast_operations_profile_ds_igmp_and_multicast_tci_control_type = EnumDatum(
    1,
    (
        ('TRANSPARENT', 0x0),
        ('STRIP_OUTER_TAG', 0x1),
        ('ADD_OUTER_TAG', 0x2),
        ('REPLACE_OUTER_TCI', 0x3),
        ('REPLACE_OUTER_VID', 0x4),
        ('ADD_OUTER_TAG_BY_SUBSCRIBER_CONFIG_INFO', 0x5),
        ('REPLACE_OUTER_TCI_BY_SUBSCRIBER_CONFIG_INFO', 0x6),
        ('REPLACE_OUTER_VID_BY_SUBSCRIBER_CONFIG_INFO', 0x7),
    )
)



class mcast_operations_profile_dynamic_access_control_list_table(StructDatum):
    fields = (
        StructField('table_control', 'Table Control', field_type=NumberDatum(2)),
        StructField('gem_port_id', 'GEM Port ID', field_type=NumberDatum(2)),
        StructField('vlan_id', 'VAN ID', field_type=NumberDatum(2)),
        StructField('src_ip', 'Source IP', field_type=NumberDatum(4)),
        StructField('ip_mcast_addr_start', 'Destination IP address start of range', field_type=NumberDatum(4)),
        StructField('ip_mcast_addr_end', 'Destination IP address end of range', field_type=NumberDatum(4)),
        StructField('imputed_grp_bw', 'Imputed Group', field_type=NumberDatum(4)),
        StructField('reserved', 'Reserved', field_type=NumberDatum(2)),
    )
    def __init__(self, default: AttrValue = None, fixed: AttrValue = None, size = 24):
        super().__init__(size, default=default, fixed=fixed)


class mcast_operations_profile_static_access_control_list_table(StructDatum):
    fields = (
        StructField('table_control', 'Table Control', field_type=NumberDatum(2)),
        StructField('gem_port_id', 'GEM Port ID', field_type=NumberDatum(2)),
        StructField('vlan_id', 'VAN ID', field_type=NumberDatum(2)),
        StructField('src_ip', 'Source IP', field_type=NumberDatum(4)),
        StructField('ip_mcast_addr_start', 'Destination IP address start of range', field_type=NumberDatum(4)),
        StructField('ip_mcast_addr_end', 'Destination IP address end of range', field_type=NumberDatum(4)),
        StructField('imputed_grp_bw', 'Imputed Group', field_type=NumberDatum(4)),
        StructField('reserved', 'Reserved', field_type=NumberDatum(2)),
    )
    def __init__(self, default: AttrValue = None, fixed: AttrValue = None, size = 24):
        super().__init__(size, default=default, fixed=fixed)


class mcast_operations_profile_ds_igmp_and_multicast_tci(StructDatum):
    fields = (
        StructField('control_type', 'Control type', field_type=mcast_operations_profile_ds_igmp_and_multicast_tci_control_type),
        StructField('tci', 'TCI', field_type=NumberDatum(2)),
    )
    def __init__(self, default: AttrValue = None, fixed: AttrValue = None, size = 3):
        super().__init__(size, default=default, fixed=fixed)

class mcast_operations_profile_me(ME):
    """ MCAST_OPERATIONS_PROFILE (309) - Multicast Operations Profile. """
    me_class = 309
    name = 'MCAST_OPERATIONS_PROFILE'
    description = 'Multicast Operations Profile'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'igmp_version', 'IGMP version', 'RWC', 'M', mcast_operations_profile_igmp_version),
        Attr(2, 'igmp_function', 'IGMP function', 'RWC', 'M', mcast_operations_profile_igmp_function),
        Attr(3, 'immediate_leave', 'Immediate leave', 'RWC', 'M', NumberDatum(1)),
        Attr(4, 'upstream_igmp_tci', 'Upstream IGMP TCI', 'RWC', 'O', NumberDatum(2)),
        Attr(5, 'upstream_igmp_tag_control', 'Upstream IGMP tag control', 'RWC', 'O', mcast_operations_profile_upstream_igmp_tag_control),
        Attr(6, 'upstream_igmp_rate', 'Upstream IGMP rate', 'RWC', 'O', NumberDatum(4)),
        Attr(7, 'dynamic_access_control_list_table', 'Dynamic access control list table', 'RW', 'M', mcast_operations_profile_dynamic_access_control_list_table()),
        Attr(8, 'static_access_control_list_table', 'Static access control list table', 'RW', 'M', mcast_operations_profile_static_access_control_list_table()),
        Attr(9, 'lost_groups_list_table', 'Lost groups list table', 'R', 'O', BytesDatum(10)),
        Attr(10, 'robustness', 'Robustness', 'RWC', 'O', NumberDatum(1)),
        Attr(11, 'querier_ip_address', 'Querier IP address', 'RWC', 'O', NumberDatum(4)),
        Attr(12, 'query_interval', 'query_interval', 'RWC', 'O', NumberDatum(4)),
        Attr(13, 'query_max_response_time', 'Query max response time', 'RWC', 'O', NumberDatum(4)),
        Attr(14, 'last_member_query_interval', 'Last member query interval', 'RW', 'O', NumberDatum(1)),
        Attr(15, 'unauth_join_request_behaviour', 'Unauthorized join request behaviour', 'RW', 'O', NumberDatum(1)),
        Attr(16, 'ds_igmp_and_multicast_tci', 'Downstream IGMP and multicast TCI', 'RWC', 'O', mcast_operations_profile_ds_igmp_and_multicast_tci()),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get', 'get_next', 'test')

    def __init__(self,
            inst : int,
            igmp_version = None,
            igmp_function = None,
            immediate_leave = None,
            upstream_igmp_tci = None,
            upstream_igmp_tag_control = None,
            upstream_igmp_rate = None,
            dynamic_access_control_list_table = None,
            static_access_control_list_table = None,
            robustness = None,
            querier_ip_address = None,
            query_interval = None,
            query_max_response_time = None,
            last_member_query_interval = None,
            unauth_join_request_behaviour = None,
            ds_igmp_and_multicast_tci = None
        ):
        """ MCAST_OPERATIONS_PROFILE ME Constructor.

        Args:
            inst : ME instance.
            igmp_version : Attribute #1. IGMP version.
            igmp_function : Attribute #2. IGMP function.
            immediate_leave : Attribute #3. Immediate leave.
            upstream_igmp_tci : Attribute #4. Upstream IGMP TCI.
            upstream_igmp_tag_control : Attribute #5. Upstream IGMP tag control.
            upstream_igmp_rate : Attribute #6. Upstream IGMP rate.
            dynamic_access_control_list_table : Attribute #7. Dynamic access control list table.
            static_access_control_list_table : Attribute #8. Static access control list table.
            robustness : Attribute #10. Robustness.
            querier_ip_address : Attribute #11. Querier IP address.
            query_interval : Attribute #12. query_interval.
            query_max_response_time : Attribute #13. Query max response time.
            last_member_query_interval : Attribute #14. Last member query interval.
            unauth_join_request_behaviour : Attribute #15. Unauthorized join request behaviour.
            ds_igmp_and_multicast_tci : Attribute #16. Downstream IGMP and multicast TCI.
        """
        super(mcast_operations_profile_me, self).__init__(inst)
        if igmp_version is not None:
            self.set_attr_value(1, igmp_version)
        if igmp_function is not None:
            self.set_attr_value(2, igmp_function)
        if immediate_leave is not None:
            self.set_attr_value(3, immediate_leave)
        if upstream_igmp_tci is not None:
            self.set_attr_value(4, upstream_igmp_tci)
        if upstream_igmp_tag_control is not None:
            self.set_attr_value(5, upstream_igmp_tag_control)
        if upstream_igmp_rate is not None:
            self.set_attr_value(6, upstream_igmp_rate)
        if dynamic_access_control_list_table is not None:
            self.set_attr_value(7, dynamic_access_control_list_table)
        if static_access_control_list_table is not None:
            self.set_attr_value(8, static_access_control_list_table)
        if robustness is not None:
            self.set_attr_value(10, robustness)
        if querier_ip_address is not None:
            self.set_attr_value(11, querier_ip_address)
        if query_interval is not None:
            self.set_attr_value(12, query_interval)
        if query_max_response_time is not None:
            self.set_attr_value(13, query_max_response_time)
        if last_member_query_interval is not None:
            self.set_attr_value(14, last_member_query_interval)
        if unauth_join_request_behaviour is not None:
            self.set_attr_value(15, unauth_join_request_behaviour)
        if ds_igmp_and_multicast_tci is not None:
            self.set_attr_value(16, ds_igmp_and_multicast_tci)


#################
# mcast_subscriber_config_info: Multicast subscriber config info
#################

mcast_subscriber_config_info_me_type = EnumDatum(
    1,
    (
        ('MAC_BRIDGE_PORT_CONFIG_DATA', 0x0),
        ('IEEE_8021P_MAPPER_SERVICE_PROFILE', 0x1),
    )
)



class mcast_subscriber_config_info_me(ME):
    """ MCAST_SUBSCRIBER_CONFIG_INFO (310) - Multicast subscriber config info. """
    me_class = 310
    name = 'MCAST_SUBSCRIBER_CONFIG_INFO'
    description = 'Multicast subscriber config info'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'me_type', 'ME Type', 'RWC', 'M', mcast_subscriber_config_info_me_type),
        Attr(2, 'mcast_operations_prof_ptr', 'Multicast operations profile pointer', 'RWC', 'M', NumberDatum(2)),
        Attr(3, 'max_simultaneous_groups', 'Max simultaneous groups', 'RWC', 'O', NumberDatum(2)),
        Attr(4, 'max_multicast_bw', 'Max multicast bandwidth', 'RWC', 'O', NumberDatum(4)),
        Attr(5, 'bw_enforcement', 'Bandwidth enforcement', 'RWC', 'O', NumberDatum(1)),
        Attr(6, 'mcast_svc_pkg_table', 'Multicast service package table', 'RW', 'O', BytesDatum(20)),
        Attr(7, 'allowed_preview_groups_table', 'Allowed preview groups table', 'RW', 'O', BytesDatum(24)),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get', 'get_next', 'test')

    def __init__(self,
            inst : int,
            me_type = None,
            mcast_operations_prof_ptr = None,
            max_simultaneous_groups = None,
            max_multicast_bw = None,
            bw_enforcement = None,
            mcast_svc_pkg_table = None,
            allowed_preview_groups_table = None
        ):
        """ MCAST_SUBSCRIBER_CONFIG_INFO ME Constructor.

        Args:
            inst : ME instance.
            me_type : Attribute #1. ME Type.
            mcast_operations_prof_ptr : Attribute #2. Multicast operations profile pointer.
            max_simultaneous_groups : Attribute #3. Max simultaneous groups.
            max_multicast_bw : Attribute #4. Max multicast bandwidth.
            bw_enforcement : Attribute #5. Bandwidth enforcement.
            mcast_svc_pkg_table : Attribute #6. Multicast service package table.
            allowed_preview_groups_table : Attribute #7. Allowed preview groups table.
        """
        super(mcast_subscriber_config_info_me, self).__init__(inst)
        if me_type is not None:
            self.set_attr_value(1, me_type)
        if mcast_operations_prof_ptr is not None:
            self.set_attr_value(2, mcast_operations_prof_ptr)
        if max_simultaneous_groups is not None:
            self.set_attr_value(3, max_simultaneous_groups)
        if max_multicast_bw is not None:
            self.set_attr_value(4, max_multicast_bw)
        if bw_enforcement is not None:
            self.set_attr_value(5, bw_enforcement)
        if mcast_svc_pkg_table is not None:
            self.set_attr_value(6, mcast_svc_pkg_table)
        if allowed_preview_groups_table is not None:
            self.set_attr_value(7, allowed_preview_groups_table)


#################
# pptp_eth_uni: PPTP Ethernet UNI
#################

pptp_eth_uni_auto_detection_config = EnumDatum(
    1,
    (
        ('AUTO_DETECT_CONFIG_AUTO_RATE_AUTO_MODE', 0x0),
        ('AUTO_DETECT_CONFIG_10_MEG_FULL_DUPLEX', 0x1),
        ('AUTO_DETECT_CONFIG_100_MEG_FULL_DUPLEX', 0x2),
        ('AUTO_DETECT_CONFIG_1000_MEG_FULL_DUPLEX', 0x3),
        ('AUTO_DETECT_CONFIG_AUTO_RATE_FULL_DUPLEX', 0x4),
        ('AUTO_DETECT_CONFIG_10_GIG_FULL_DUPLEX', 0x5),
        ('AUTO_DETECT_CONFIG_10_MEG_AUTO_MODE', 0x10),
        ('AUTO_DETECT_CONFIG_10_MEG_HALF_DUPLEX', 0x11),
        ('AUTO_DETECT_CONFIG_100_MEG_HALF_DUPLEX', 0x12),
        ('AUTO_DETECT_CONFIG_1000_MEG_HALF_DUPLEX', 0x13),
        ('AUTO_DETECT_CONFIG_AUTO_RATE_HALF_DUPLEX', 0x14),
        ('AUTO_DETECT_CONFIG_1000_MEG_AUTO_MODE', 0x20),
        ('AUTO_DETECT_CONFIG_100_MEG_AUTO_MODE', 0x30),
    )
)

pptp_eth_uni_ethernet_loopback_config = EnumDatum(
    1,
    (
        ('NO_LOOPBACK', 0x0),
        ('LOOP_3', 0x3),
    )
)

pptp_eth_uni_admin_state = EnumDatum(
    1,
    (
        ('UNLOCK', 0x0),
        ('LOCK', 0x1),
    )
)

pptp_eth_uni_oper_state = EnumDatum(
    1,
    (
        ('ENABLED', 0x0),
        ('DISABLED', 0x1),
    )
)

pptp_eth_uni_config_ind = EnumDatum(
    1,
    (
        ('CONFIG_UNKNOWN', 0x0),
        ('CONFIG_10_BASE_T_FULL_DUPLEX', 0x1),
        ('CONFIG_100_BASE_T_FULL_DUPLEX', 0x2),
        ('CONFIG_GIG_ETHERNET_FULL_DUPLEX', 0x3),
        ('CONFIG_10_GIG_ETHERNET_FULL_DUPLEX', 0x4),
        ('CONFIG_10_BASE_T_HALF_DUPLEX', 0x11),
        ('CONFIG_100_BASE_T_HALF_DUPLEX', 0x12),
        ('CONFIG_GIG_ETHERNET_HALF_DUPLEX', 0x13),
    )
)

pptp_eth_uni_dte_or_dce_ind = EnumDatum(
    1,
    (
        ('DCE_OR_MDI_X', 0x0),
        ('DTE_OR_MDI', 0x1),
        ('AUTO_SELECTION', 0x2),
    )
)

pptp_eth_uni_bridged_or_ip_ind = EnumDatum(
    1,
    (
        ('BRIDGED', 0x0),
        ('IP_ROUTER', 0x1),
        ('DEPENDENCY_ON_PARENT_CKT_PACK', 0x2),
    )
)



class pptp_eth_uni_me(ME):
    """ PPTP_ETH_UNI (11) - PPTP Ethernet UNI. """
    me_class = 11
    name = 'PPTP_ETH_UNI'
    description = 'PPTP Ethernet UNI'

    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'expected_type', 'Expected Type', 'RW', 'M', NumberDatum(1)),
        Attr(2, 'sensed_type', 'Sensed Type', 'R', 'M', NumberDatum(1)),
        Attr(3, 'auto_detection_config', 'Auto Detection Configuration', 'RW', 'M', pptp_eth_uni_auto_detection_config),
        Attr(4, 'ethernet_loopback_config', 'Ethernet loopback configuration', 'RW', 'M', pptp_eth_uni_ethernet_loopback_config),
        Attr(5, 'admin_state', 'Administrative State', 'RW', 'M', pptp_eth_uni_admin_state),
        Attr(6, 'oper_state', 'Operational State', 'R', 'O', pptp_eth_uni_oper_state),
        Attr(7, 'config_ind', 'Config Indication', 'R', 'M', pptp_eth_uni_config_ind),
        Attr(8, 'max_frame_size', 'Max frame size', 'RW', 'M', NumberDatum(2)),
        Attr(9, 'dte_or_dce_ind', 'DTE or DCE ind', 'RW', 'M', pptp_eth_uni_dte_or_dce_ind),
        Attr(10, 'pause_time', 'Pause time', 'RW', 'O', NumberDatum(2)),
        Attr(11, 'bridged_or_ip_ind', 'Bridged or IP ind', 'RW', 'O', pptp_eth_uni_bridged_or_ip_ind),
        Attr(12, 'arc', 'ARC', 'RW', 'O', NumberDatum(1)),
        Attr(13, 'arc_interval', 'ARC interval', 'RW', 'O', NumberDatum(1)),
        Attr(14, 'pppoe_filter', 'PPPoE filter', 'RW', 'O', NumberDatum(1)),
        Attr(15, 'power_control', 'Power control', 'RW', 'O', NumberDatum(1)),
    )
    num_attrs = len(attrs)
    actions = ('set', 'get')
    

    def __init__(self,
            inst : int,
            expected_type = None,
            auto_detection_config = None,
            ethernet_loopback_config = None,
            admin_state = None,
            max_frame_size = None,
            dte_or_dce_ind = None,
            pause_time = None,
            bridged_or_ip_ind = None,
            arc = None,
            arc_interval = None,
            pppoe_filter = None,
            power_control = None
        ):
        """ PPTP_ETH_UNI ME Constructor.

        Args:
            inst : ME instance.
            expected_type : Attribute #1. Expected Type.
            auto_detection_config : Attribute #3. Auto Detection Configuration.
            ethernet_loopback_config : Attribute #4. Ethernet loopback configuration.
            admin_state : Attribute #5. Administrative State.
            max_frame_size : Attribute #8. Max frame size.
            dte_or_dce_ind : Attribute #9. DTE or DCE ind.
            pause_time : Attribute #10. Pause time.
            bridged_or_ip_ind : Attribute #11. Bridged or IP ind.
            arc : Attribute #12. ARC.
            arc_interval : Attribute #13. ARC interval.
            pppoe_filter : Attribute #14. PPPoE filter.
            power_control : Attribute #15. Power control.
        """
        
        
        
        
        super(pptp_eth_uni_me, self).__init__(inst)
        if expected_type is not None:
            self.set_attr_value(1, expected_type)
        if auto_detection_config is not None:
            self.set_attr_value(3, auto_detection_config)
        if ethernet_loopback_config is not None:
            self.set_attr_value(4, ethernet_loopback_config)
        if admin_state is not None:
            self.set_attr_value(5, admin_state)
        if max_frame_size is not None:
            self.set_attr_value(8, max_frame_size)
        if dte_or_dce_ind is not None:
            self.set_attr_value(9, dte_or_dce_ind)
        if pause_time is not None:
            self.set_attr_value(10, pause_time)
        if bridged_or_ip_ind is not None:
            self.set_attr_value(11, bridged_or_ip_ind)
        if arc is not None:
            self.set_attr_value(12, arc)
        if arc_interval is not None:
            self.set_attr_value(13, arc_interval)
        if pppoe_filter is not None:
            self.set_attr_value(14, pppoe_filter)
        if power_control is not None:
            self.set_attr_value(15, power_control)

        self.alarms = (
            Alarm(0,'bbf-obbaa-ethernet-alarm-types:loss-of-signal','/ietf-interfaces:interfaces/interface','Loss of signal'),
        )
       
    


#################
# virtual_eth_intf_point: Virtual Ethernet Interface Point
#################

virtual_eth_intf_point_admin_state = EnumDatum(
    1,
    (
        ('UNLOCK', 0x0),
        ('LOCK', 0x1),
    )
)

virtual_eth_intf_point_oper_state = EnumDatum(
    1,
    (
        ('ENABLED', 0x0),
        ('DISABLED', 0x1),
    )
)



class virtual_eth_intf_point_me(ME):
    """ VIRTUAL_ETH_INTF_POINT (329) - Virtual Ethernet Interface Point. """
    me_class = 329
    name = 'VIRTUAL_ETH_INTF_POINT'
    description = 'Virtual Ethernet Interface Point'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'admin_state', 'Admin state', 'RW', 'M', virtual_eth_intf_point_admin_state),
        Attr(2, 'oper_state', 'Operational state', 'R', 'O', virtual_eth_intf_point_oper_state),
        Attr(3, 'interdomain_name', 'Interdomain Name', 'RW', 'O', BytesDatum(25)),
        Attr(4, 'tcp_udp_ptr', 'TCP/UDP pointer', 'RW', 'O', NumberDatum(2)),
        Attr(5, 'iana_assigned_port', 'IANA Assigned port', 'R', 'M', NumberDatum(2)),
    )
    num_attrs = len(attrs)
    actions = ('set', 'get')

    def __init__(self,
            inst : int,
            admin_state = None,
            interdomain_name = None,
            tcp_udp_ptr = None,
        ):
        """ VIRTUAL_ETH_INTF_POINT ME Constructor.

        Args:
            inst : ME instance.
            admin_state : Attribute #1. Admin state.
            interdomain_name : Attribute #3. Interdomain Name.
            tcp_udp_ptr : Attribute #4. TCP/UDP pointer.
        """
        super(virtual_eth_intf_point_me, self).__init__(inst)
        if admin_state is not None:
            self.set_attr_value(1, admin_state)
        if interdomain_name is not None:
            self.set_attr_value(3, interdomain_name)
        if tcp_udp_ptr is not None:
            self.set_attr_value(4, tcp_udp_ptr)


#################
# onu_data: ONU data
#################



class onu_data_me(ME):
    """ ONU_DATA (2) - ONU data. """
    me_class = 2
    name = 'ONU_DATA'
    description = 'ONU data'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'mib_data_sync', '', 'RW', 'M', NumberDatum(1)),
    )
    num_attrs = len(attrs)
    actions = ('set', 'get', 'reboot')

    def __init__(self,
            inst : int,
            mib_data_sync = None
        ):
        """ ONU_DATA ME Constructor.

        Args:
            inst : ME instance.
            mib_data_sync : Attribute #1. .
        """
        super(onu_data_me, self).__init__(inst)
        if mib_data_sync is not None:
            self.set_attr_value(1, mib_data_sync)


#################
# onu_g: ONU-G (9.1.1)
#################

onu_g_traffic_management = EnumDatum(
    1,
    (
        ('PRIORITY', 0x0),
        ('RATE', 0x1),
        ('PRIORITY_AND_RATE', 0x2),
    )
)

onu_g_admin_state = EnumDatum(
    1,
    (
        ('UNLOCK', 0x0),
        ('LOCK', 0x1),
    )
)

onu_g_oper_state = EnumDatum(
    1,
    (
        ('ENABLED', 0x0),
        ('DISABLED', 0x1),
    )
)

onu_g_credentials_status = EnumDatum(
    1,
    (
        ('INITIAL_STATE', 0x0),
        ('SUCCESSFUL_AUTHENTICATION', 0x1),
        ('LOID_ERROR', 0x2),
        ('PASSWORD_ERROR', 0x3),
        ('DUPLICATE_LOID', 0x4),
    )
)



class onu_g_me(ME):
    """ ONU_G (256) - ONU-G (9.1.1). """
    me_class = 256
    name = 'ONU_G'
    description = 'ONU-G (9.1.1)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'vendor_id', '4 MS bytes of ONU serial number', 'R', 'M', BytesDatum(4)),
        Attr(2, 'version', 'ONU version string by the vendor', 'R', 'M', BytesDatum(14)),
        Attr(3, 'serial_number', 'Serial number', 'R', 'M', BytesDatum(8)),
        Attr(4, 'traffic_management', '', 'R', 'M', onu_g_traffic_management),
        Attr(5, 'deprecated0', '', 'R', 'O', NumberDatum(1)),
        Attr(6, 'battery_backup', '', 'RW', 'M', NumberDatum(1)),
        Attr(7, 'admin_state', '', 'RW', 'M', onu_g_admin_state),
        Attr(8, 'oper_state', '', 'R', 'O', onu_g_oper_state),
        Attr(9, 'survival_time', '', 'R', 'O', NumberDatum(1)),
        Attr(10, 'logical_onu_id', '', 'R', 'O', BytesDatum(24)),
        Attr(11, 'logical_password', '', 'R', 'O', BytesDatum(12)),
        Attr(12, 'credentials_status', '', 'RW', 'O', onu_g_credentials_status),
        Attr(13, 'extended_tc_options', '', 'R', 'O', NumberDatum(2)),
    )
    num_attrs = len(attrs)
    actions = ('set', 'get', 'sync_time')

    def __init__(self,
            inst : int,
            battery_backup = None,
            admin_state = None,
            credentials_status = None,
        ):
        """ ONU_G ME Constructor.

        Args:
            inst : ME instance.
            battery_backup : Attribute #6. .
            admin_state : Attribute #7. .
            credentials_status : Attribute #12. .
        """
        super(onu_g_me, self).__init__(inst)
        if battery_backup is not None:
            self.set_attr_value(6, battery_backup)
        if admin_state is not None:
            self.set_attr_value(7, admin_state)
        if credentials_status is not None:
            self.set_attr_value(12, credentials_status)


#################
# onu2_g: ONU2-G (9.1.2)
#################

onu2_g_omcc_version = EnumDatum(
    1,
    (
        ('BASELINE_2004', 0x80),
        ('BASELINE_2004_AMD1', 0x81),
        ('BASELINE_2004_AMD2', 0x82),
        ('BASELINE_2004_AMD3', 0x83),
        ('BASELINE_2008', 0x84),
        ('BASELINE_2008_AMD1', 0x85),
        ('BASELINE_2008_AMD2', 0x86),
        ('BASELINE_AND_EXTENDED_2008_AMD2', 0x96),
        ('BASELINE_2010', 0xa0),
        ('BASELINE_AMD1', 0xa1),
        ('BASELINE_AMD2', 0xa2),
        ('BASELINE_2012', 0xa3),
        ('BASELINE_AND_EXTENDED_2010', 0xb0),
        ('BASELINE_AND_EXTENDED_AMD1', 0xb1),
        ('BASELINE_AND_EXTENDED_AMD2', 0xb2),
        ('BASELINE_AND_EXTENDED_2012', 0xb3),
        ('BASELINE_AND_EXTENDED_2014', 0xb4),
    )
)

onu2_g_security_capability = EnumDatum(
    1,
    (
        ('AES_128', 0x1),
    )
)

onu2_g_security_mode = EnumDatum(
    1,
    (
        ('AES_128', 0x1),
    )
)

onu2_g_connectivity_mode = EnumDatum(
    1,
    (
        ('NO_SELECTION', 0x0),
        ('N_1_BRIDGING', 0x1),
        ('1_M_MAPPING', 0x2),
        ('1_P_FILTERING', 0x3),
        ('N_M_BRIDGE_MAPPING', 0x4),
        ('1_MP_MAP_FILERING', 0x5),
        ('N_P_BRIDGE_FILTERING', 0x6),
        ('N_P_BRIDGE_MAP_FILTERING', 0x7),
    )
)



class onu2_g_me(ME):
    """ ONU2_G (257) - ONU2-G (9.1.2). """
    me_class = 257
    name = 'ONU2_G'
    description = 'ONU2-G (9.1.2)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'equipment_id', '', 'R', 'O', BytesDatum(20)),
        Attr(2, 'omcc_version', '', 'R', 'M', onu2_g_omcc_version),
        Attr(3, 'vendor_product_code', '', 'R', 'O', NumberDatum(2)),
        Attr(4, 'security_capability', '', 'R', 'M', onu2_g_security_capability),
        Attr(5, 'security_mode', '', 'RW', 'M', onu2_g_security_mode),
        Attr(6, 'total_priority_queue_number', '', 'R', 'M', NumberDatum(2)),
        Attr(7, 'total_traf_sched_number', '', 'R', 'M', NumberDatum(1)),
        Attr(8, 'deprecated0', '', 'R', 'M', NumberDatum(1)),
        Attr(9, 'total_gem_port_number', '', 'R', 'O', NumberDatum(2)),
        Attr(10, 'sys_up_time', 'In 10ms intervals', 'R', 'O', NumberDatum(4)),
        Attr(11, 'connectivity_capability', '', 'R', 'O', NumberDatum(2)),
        Attr(12, 'connectivity_mode', '', 'RW', 'O', onu2_g_connectivity_mode),
        Attr(13, 'qos_config_flexibility', 'Actually it is an enum', 'R', 'O', NumberDatum(2)),
        Attr(14, 'priority_queue_scale_factor', '', 'RW', 'O', NumberDatum(2)),
    )
    num_attrs = len(attrs)
    actions = ('set', 'get')

    def __init__(self,
            inst : int,
            security_mode = None,
            connectivity_mode = None,
            priority_queue_scale_factor = None
        ):
        """ ONU2_G ME Constructor.

        Args:
            inst : ME instance.
            security_mode : Attribute #5. .
            connectivity_mode : Attribute #12. .
            priority_queue_scale_factor : Attribute #14. .
        """
        super(onu2_g_me, self).__init__(inst)
        if security_mode is not None:
            self.set_attr_value(5, security_mode)
        if connectivity_mode is not None:
            self.set_attr_value(12, connectivity_mode)
        if priority_queue_scale_factor is not None:
            self.set_attr_value(14, priority_queue_scale_factor)


#################
# sw_image: Software image (9.1.4)
#################

sw_image_is_committed = EnumDatum(
    1,
    (
        ('UNCOMMITTED', 0x0),
        ('COMMITTED', 0x1),
    )
)

sw_image_is_active = EnumDatum(
    1,
    (
        ('INACTIVE', 0x0),
        ('ACTIVE', 0x1),
    )
)

sw_image_is_valid = EnumDatum(
    1,
    (
        ('INVALID', 0x0),
        ('VALID', 0x1),
    )
)



class sw_image_me(ME):
    """ SW_IMAGE (7) - Software image (9.1.4). """
    me_class = 7
    name = 'SW_IMAGE'
    description = 'Software image (9.1.4)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'version', '', 'R', 'M', BytesDatum(14)),
        Attr(2, 'is_committed', '', 'R', 'M', sw_image_is_committed),
        Attr(3, 'is_active', '', 'R', 'M', sw_image_is_active),
        Attr(4, 'is_valid', '', 'R', 'M', sw_image_is_valid),
        Attr(5, 'product_code', '', 'R', 'O', BytesDatum(25)),
        Attr(6, 'image_hash', '', 'R', 'O', BytesDatum(16)),
    )
    num_attrs = len(attrs)
    actions = ('get', 'sw_download', 'download_section', 'end_sw_download', 'activate_sw', 'commit_sw')

    def __init__(self,
            inst : int,
        ):
        """ SW_IMAGE ME Constructor.

        Args:
            inst : ME instance.
        """
        super(sw_image_me, self).__init__(inst)


#################
# ani_g: ANI-G (9.2.1)
#################



class ani_g_me(ME):
    """ ANI_G (263) - ANI-G (9.2.1). """
    me_class = 263
    name = 'ANI_G'
    description = 'ANI-G (9.2.1)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'sr_indication', '', 'R', 'M', NumberDatum(1)),
        Attr(2, 'total_tcont_number', '', 'R', 'M', NumberDatum(2)),
        Attr(3, 'gem_block_length', '', 'RW', 'M', NumberDatum(2)),
        Attr(4, 'piggy_back_dba_reporting', '', 'R', 'M', NumberDatum(1)),
        Attr(5, 'deprecated', '', 'R', 'M', NumberDatum(1)),
        Attr(6, 'sf_threshold', '', 'RW', 'M', NumberDatum(1)),
        Attr(7, 'sd_threshold', '', 'RW', 'M', NumberDatum(1)),
        Attr(8, 'arc', '', 'RW', 'O', NumberDatum(1)),
        Attr(9, 'arc_interval', '', 'RW', 'O', NumberDatum(1)),
        Attr(10, 'optical_signal_level', '', 'R', 'O', NumberDatum(2)),
        Attr(11, 'lower_optical_threshold', '', 'RW', 'O', NumberDatum(1)),
        Attr(12, 'upper_optical_threshold', '', 'RW', 'O', NumberDatum(1)),
        Attr(13, 'onu_response_time', '', 'R', 'O', NumberDatum(2)),
        Attr(14, 'transmit_optical_level', '', 'R', 'O', NumberDatum(2)),
        Attr(15, 'lower_transmit_power_threshold', '', 'RW', 'O', NumberDatum(1)),
        Attr(16, 'upper_transmit_power_threshold', '', 'RW', 'O', NumberDatum(1)),
    )
    num_attrs = len(attrs)
    actions = ('set', 'get', 'test')

    def __init__(self,
            inst : int,
            gem_block_length = None,
            sf_threshold = None,
            sd_threshold = None,
            arc = None,
            arc_interval = None,
            lower_optical_threshold = None,
            upper_optical_threshold = None,
            lower_transmit_power_threshold = None,
            upper_transmit_power_threshold = None
        ):
        """ ANI_G ME Constructor.

        Args:
            inst : ME instance.
            gem_block_length : Attribute #3. .
            sf_threshold : Attribute #6. .
            sd_threshold : Attribute #7. .
            arc : Attribute #8. .
            arc_interval : Attribute #9. .
            lower_optical_threshold : Attribute #11. .
            upper_optical_threshold : Attribute #12. .
            lower_transmit_power_threshold : Attribute #15. .
            upper_transmit_power_threshold : Attribute #16. .
        """



        super(ani_g_me, self).__init__(inst)
        if gem_block_length is not None:
            self.set_attr_value(3, gem_block_length)
        if sf_threshold is not None:
            self.set_attr_value(6, sf_threshold)
        if sd_threshold is not None:
            self.set_attr_value(7, sd_threshold)
        if arc is not None:
            self.set_attr_value(8, arc)
        if arc_interval is not None:
            self.set_attr_value(9, arc_interval)
        if lower_optical_threshold is not None:
            self.set_attr_value(11, lower_optical_threshold)
        if upper_optical_threshold is not None:
            self.set_attr_value(12, upper_optical_threshold)
        if lower_transmit_power_threshold is not None:
            self.set_attr_value(15, lower_transmit_power_threshold)
        if upper_transmit_power_threshold is not None:
            self.set_attr_value(16, upper_transmit_power_threshold)

        
        self.alarms = (
            Alarm(0,'bbf-hardware-transceiver-alarm-types:rx-power-low', '/ietf-hardware:hardware/component','Low receive (RX) input power'),
            Alarm(1,'bbf-hardware-transceiver-alarm-types:rx-power-high','/ietf-hardware:hardware/component','High receive (RX) input power'),
            Alarm(2,'bbf-obbaa-xpon-onu-alarm-types:signal-fail','/ietf-interfaces:interfaces/interface','Signal Fail'),
            Alarm(3,'bbf-obbaa-xpon-onu-alarm-types:signal-degraded','/ietf-interfaces:interfaces/interface','Signal Degraded'),
            Alarm(4,'bbf-hardware-transceiver-alarm-types:tx-power-low','/ietf-hardware:hardware/component','Low transmit (TX) input power'),
            Alarm(5,'bbf-hardware-transceiver-alarm-types:tx-power-high','/ietf-hardware:hardware/component','High transmit (TX) input power'),
            Alarm(6,'bbf-hardware-transceiver-alarm-types:tx-bias-high','/ietf-hardware:hardware/component','High transmit (TX) bias current'),
        )

#################
# gem_port_net_ctp_pm: GEM Port Network CTP PM(9.2.13)
#################



class gem_port_net_ctp_pm_me(ME):
    """ GEM_PORT_NET_CTP_PM (341) - GEM Port Network CTP PM(9.2.13). """
    me_class = 341
    name = 'GEM_PORT_NET_CTP_PM'
    description = 'GEM Port Network CTP PM(9.2.13)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'interval_end_time', '', 'R', 'M', NumberDatum(1)),
        Attr(2, 'threshold_data', '', 'RWC', 'M', NumberDatum(2)),
        Attr(3, 'tx_gem_frames', '', 'R', 'M', NumberDatum(4)),
        Attr(4, 'rx_gem_frames', '', 'R', 'M', NumberDatum(4)),
        Attr(5, 'rx_payload_bytes', '', 'R', 'M', BytesDatum(8)),
        Attr(6, 'tx_payload_bytes', '', 'R', 'M', BytesDatum(8)),
        Attr(7, 'encry_key_errors', '', 'R', 'O', NumberDatum(4)),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            threshold_data = None,
        ):
        """ GEM_PORT_NET_CTP_PM ME Constructor.

        Args:
            inst : ME instance.
            threshold_data : Attribute #2. .
        """
        super(gem_port_net_ctp_pm_me, self).__init__(inst)
        if threshold_data is not None:
            self.set_attr_value(2, threshold_data)


#################
# eth_frame_upstream_pm: ETH FRAME UPSTREAM PM(9.3.30)
#################



class eth_frame_upstream_pm_me(ME):
    """ ETH_FRAME_UPSTREAM_PM (322) - ETH FRAME UPSTREAM PM(9.3.30). """
    me_class = 322
    name = 'ETH_FRAME_UPSTREAM_PM'
    description = 'ETH FRAME UPSTREAM PM(9.3.30)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'interval_end_time', '', 'R', 'M', NumberDatum(1)),
        Attr(2, 'threshold_data', '', 'RWC', 'M', NumberDatum(2)),
        Attr(3, 'up_drop_events', '', 'R', 'M', NumberDatum(4)),
        Attr(4, 'up_octets', '', 'R', 'M', NumberDatum(4)),
        Attr(5, 'up_packets', '', 'R', 'M', NumberDatum(4)),
        Attr(6, 'up_broadcast_packets', '', 'R', 'M', NumberDatum(4)),
        Attr(7, 'up_multicast_packets', '', 'R', 'M', NumberDatum(4)),
        Attr(8, 'up_crc_errored_packets', '', 'R', 'M', NumberDatum(4)),
        Attr(9, 'up_undersize_packets', '', 'R', 'M', NumberDatum(4)),
        Attr(10, 'up_oversize_packets', '', 'R', 'M', NumberDatum(4)),
        Attr(11, 'up_packets_64_octets', '', 'R', 'M', NumberDatum(4)),
        Attr(12, 'up_packets_65_127_octets', '', 'R', 'M', NumberDatum(4)),
        Attr(13, 'up_packets_128_255_octets', '', 'R', 'M', NumberDatum(4)),
        Attr(14, 'up_packets_256_511_octets', '', 'R', 'M', NumberDatum(4)),
        Attr(15, 'up_packets_512_1023_octets', '', 'R', 'M', NumberDatum(4)),
        Attr(16, 'up_packets_1024_1518_octets', '', 'R', 'M', NumberDatum(4)),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            threshold_data = None,
        ):
        """ ETH_FRAME_UPSTREAM_PM ME Constructor.

        Args:
            inst : ME instance.
            threshold_data : Attribute #2. .
        """
        super(eth_frame_upstream_pm_me, self).__init__(inst)
        if threshold_data is not None:
            self.set_attr_value(2, threshold_data)


#################
# eth_frame_downstream_pm: ETH FRAME DOWNSTREAM PM(9.3.31)
#################



class eth_frame_downstream_pm_me(ME):
    """ ETH_FRAME_DOWNSTREAM_PM (321) - ETH FRAME DOWNSTREAM PM(9.3.31). """
    me_class = 321
    name = 'ETH_FRAME_DOWNSTREAM_PM'
    description = 'ETH FRAME DOWNSTREAM PM(9.3.31)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'interval_end_time', '', 'R', 'M', NumberDatum(1)),
        Attr(2, 'threshold_data', '', 'RWC', 'M', NumberDatum(2)),
        Attr(3, 'dn_drop_events', '', 'R', 'M', NumberDatum(4)),
        Attr(4, 'dn_octets', '', 'R', 'M', NumberDatum(4)),
        Attr(5, 'dn_packets', '', 'R', 'M', NumberDatum(4)),
        Attr(6, 'dn_broadcast_packets', '', 'R', 'M', NumberDatum(4)),
        Attr(7, 'dn_multicast_packets', '', 'R', 'M', NumberDatum(4)),
        Attr(8, 'dn_crc_errored_packets', '', 'R', 'M', NumberDatum(4)),
        Attr(9, 'dn_undersize_packets', '', 'R', 'M', NumberDatum(4)),
        Attr(10, 'dn_oversize_packets', '', 'R', 'M', NumberDatum(4)),
        Attr(11, 'dn_packets_64_octets', '', 'R', 'M', NumberDatum(4)),
        Attr(12, 'dn_packets_65_127_octets', '', 'R', 'M', NumberDatum(4)),
        Attr(13, 'dn_packets_128_255_octets', '', 'R', 'M', NumberDatum(4)),
        Attr(14, 'dn_packets_256_511_octets', '', 'R', 'M', NumberDatum(4)),
        Attr(15, 'dn_packets_512_1023_octets', '', 'R', 'M', NumberDatum(4)),
        Attr(16, 'dn_packets_1024_1518_octets', '', 'R', 'M', NumberDatum(4)),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            threshold_data = None,
        ):
        """ ETH_FRAME_DOWNSTREAM_PM ME Constructor.

        Args:
            inst : ME instance.
            threshold_data : Attribute #2. .
        """
        super(eth_frame_downstream_pm_me, self).__init__(inst)
        if threshold_data is not None:
            self.set_attr_value(2, threshold_data)


#################
# fec_pm: FEC PERFORMANCE PM DATA(9.2.9)
#################



class fec_pm_me(ME):
    """ FEC_PM (312) - FEC PERFORMANCE PM DATA(9.2.9). """
    me_class = 312
    name = 'FEC_PM'
    description = 'FEC PERFORMANCE PM DATA(9.2.9)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'interval_end_time', '', 'R', 'M', NumberDatum(1)),
        Attr(2, 'threshold_data', '', 'RWC', 'M', NumberDatum(2)),
        Attr(3, 'corrected_bytes', '', 'R', 'M', NumberDatum(4)),
        Attr(4, 'corrected_code_words', '', 'R', 'M', NumberDatum(4)),
        Attr(5, 'uncorrectable_code_words', '', 'R', 'M', NumberDatum(4)),
        Attr(6, 'total_code_words', '', 'R', 'M', NumberDatum(4)),
        Attr(7, 'fec_seconds', '', 'R', 'M', NumberDatum(2)),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            threshold_data = None,
        ):
        """ FEC_PM ME Constructor.

        Args:
            inst : ME instance.
            threshold_data : Attribute #2. .
        """
        super(fec_pm_me, self).__init__(inst)
        if threshold_data is not None:
            self.set_attr_value(2, threshold_data)


#################
# xgpon_tc_pm: XG-PON TC PERFORMANCE PM DATA(9.2.15)
#################



class xgpon_tc_pm_me(ME):
    """ XGPON_TC_PM (344) - XG-PON TC PERFORMANCE PM DATA(9.2.15). """
    me_class = 344
    name = 'XGPON_TC_PM'
    description = 'XG-PON TC PERFORMANCE PM DATA(9.2.15)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'interval_end_time', '', 'R', 'M', NumberDatum(1)),
        Attr(2, 'threshold_data', '', 'RWC', 'M', NumberDatum(2)),
        Attr(3, 'psbd_hec_error_count', '', 'R', 'O', NumberDatum(4)),
        Attr(4, 'xgtc_hec_error_count', '', 'R', 'O', NumberDatum(4)),
        Attr(5, 'unknown_profile_count', '', 'R', 'O', NumberDatum(4)),
        Attr(6, 'transmitted_xgem_frames', '', 'R', 'M', NumberDatum(4)),
        Attr(7, 'fragment_xgem_frames', '', 'R', 'O', NumberDatum(4)),
        Attr(8, 'xgem_hec_lost_words_count', '', 'R', 'O', NumberDatum(4)),
        Attr(9, 'xgem_key_errors', '', 'R', 'M', NumberDatum(4)),
        Attr(10, 'xgem_hec_error_count', '', 'R', 'M', NumberDatum(4)),
        Attr(11, 'tx_bytes_in_non_idle_xgem_frames', '', 'R', 'M', BytesDatum(8)),
        Attr(12, 'rx_bytes_in_non_idle_xgem_frames', '', 'R', 'O', BytesDatum(8)),
        Attr(13, 'lods_event_count', '', 'R', 'O', NumberDatum(4)),
        Attr(14, 'lods_event_restored_count', '', 'R', 'O', NumberDatum(4)),
        Attr(15, 'onu_reactivation_by_lods_events', '', 'R', 'O', NumberDatum(4)),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            threshold_data = None,
        ):
        """ XGPON_TC_PM ME Constructor.

        Args:
            inst : ME instance.
            threshold_data : Attribute #2. .
        """
        super(xgpon_tc_pm_me, self).__init__(inst)
        if threshold_data is not None:
            self.set_attr_value(2, threshold_data)


#################
# ip_host_config_data: IP Host Config Data (9.4.1)
#################



class ip_host_config_data_me(ME):
    """ IP_HOST_CONFIG_DATA (134) - IP Host Config Data (9.4.1). """
    me_class = 134
    name = 'IP_HOST_CONFIG_DATA'
    description = 'IP Host Config Data (9.4.1)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'ip_options', 'Bit map that enables/disables IP-related options', 'RW', 'M', NumberDatum(1)),
        Attr(2, 'mac_addr', 'MAC Address', 'R', 'M', BytesDatum(6)),
        Attr(3, 'onu_id', 'ONU identifier', 'RW', 'M', BytesDatum(25)),
        Attr(4, 'ip_address', '', 'RW', 'M', NumberDatum(4)),
        Attr(5, 'mask', '', 'RW', 'M', NumberDatum(4)),
        Attr(6, 'gateway', '', 'RW', 'M', NumberDatum(4)),
        Attr(7, 'primary_dns', '', 'RW', 'M', NumberDatum(4)),
        Attr(8, 'secondary_dns', '', 'RW', 'M', NumberDatum(4)),
        Attr(9, 'current_address', '', 'R', 'O', NumberDatum(4)),
        Attr(10, 'current_mask', '', 'R', 'O', NumberDatum(4)),
        Attr(11, 'current_gateway', '', 'R', 'O', NumberDatum(4)),
        Attr(12, 'current_primary_dns', '', 'R', 'O', NumberDatum(4)),
        Attr(13, 'current_secondary_dns', '', 'R', 'O', NumberDatum(4)),
        Attr(14, 'domain_name', '', 'R', 'M', BytesDatum(25)),
        Attr(15, 'host_name', '', 'R', 'M', BytesDatum(25)),
        Attr(16, 'relay_agent_options', '', 'RW', 'O', BytesDatum(2)),
    )
    num_attrs = len(attrs)
    actions = ('set', 'get', 'test')

    def __init__(self,
            inst : int,
            ip_options = None,
            onu_id = None,
            ip_address = None,
            mask = None,
            gateway = None,
            primary_dns = None,
            secondary_dns = None,
            relay_agent_options = None
        ):
        """ IP_HOST_CONFIG_DATA ME Constructor.

        Args:
            inst : ME instance.
            ip_options : Attribute #1. Bit map that enables/disables IP-related options.
            onu_id : Attribute #3. ONU identifier.
            ip_address : Attribute #4. .
            mask : Attribute #5. .
            gateway : Attribute #6. .
            primary_dns : Attribute #7. .
            secondary_dns : Attribute #8. .
            relay_agent_options : Attribute #16. .
        """
        super(ip_host_config_data_me, self).__init__(inst)
        if ip_options is not None:
            self.set_attr_value(1, ip_options)
        if onu_id is not None:
            self.set_attr_value(3, onu_id)
        if ip_address is not None:
            self.set_attr_value(4, ip_address)
        if mask is not None:
            self.set_attr_value(5, mask)
        if gateway is not None:
            self.set_attr_value(6, gateway)
        if primary_dns is not None:
            self.set_attr_value(7, primary_dns)
        if secondary_dns is not None:
            self.set_attr_value(8, secondary_dns)
        if relay_agent_options is not None:
            self.set_attr_value(16, relay_agent_options)


#################
# voip_line_status: VoIP Line Status (9.9.11)
#################

voip_line_status_codec = EnumDatum(
    2,
    (
        ('PCMU', 0x0),
        ('GSM', 0x3),
        ('G723', 0x4),
        ('DVI4_8KHZ', 0x5),
        ('DVI4_16KHZ', 0x6),
        ('LPC', 0x7),
        ('PCMA', 0x8),
        ('G722', 0x9),
        ('L16_2CH', 0xa),
        ('L16_1CH', 0xb),
        ('QCELP', 0xc),
        ('CN', 0xd),
        ('MPA', 0xe),
        ('G728', 0xf),
        ('DVI4_11KHZ', 0x10),
        ('DVI4_22KHZ', 0x11),
        ('G729', 0x12),
    )
)

voip_line_status_voice_server_status = EnumDatum(
    1,
    (
        ('NONE', 0x0),
        ('REGISTERED', 0x1),
        ('IN_SESSION', 0x2),
        ('FAILED_REGISTRATION_ICMP_ERROR', 0x3),
        ('FAILED_REGISTRATION_FAILED_TCP', 0x4),
        ('FAILED_REGISTRATION_FAILED_AUTHENTICATION', 0x5),
        ('FAILED_REGISTRATION_TIMEOUT', 0x6),
        ('FAILED_REGISTRATION_SERVER_FAIL_CODE', 0x7),
        ('FAILED_INVITE_ICMP_ERROR', 0x8),
        ('FAILED_INVITE_FAILED_TCP', 0x9),
        ('FAILED_INVITE_FAILED_AUTHENTICATION', 0xa),
        ('FAILED_INVITE_TIMEOUT', 0xb),
        ('FAILED_INVITE_SERVER_FAIL_CODE', 0xc),
        ('PORT_NOT_CONFIGURED', 0xd),
        ('CONFIG_DONE', 0xe),
        ('DISABLED_BY_SWITCH', 0xf),
    )
)

voip_line_status_port_session_type = EnumDatum(
    1,
    (
        ('IDLE', 0x0),
        ('2WAY', 0x1),
        ('3WAY', 0x2),
        ('FAX_MODEM', 0x3),
        ('TELEMETRY', 0x4),
        ('CONFERENCE', 0x5),
    )
)

voip_line_status_line_state = EnumDatum(
    1,
    (
        ('IDLE_ON_HOOK', 0x0),
        ('OFF_HOOK_DIAL_TONE', 0x1),
        ('DIALING', 0x2),
        ('RINGING', 0x3),
        ('AUDIBLE_RINGBACK', 0x4),
        ('CONNECTING', 0x5),
        ('CONNECTED', 0x6),
        ('DISCONNECTING', 0x7),
        ('ROH_NO_TONE', 0x8),
        ('ROH_WITH_TONE', 0x9),
        ('UNKNOWN', 0xa),
    )
)

voip_line_status_emergency_call_status = EnumDatum(
    1,
    (
        ('NOT_IN_PROGRESS', 0x0),
        ('IN_PROGRESS', 0x1),
    )
)



class voip_line_status_me(ME):
    """ VOIP_LINE_STATUS (141) - VoIP Line Status (9.9.11). """
    me_class = 141
    name = 'VOIP_LINE_STATUS'
    description = 'VoIP Line Status (9.9.11)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'codec', 'VoIP codec used', 'R', 'M', voip_line_status_codec),
        Attr(2, 'voice_server_status', 'VoIP server status', 'R', 'M', voip_line_status_voice_server_status),
        Attr(3, 'port_session_type', 'Port Session Type', 'R', 'M', voip_line_status_port_session_type),
        Attr(4, 'call1_packet_period', '', 'R', 'M', NumberDatum(2)),
        Attr(5, 'call2_packet_period', '', 'R', 'M', NumberDatum(2)),
        Attr(6, 'call1_dest_address', '', 'R', 'M', BytesDatum(25)),
        Attr(7, 'call2_dest_address', '', 'R', 'M', BytesDatum(25)),
        Attr(8, 'line_state', 'Port Session Type', 'R', 'O', voip_line_status_line_state),
        Attr(9, 'emergency_call_status', '', 'R', 'O', voip_line_status_emergency_call_status),
    )
    num_attrs = len(attrs)
    actions = ('get')

    def __init__(self,
            inst : int,
        ):
        """ VOIP_LINE_STATUS ME Constructor.

        Args:
            inst : ME instance.
        """
        super(voip_line_status_me, self).__init__(inst)


#################
# voip_media_profile: VoIP Line Status (9.9.11)
#################

voip_media_profile_fax_mode = EnumDatum(
    1,
    (
        ('PASSTHROUGH', 0x0),
        ('T38', 0x1),
    )
)

voip_media_profile_codec_selection1 = EnumDatum(
    1,
    (
        ('PCMU', 0x0),
        ('GSM', 0x3),
        ('G723', 0x4),
        ('DVI4_8KHZ', 0x5),
        ('DVI4_16KHZ', 0x6),
        ('LPC', 0x7),
        ('PCMA', 0x8),
        ('G722', 0x9),
        ('L16_2CH', 0xa),
        ('L16_1CH', 0xb),
        ('QCELP', 0xc),
        ('CN', 0xd),
        ('MPA', 0xe),
        ('G728', 0xf),
        ('DVI4_11KHZ', 0x10),
        ('DVI4_22KHZ', 0x11),
        ('G729', 0x12),
    )
)



class voip_media_profile_me(ME):
    """ VOIP_MEDIA_PROFILE (142) - VoIP Line Status (9.9.11). """
    me_class = 142
    name = 'VOIP_MEDIA_PROFILE'
    description = 'VoIP Line Status (9.9.11)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'fax_mode', '', 'RWC', 'M', voip_media_profile_fax_mode),
        Attr(2, 'voice_service_prof_ptr', '', 'RWC', 'M', NumberDatum(2)),
        Attr(3, 'codec_selection1', '', 'RWC', 'M', voip_media_profile_codec_selection1),
        Attr(4, 'packet_period1', '', 'RWC', 'M', NumberDatum(1)),
        Attr(5, 'silence_supression1', '', 'RWC', 'M', NumberDatum(1)),
        Attr(6, 'codec_selection2', '', 'RWC', 'M', NumberDatum(1)),
        Attr(7, 'packet_period2', '', 'RWC', 'M', NumberDatum(1)),
        Attr(8, 'silence_supression2', '', 'RWC', 'M', NumberDatum(1)),
        Attr(9, 'codec_selection3', '', 'RWC', 'M', NumberDatum(1)),
        Attr(10, 'packet_period3', '', 'RWC', 'M', NumberDatum(1)),
        Attr(11, 'silence_supression3', '', 'RWC', 'M', NumberDatum(1)),
        Attr(12, 'codec_selection4', '', 'RWC', 'M', NumberDatum(1)),
        Attr(13, 'packet_period4', '', 'RWC', 'M', NumberDatum(1)),
        Attr(14, 'silence_supression4', '', 'RWC', 'M', NumberDatum(1)),
        Attr(15, 'oob_dtmf', '', 'RWC', 'M', NumberDatum(1)),
        Attr(16, 'rtp_profile_ptr', '', 'RWC', 'M', NumberDatum(2)),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            fax_mode = None,
            voice_service_prof_ptr = None,
            codec_selection1 = None,
            packet_period1 = None,
            silence_supression1 = None,
            codec_selection2 = None,
            packet_period2 = None,
            silence_supression2 = None,
            codec_selection3 = None,
            packet_period3 = None,
            silence_supression3 = None,
            codec_selection4 = None,
            packet_period4 = None,
            silence_supression4 = None,
            oob_dtmf = None,
            rtp_profile_ptr = None
        ):
        """ VOIP_MEDIA_PROFILE ME Constructor.

        Args:
            inst : ME instance.
            fax_mode : Attribute #1. .
            voice_service_prof_ptr : Attribute #2. .
            codec_selection1 : Attribute #3. .
            packet_period1 : Attribute #4. .
            silence_supression1 : Attribute #5. .
            codec_selection2 : Attribute #6. .
            packet_period2 : Attribute #7. .
            silence_supression2 : Attribute #8. .
            codec_selection3 : Attribute #9. .
            packet_period3 : Attribute #10. .
            silence_supression3 : Attribute #11. .
            codec_selection4 : Attribute #12. .
            packet_period4 : Attribute #13. .
            silence_supression4 : Attribute #14. .
            oob_dtmf : Attribute #15. .
            rtp_profile_ptr : Attribute #16. .
        """
        super(voip_media_profile_me, self).__init__(inst)
        if fax_mode is not None:
            self.set_attr_value(1, fax_mode)
        if voice_service_prof_ptr is not None:
            self.set_attr_value(2, voice_service_prof_ptr)
        if codec_selection1 is not None:
            self.set_attr_value(3, codec_selection1)
        if packet_period1 is not None:
            self.set_attr_value(4, packet_period1)
        if silence_supression1 is not None:
            self.set_attr_value(5, silence_supression1)
        if codec_selection2 is not None:
            self.set_attr_value(6, codec_selection2)
        if packet_period2 is not None:
            self.set_attr_value(7, packet_period2)
        if silence_supression2 is not None:
            self.set_attr_value(8, silence_supression2)
        if codec_selection3 is not None:
            self.set_attr_value(9, codec_selection3)
        if packet_period3 is not None:
            self.set_attr_value(10, packet_period3)
        if silence_supression3 is not None:
            self.set_attr_value(11, silence_supression3)
        if codec_selection4 is not None:
            self.set_attr_value(12, codec_selection4)
        if packet_period4 is not None:
            self.set_attr_value(13, packet_period4)
        if silence_supression4 is not None:
            self.set_attr_value(14, silence_supression4)
        if oob_dtmf is not None:
            self.set_attr_value(15, oob_dtmf)
        if rtp_profile_ptr is not None:
            self.set_attr_value(16, rtp_profile_ptr)


#################
# sip_user_data: SIP User Data (9.9.2)
#################



class sip_user_data_me(ME):
    """ SIP_USER_DATA (153) - SIP User Data (9.9.2). """
    me_class = 153
    name = 'SIP_USER_DATA'
    description = 'SIP User Data (9.9.2)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'sip_agent_ptr', '', 'RWC', 'M', NumberDatum(2)),
        Attr(2, 'user_part_aor', '', 'RWC', 'M', NumberDatum(2)),
        Attr(3, 'sip_display_name', '', 'RW', 'M', BytesDatum(25)),
        Attr(4, 'username_password', '', 'RWC', 'M', NumberDatum(2)),
        Attr(5, 'voicemail_server_uri', '', 'RWC', 'M', NumberDatum(2)),
        Attr(6, 'voicemail_subscription_exp_time', '', 'RWC', 'M', NumberDatum(4)),
        Attr(7, 'network_dial_plan_ptr', '', 'RWC', 'M', NumberDatum(2)),
        Attr(8, 'app_service_prof_ptr', '', 'RWC', 'M', NumberDatum(2)),
        Attr(9, 'feature_code_ptr', '', 'RWC', 'M', NumberDatum(2)),
        Attr(10, 'pptp_ptr', '', 'RWC', 'M', NumberDatum(2)),
        Attr(11, 'release_timer', '', 'RWC', 'M', NumberDatum(1)),
        Attr(12, 'roh_timer', '', 'RWC', 'M', NumberDatum(1)),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            sip_agent_ptr = None,
            user_part_aor = None,
            sip_display_name = None,
            username_password = None,
            voicemail_server_uri = None,
            voicemail_subscription_exp_time = None,
            network_dial_plan_ptr = None,
            app_service_prof_ptr = None,
            feature_code_ptr = None,
            pptp_ptr = None,
            release_timer = None,
            roh_timer = None
        ):
        """ SIP_USER_DATA ME Constructor.

        Args:
            inst : ME instance.
            sip_agent_ptr : Attribute #1. .
            user_part_aor : Attribute #2. .
            sip_display_name : Attribute #3. .
            username_password : Attribute #4. .
            voicemail_server_uri : Attribute #5. .
            voicemail_subscription_exp_time : Attribute #6. .
            network_dial_plan_ptr : Attribute #7. .
            app_service_prof_ptr : Attribute #8. .
            feature_code_ptr : Attribute #9. .
            pptp_ptr : Attribute #10. .
            release_timer : Attribute #11. .
            roh_timer : Attribute #12. .
        """
        super(sip_user_data_me, self).__init__(inst)
        if sip_agent_ptr is not None:
            self.set_attr_value(1, sip_agent_ptr)
        if user_part_aor is not None:
            self.set_attr_value(2, user_part_aor)
        if sip_display_name is not None:
            self.set_attr_value(3, sip_display_name)
        if username_password is not None:
            self.set_attr_value(4, username_password)
        if voicemail_server_uri is not None:
            self.set_attr_value(5, voicemail_server_uri)
        if voicemail_subscription_exp_time is not None:
            self.set_attr_value(6, voicemail_subscription_exp_time)
        if network_dial_plan_ptr is not None:
            self.set_attr_value(7, network_dial_plan_ptr)
        if app_service_prof_ptr is not None:
            self.set_attr_value(8, app_service_prof_ptr)
        if feature_code_ptr is not None:
            self.set_attr_value(9, feature_code_ptr)
        if pptp_ptr is not None:
            self.set_attr_value(10, pptp_ptr)
        if release_timer is not None:
            self.set_attr_value(11, release_timer)
        if roh_timer is not None:
            self.set_attr_value(12, roh_timer)


#################
# sip_agent_config_data: SIP Agent Config Data (9.9.3)
#################

sip_agent_config_data_sip_status = EnumDatum(
    1,
    (
        ('OK', 0x0),
        ('CONNECTED', 0x1),
        ('FAILED_ICMP_ERROR', 0x2),
        ('FAILED_MALFORMED_RESPONSE', 0x3),
        ('FAILED_INADEQUATE_INFO_RESPONSE', 0x4),
        ('FAILED_TIMEOUT', 0x5),
        ('REDUNDANT_OFFLINE', 0x6),
    )
)

sip_agent_config_data_sip_transmit_control = EnumDatum(
    1,
    (
        ('ENABLED', 0x1),
        ('DISABLED', 0x0),
    )
)

sip_agent_config_data_sip_uri_format = EnumDatum(
    1,
    (
        ('TEL_URI', 0x0),
        ('SIP_URI', 0x1),
    )
)




class sip_agent_config_data_sip_response_table(StructDatum):
    fields = (
        StructField('response_code', '', field_type=NumberDatum(2)),
        StructField('tone', '', field_type=NumberDatum(1)),
        StructField('text_message', '', field_type=NumberDatum(2)),
    )
    def __init__(self, default: AttrValue = None, fixed: AttrValue = None, size = 5):
        super().__init__(size, default=default, fixed=fixed)

class sip_agent_config_data_me(ME):
    """ SIP_AGENT_CONFIG_DATA (150) - SIP Agent Config Data (9.9.3). """
    me_class = 150
    name = 'SIP_AGENT_CONFIG_DATA'
    description = 'SIP Agent Config Data (9.9.3)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'proxy_server_addr_ptr', '', 'RWC', 'M', NumberDatum(2)),
        Attr(2, 'outbound_proxy_addr_ptr', '', 'RWC', 'M', NumberDatum(2)),
        Attr(3, 'primary_sip_dns', '', 'RWC', 'M', NumberDatum(4)),
        Attr(4, 'secondary_sip_dns', '', 'RWC', 'M', NumberDatum(4)),
        Attr(5, 'tcp_udp_ptr', '', 'RW', 'M', NumberDatum(2)),
        Attr(6, 'sip_reg_exp_time', '', 'RW', 'M', NumberDatum(4)),
        Attr(7, 'sip_rereg_head_start_time', '', 'RW', 'M', NumberDatum(4)),
        Attr(8, 'host_part_uri', '', 'RWC', 'M', NumberDatum(2)),
        Attr(9, 'sip_status', '', 'R', 'M', sip_agent_config_data_sip_status),
        Attr(10, 'sip_registrar', '', 'RWC', 'M', NumberDatum(2)),
        Attr(11, 'softswitch', '', 'RWC', 'M', NumberDatum(4)),
        Attr(12, 'sip_response_table', '', 'RW', 'O', sip_agent_config_data_sip_response_table()),
        Attr(13, 'sip_transmit_control', '', 'RWC', 'O', sip_agent_config_data_sip_transmit_control),
        Attr(14, 'sip_uri_format', '', 'RWC', 'O', sip_agent_config_data_sip_uri_format),
        Attr(15, 'redundant_sip_agent_ptr', '', 'RW', 'O', NumberDatum(2)),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            proxy_server_addr_ptr = None,
            outbound_proxy_addr_ptr = None,
            primary_sip_dns = None,
            secondary_sip_dns = None,
            tcp_udp_ptr = None,
            sip_reg_exp_time = None,
            sip_rereg_head_start_time = None,
            host_part_uri = None,
            sip_registrar = None,
            softswitch = None,
            sip_response_table = None,
            sip_transmit_control = None,
            sip_uri_format = None,
            redundant_sip_agent_ptr = None
        ):
        """ SIP_AGENT_CONFIG_DATA ME Constructor.

        Args:
            inst : ME instance.
            proxy_server_addr_ptr : Attribute #1. .
            outbound_proxy_addr_ptr : Attribute #2. .
            primary_sip_dns : Attribute #3. .
            secondary_sip_dns : Attribute #4. .
            tcp_udp_ptr : Attribute #5. .
            sip_reg_exp_time : Attribute #6. .
            sip_rereg_head_start_time : Attribute #7. .
            host_part_uri : Attribute #8. .
            sip_registrar : Attribute #10. .
            softswitch : Attribute #11. .
            sip_response_table : Attribute #12. .
            sip_transmit_control : Attribute #13. .
            sip_uri_format : Attribute #14. .
            redundant_sip_agent_ptr : Attribute #15. .
        """
        super(sip_agent_config_data_me, self).__init__(inst)
        if proxy_server_addr_ptr is not None:
            self.set_attr_value(1, proxy_server_addr_ptr)
        if outbound_proxy_addr_ptr is not None:
            self.set_attr_value(2, outbound_proxy_addr_ptr)
        if primary_sip_dns is not None:
            self.set_attr_value(3, primary_sip_dns)
        if secondary_sip_dns is not None:
            self.set_attr_value(4, secondary_sip_dns)
        if tcp_udp_ptr is not None:
            self.set_attr_value(5, tcp_udp_ptr)
        if sip_reg_exp_time is not None:
            self.set_attr_value(6, sip_reg_exp_time)
        if sip_rereg_head_start_time is not None:
            self.set_attr_value(7, sip_rereg_head_start_time)
        if host_part_uri is not None:
            self.set_attr_value(8, host_part_uri)
        if sip_registrar is not None:
            self.set_attr_value(10, sip_registrar)
        if softswitch is not None:
            self.set_attr_value(11, softswitch)
        if sip_response_table is not None:
            self.set_attr_value(12, sip_response_table)
        if sip_transmit_control is not None:
            self.set_attr_value(13, sip_transmit_control)
        if sip_uri_format is not None:
            self.set_attr_value(14, sip_uri_format)
        if redundant_sip_agent_ptr is not None:
            self.set_attr_value(15, redundant_sip_agent_ptr)


#################
# network_address: Network Address (9.12.3)
#################



class network_address_me(ME):
    """ NETWORK_ADDRESS (137) - Network Address (9.12.3). """
    me_class = 137
    name = 'NETWORK_ADDRESS'
    description = 'Network Address (9.12.3)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'security_ptr', '', 'RWC', 'M', NumberDatum(2)),
        Attr(2, 'address_ptr', '', 'RWC', 'M', NumberDatum(2)),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            security_ptr = None,
            address_ptr = None
        ):
        """ NETWORK_ADDRESS ME Constructor.

        Args:
            inst : ME instance.
            security_ptr : Attribute #1. .
            address_ptr : Attribute #2. .
        """
        super(network_address_me, self).__init__(inst)
        if security_ptr is not None:
            self.set_attr_value(1, security_ptr)
        if address_ptr is not None:
            self.set_attr_value(2, address_ptr)


#################
# large_string: Large String (9.12.5)
#################



class large_string_me(ME):
    """ LARGE_STRING (157) - Large String (9.12.5). """
    me_class = 157
    name = 'LARGE_STRING'
    description = 'Large String (9.12.5)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'number_of_parts', '', 'RW', 'M', NumberDatum(1)),
        Attr(2, 'part1', '', 'RW', 'M', BytesDatum(25)),
        Attr(3, 'part2', '', 'RW', 'M', BytesDatum(25)),
        Attr(4, 'part3', '', 'RW', 'M', BytesDatum(25)),
        Attr(5, 'part4', '', 'RW', 'M', BytesDatum(25)),
        Attr(6, 'part5', '', 'RW', 'M', BytesDatum(25)),
        Attr(7, 'part6', '', 'RW', 'M', BytesDatum(25)),
        Attr(8, 'part7', '', 'RW', 'M', BytesDatum(25)),
        Attr(9, 'part8', '', 'RW', 'M', BytesDatum(25)),
        Attr(10, 'part9', '', 'RW', 'M', BytesDatum(25)),
        Attr(11, 'part10', '', 'RW', 'M', BytesDatum(25)),
        Attr(12, 'part11', '', 'RW', 'M', BytesDatum(25)),
        Attr(13, 'part12', '', 'RW', 'M', BytesDatum(25)),
        Attr(14, 'part13', '', 'RW', 'M', BytesDatum(25)),
        Attr(15, 'part14', '', 'RW', 'M', BytesDatum(25)),
        Attr(16, 'part15', '', 'RW', 'M', BytesDatum(25)),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            number_of_parts = None,
            part1 = None,
            part2 = None,
            part3 = None,
            part4 = None,
            part5 = None,
            part6 = None,
            part7 = None,
            part8 = None,
            part9 = None,
            part10 = None,
            part11 = None,
            part12 = None,
            part13 = None,
            part14 = None,
            part15 = None
        ):
        """ LARGE_STRING ME Constructor.

        Args:
            inst : ME instance.
            number_of_parts : Attribute #1. .
            part1 : Attribute #2. .
            part2 : Attribute #3. .
            part3 : Attribute #4. .
            part4 : Attribute #5. .
            part5 : Attribute #6. .
            part6 : Attribute #7. .
            part7 : Attribute #8. .
            part8 : Attribute #9. .
            part9 : Attribute #10. .
            part10 : Attribute #11. .
            part11 : Attribute #12. .
            part12 : Attribute #13. .
            part13 : Attribute #14. .
            part14 : Attribute #15. .
            part15 : Attribute #16. .
        """
        super(large_string_me, self).__init__(inst)
        if number_of_parts is not None:
            self.set_attr_value(1, number_of_parts)
        if part1 is not None:
            self.set_attr_value(2, part1)
        if part2 is not None:
            self.set_attr_value(3, part2)
        if part3 is not None:
            self.set_attr_value(4, part3)
        if part4 is not None:
            self.set_attr_value(5, part4)
        if part5 is not None:
            self.set_attr_value(6, part5)
        if part6 is not None:
            self.set_attr_value(7, part6)
        if part7 is not None:
            self.set_attr_value(8, part7)
        if part8 is not None:
            self.set_attr_value(9, part8)
        if part9 is not None:
            self.set_attr_value(10, part9)
        if part10 is not None:
            self.set_attr_value(11, part10)
        if part11 is not None:
            self.set_attr_value(12, part11)
        if part12 is not None:
            self.set_attr_value(13, part12)
        if part13 is not None:
            self.set_attr_value(14, part13)
        if part14 is not None:
            self.set_attr_value(15, part14)
        if part15 is not None:
            self.set_attr_value(16, part15)


#################
# authentication_security_method: Authentication Security Method (9.12.4)
#################

authentication_security_method_validation_scheme = EnumDatum(
    1,
    (
        ('DISABLED', 0x0),
        ('MD5', 0x1),
        ('BASIC', 0x3),
    )
)



class authentication_security_method_me(ME):
    """ AUTHENTICATION_SECURITY_METHOD (148) - Authentication Security Method (9.12.4). """
    me_class = 148
    name = 'AUTHENTICATION_SECURITY_METHOD'
    description = 'Authentication Security Method (9.12.4)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'validation_scheme', '', 'RW', 'M', authentication_security_method_validation_scheme),
        Attr(2, 'username1', '', 'RW', 'M', BytesDatum(25)),
        Attr(3, 'password', '', 'RW', 'M', BytesDatum(25)),
        Attr(4, 'realm', '', 'RW', 'M', BytesDatum(25)),
        Attr(5, 'username2', '', 'RW', 'O', BytesDatum(25)),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            validation_scheme = None,
            username1 = None,
            password = None,
            realm = None,
            username2 = None
        ):
        """ AUTHENTICATION_SECURITY_METHOD ME Constructor.

        Args:
            inst : ME instance.
            validation_scheme : Attribute #1. .
            username1 : Attribute #2. .
            password : Attribute #3. .
            realm : Attribute #4. .
            username2 : Attribute #5. .
        """
        super(authentication_security_method_me, self).__init__(inst)
        if validation_scheme is not None:
            self.set_attr_value(1, validation_scheme)
        if username1 is not None:
            self.set_attr_value(2, username1)
        if password is not None:
            self.set_attr_value(3, password)
        if realm is not None:
            self.set_attr_value(4, realm)
        if username2 is not None:
            self.set_attr_value(5, username2)


#################
# voice_service_profile: Voice Service Profile (9.9.6)
#################

voice_service_profile_announcement_type = EnumDatum(
    1,
    (
        ('SILENCE', 0x1),
        ('REORDER_TONE', 0x2),
        ('FAST_BUSY', 0x3),
        ('VOICE_ANNOUNCEMENT', 0x4),
        ('UNSPECIFIED', 0xff),
    )
)

voice_service_profile_echo_cancel = EnumDatum(
    1,
    (
        ('ENABLED', 0x1),
        ('DISABLED', 0x0),
    )
)




class voice_service_profile_tone_pattern_table(StructDatum):
    fields = (
        StructField('index', '', field_type=NumberDatum(1)),
        StructField('tone_on', '', field_type=NumberDatum(1)),
        StructField('frequency1', '', field_type=NumberDatum(2)),
        StructField('power1', '', field_type=NumberDatum(1)),
        StructField('frequency2', '', field_type=NumberDatum(2)),
        StructField('power2', '', field_type=NumberDatum(1)),
        StructField('frequency3', '', field_type=NumberDatum(2)),
        StructField('power3', '', field_type=NumberDatum(1)),
        StructField('frequency4', '', field_type=NumberDatum(2)),
        StructField('power4', '', field_type=NumberDatum(1)),
        StructField('modulation_frequency', '', field_type=NumberDatum(2)),
        StructField('modulation_power', '', field_type=NumberDatum(1)),
        StructField('duration', '', field_type=NumberDatum(2)),
        StructField('next_entry', '', field_type=NumberDatum(1)),
    )
    def __init__(self, default: AttrValue = None, fixed: AttrValue = None, size = 20):
        super().__init__(size, default=default, fixed=fixed)


class voice_service_profile_tone_event_table(StructDatum):
    fields = (
        StructField('event', '', field_type=NumberDatum(1)),
        StructField('tone_pattern', '', field_type=NumberDatum(1)),
        StructField('tone_file', '', field_type=NumberDatum(2)),
        StructField('tone_file_repetitions', '', field_type=NumberDatum(1)),
        StructField('reserved', '', field_type=NumberDatum(2)),
    )
    def __init__(self, default: AttrValue = None, fixed: AttrValue = None, size = 7):
        super().__init__(size, default=default, fixed=fixed)


class voice_service_profile_ringing_pattern_table(StructDatum):
    fields = (
        StructField('index', '', field_type=NumberDatum(1)),
        StructField('ringing_on', '', field_type=NumberDatum(1)),
        StructField('duration', '', field_type=NumberDatum(2)),
        StructField('next_entry', '', field_type=NumberDatum(1)),
    )
    def __init__(self, default: AttrValue = None, fixed: AttrValue = None, size = 5):
        super().__init__(size, default=default, fixed=fixed)


class voice_service_profile_ringing_event_table(StructDatum):
    fields = (
        StructField('event', '', field_type=NumberDatum(1)),
        StructField('ringing_pattern', '', field_type=NumberDatum(1)),
        StructField('ringing_file', '', field_type=NumberDatum(2)),
        StructField('ringing_file_repetitions', '', field_type=NumberDatum(1)),
        StructField('ringing_text', '', field_type=NumberDatum(2)),
    )
    def __init__(self, default: AttrValue = None, fixed: AttrValue = None, size = 7):
        super().__init__(size, default=default, fixed=fixed)

class voice_service_profile_me(ME):
    """ VOICE_SERVICE_PROFILE (58) - Voice Service Profile (9.9.6). """
    me_class = 58
    name = 'VOICE_SERVICE_PROFILE'
    description = 'Voice Service Profile (9.9.6)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'announcement_type', '', 'RWC', 'M', voice_service_profile_announcement_type),
        Attr(2, 'jitter_target', '', 'RWC', 'O', NumberDatum(2)),
        Attr(3, 'jitter_buffer_max', '', 'RWC', 'O', NumberDatum(2)),
        Attr(4, 'echo_cancel', '', 'RWC', 'M', voice_service_profile_echo_cancel),
        Attr(5, 'pstn_protocol_variant', '', 'RWC', 'O', NumberDatum(2)),
        Attr(6, 'dtmf_digit_levels', '', 'RWC', 'O', NumberDatum(2)),
        Attr(7, 'dtmf_digit_duration', '', 'RWC', 'O', NumberDatum(2)),
        Attr(8, 'hook_flash_min_time', '', 'RWC', 'O', NumberDatum(2)),
        Attr(9, 'hook_flash_max_time', '', 'RWC', 'O', NumberDatum(2)),
        Attr(10, 'tone_pattern_table', '', 'RW', 'O', voice_service_profile_tone_pattern_table()),
        Attr(11, 'tone_event_table', '', 'RW', 'O', voice_service_profile_tone_event_table()),
        Attr(12, 'ringing_pattern_table', '', 'RW', 'O', voice_service_profile_ringing_pattern_table()),
        Attr(13, 'ringing_event_table', '', 'RW', 'O', voice_service_profile_ringing_event_table()),
        Attr(14, 'network_specific_ext_ptr', '', 'RWC', 'O', NumberDatum(2)),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            announcement_type = None,
            jitter_target = None,
            jitter_buffer_max = None,
            echo_cancel = None,
            pstn_protocol_variant = None,
            dtmf_digit_levels = None,
            dtmf_digit_duration = None,
            hook_flash_min_time = None,
            hook_flash_max_time = None,
            tone_pattern_table = None,
            tone_event_table = None,
            ringing_pattern_table = None,
            ringing_event_table = None,
            network_specific_ext_ptr = None
        ):
        """ VOICE_SERVICE_PROFILE ME Constructor.

        Args:
            inst : ME instance.
            announcement_type : Attribute #1. .
            jitter_target : Attribute #2. .
            jitter_buffer_max : Attribute #3. .
            echo_cancel : Attribute #4. .
            pstn_protocol_variant : Attribute #5. .
            dtmf_digit_levels : Attribute #6. .
            dtmf_digit_duration : Attribute #7. .
            hook_flash_min_time : Attribute #8. .
            hook_flash_max_time : Attribute #9. .
            tone_pattern_table : Attribute #10. .
            tone_event_table : Attribute #11. .
            ringing_pattern_table : Attribute #12. .
            ringing_event_table : Attribute #13. .
            network_specific_ext_ptr : Attribute #14. .
        """
        super(voice_service_profile_me, self).__init__(inst)
        if announcement_type is not None:
            self.set_attr_value(1, announcement_type)
        if jitter_target is not None:
            self.set_attr_value(2, jitter_target)
        if jitter_buffer_max is not None:
            self.set_attr_value(3, jitter_buffer_max)
        if echo_cancel is not None:
            self.set_attr_value(4, echo_cancel)
        if pstn_protocol_variant is not None:
            self.set_attr_value(5, pstn_protocol_variant)
        if dtmf_digit_levels is not None:
            self.set_attr_value(6, dtmf_digit_levels)
        if dtmf_digit_duration is not None:
            self.set_attr_value(7, dtmf_digit_duration)
        if hook_flash_min_time is not None:
            self.set_attr_value(8, hook_flash_min_time)
        if hook_flash_max_time is not None:
            self.set_attr_value(9, hook_flash_max_time)
        if tone_pattern_table is not None:
            self.set_attr_value(10, tone_pattern_table)
        if tone_event_table is not None:
            self.set_attr_value(11, tone_event_table)
        if ringing_pattern_table is not None:
            self.set_attr_value(12, ringing_pattern_table)
        if ringing_event_table is not None:
            self.set_attr_value(13, ringing_event_table)
        if network_specific_ext_ptr is not None:
            self.set_attr_value(14, network_specific_ext_ptr)


#################
# voip_config_data: VoIP config data (9.9.18)
#################

voip_config_data_available_signalling_protocols = EnumDatum(
    1,
    (
        ('SIP', 0x1),
        ('H248', 0x2),
        ('MGCP', 0x3),
    )
)

voip_config_data_signalling_protocol_used = EnumDatum(
    1,
    (
        ('SIP', 0x1),
        ('H248', 0x2),
        ('MGCP', 0x3),
        ('NON_OMCI', 0xff),
    )
)

voip_config_data_available_voip_config_methods = EnumDatum(
    4,
    (
        ('OMCI', 0x1),
        ('CONFIG_FILE', 0x2),
        ('TR069', 0x3),
        ('SIP', 0x4),
    )
)

voip_config_data_voip_config_method_used = EnumDatum(
    1,
    (
        ('OMCI', 0x1),
        ('CONFIG_FILE', 0x2),
        ('TR069', 0x3),
        ('SIP', 0x4),
    )
)

voip_config_data_voip_config_state = EnumDatum(
    1,
    (
        ('INACTIVE', 0x0),
        ('ACTIVE', 0x1),
        ('INITIALIZING', 0x2),
        ('FAULT', 0x3),
    )
)



class voip_config_data_me(ME):
    """ VOIP_CONFIG_DATA (138) - VoIP config data (9.9.18). """
    me_class = 138
    name = 'VOIP_CONFIG_DATA'
    description = 'VoIP config data (9.9.18)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'available_signalling_protocols', '', 'R', 'M', voip_config_data_available_signalling_protocols),
        Attr(2, 'signalling_protocol_used', '', 'RW', 'M', voip_config_data_signalling_protocol_used),
        Attr(3, 'available_voip_config_methods', '', 'R', 'M', voip_config_data_available_voip_config_methods),
        Attr(4, 'voip_config_method_used', '', 'RW', 'M', voip_config_data_voip_config_method_used),
        Attr(5, 'voice_config_ptr', '', 'RW', 'M', NumberDatum(2)),
        Attr(6, 'voip_config_state', '', 'R', 'M', voip_config_data_voip_config_state),
        Attr(7, 'retrieve_profile', '', 'W', 'M', NumberDatum(1)),
        Attr(8, 'profile_version', '', 'R', 'M', BytesDatum(25)),
    )
    num_attrs = len(attrs)
    actions = ('set', 'get')

    def __init__(self,
            inst : int,
            signalling_protocol_used = None,
            voip_config_method_used = None,
            voice_config_ptr = None,
            retrieve_profile = None,
        ):
        """ VOIP_CONFIG_DATA ME Constructor.

        Args:
            inst : ME instance.
            signalling_protocol_used : Attribute #2. .
            voip_config_method_used : Attribute #4. .
            voice_config_ptr : Attribute #5. .
            retrieve_profile : Attribute #7. .
        """
        super(voip_config_data_me, self).__init__(inst)
        if signalling_protocol_used is not None:
            self.set_attr_value(2, signalling_protocol_used)
        if voip_config_method_used is not None:
            self.set_attr_value(4, voip_config_method_used)
        if voice_config_ptr is not None:
            self.set_attr_value(5, voice_config_ptr)
        if retrieve_profile is not None:
            self.set_attr_value(7, retrieve_profile)


#################
# voip_voice_ctp: VoIP voice CTP (9.9.4)
#################

voip_voice_ctp_signalling_code = EnumDatum(
    1,
    (
        ('LOOP_START', 0x1),
        ('GROUND_START', 0x2),
        ('LOOP_REVERSE_BATTERY', 0x3),
        ('COIN_FIRST', 0x4),
        ('DIAL_TONE_FIRST', 0x5),
        ('MULTI_PARTY', 0x6),
    )
)



class voip_voice_ctp_me(ME):
    """ VOIP_VOICE_CTP (139) - VoIP voice CTP (9.9.4). """
    me_class = 139
    name = 'VOIP_VOICE_CTP'
    description = 'VoIP voice CTP (9.9.4)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'user_protocol_ptr', '', 'RWC', 'M', NumberDatum(2)),
        Attr(2, 'pptp_ptr', '', 'RWC', 'M', NumberDatum(2)),
        Attr(3, 'voice_media_profile_ptr', '', 'RWC', 'M', NumberDatum(2)),
        Attr(4, 'signalling_code', '', 'RWC', 'M', voip_voice_ctp_signalling_code),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            user_protocol_ptr = None,
            pptp_ptr = None,
            voice_media_profile_ptr = None,
            signalling_code = None
        ):
        """ VOIP_VOICE_CTP ME Constructor.

        Args:
            inst : ME instance.
            user_protocol_ptr : Attribute #1. .
            pptp_ptr : Attribute #2. .
            voice_media_profile_ptr : Attribute #3. .
            signalling_code : Attribute #4. .
        """
        super(voip_voice_ctp_me, self).__init__(inst)
        if user_protocol_ptr is not None:
            self.set_attr_value(1, user_protocol_ptr)
        if pptp_ptr is not None:
            self.set_attr_value(2, pptp_ptr)
        if voice_media_profile_ptr is not None:
            self.set_attr_value(3, voice_media_profile_ptr)
        if signalling_code is not None:
            self.set_attr_value(4, signalling_code)


#################
# tcp_udp_config_data: TCP/UDP config data (9.4.3)
#################



class tcp_udp_config_data_me(ME):
    """ TCP_UDP_CONFIG_DATA (136) - TCP/UDP config data (9.4.3). """
    me_class = 136
    name = 'TCP_UDP_CONFIG_DATA'
    description = 'TCP/UDP config data (9.4.3)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'port_id', '', 'RWC', 'M', NumberDatum(2)),
        Attr(2, 'protocol', '', 'RWC', 'M', NumberDatum(1)),
        Attr(3, 'tos', '', 'RWC', 'M', NumberDatum(1)),
        Attr(4, 'ip_host_ptr', '', 'RWC', 'M', NumberDatum(2)),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            port_id = None,
            protocol = None,
            tos = None,
            ip_host_ptr = None
        ):
        """ TCP_UDP_CONFIG_DATA ME Constructor.

        Args:
            inst : ME instance.
            port_id : Attribute #1. .
            protocol : Attribute #2. .
            tos : Attribute #3. .
            ip_host_ptr : Attribute #4. .
        """
        super(tcp_udp_config_data_me, self).__init__(inst)
        if port_id is not None:
            self.set_attr_value(1, port_id)
        if protocol is not None:
            self.set_attr_value(2, protocol)
        if tos is not None:
            self.set_attr_value(3, tos)
        if ip_host_ptr is not None:
            self.set_attr_value(4, ip_host_ptr)


#################
# network_dial_plan_table: Network dial plan table (9.9.10)
#################

network_dial_plan_table_dial_plan_format = EnumDatum(
    1,
    (
        ('UNDEFINED', 0x0),
        ('H248', 0x1),
        ('MGCP', 0x2),
        ('VENDOR', 0x3),
    )
)




class network_dial_plan_table_dial_plan_table(StructDatum):
    fields = (
        StructField('dial_plan_id', '', field_type=NumberDatum(1)),
        StructField('action', '', field_type=NumberDatum(1)),
        StructField('dial_plan_token', '', field_type=BytesDatum(28)),
    )
    def __init__(self, default: AttrValue = None, fixed: AttrValue = None, size = 30):
        super().__init__(size, default=default, fixed=fixed)

class network_dial_plan_table_me(ME):
    """ NETWORK_DIAL_PLAN_TABLE (145) - Network dial plan table (9.9.10). """
    me_class = 145
    name = 'NETWORK_DIAL_PLAN_TABLE'
    description = 'Network dial plan table (9.9.10)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'dial_plan_number', '', 'R', 'M', NumberDatum(2)),
        Attr(2, 'dial_plan_table_max_size', '', 'RC', 'M', NumberDatum(2)),
        Attr(3, 'critical_dial_timeout', '', 'RWC', 'M', NumberDatum(2)),
        Attr(4, 'partial_dial_timeout', '', 'RWC', 'M', NumberDatum(2)),
        Attr(5, 'dial_plan_format', '', 'RWC', 'M', network_dial_plan_table_dial_plan_format),
        Attr(6, 'dial_plan_table', 'Dial plan table', 'RW', 'M', network_dial_plan_table_dial_plan_table()),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get', 'get_next')

    def __init__(self,
            inst : int,
            dial_plan_table_max_size = None,
            critical_dial_timeout = None,
            partial_dial_timeout = None,
            dial_plan_format = None,
            dial_plan_table = None
        ):
        """ NETWORK_DIAL_PLAN_TABLE ME Constructor.

        Args:
            inst : ME instance.
            dial_plan_table_max_size : Attribute #2. .
            critical_dial_timeout : Attribute #3. .
            partial_dial_timeout : Attribute #4. .
            dial_plan_format : Attribute #5. .
            dial_plan_table : Attribute #6. Dial plan table.
        """
        super(network_dial_plan_table_me, self).__init__(inst)
        if dial_plan_table_max_size is not None:
            self.set_attr_value(2, dial_plan_table_max_size)
        if critical_dial_timeout is not None:
            self.set_attr_value(3, critical_dial_timeout)
        if partial_dial_timeout is not None:
            self.set_attr_value(4, partial_dial_timeout)
        if dial_plan_format is not None:
            self.set_attr_value(5, dial_plan_format)
        if dial_plan_table is not None:
            self.set_attr_value(6, dial_plan_table)


#################
# rtp_profile_data: RTP profile data (9.9.7)
#################



class rtp_profile_data_me(ME):
    """ RTP_PROFILE_DATA (143) - RTP profile data (9.9.7). """
    me_class = 143
    name = 'RTP_PROFILE_DATA'
    description = 'RTP profile data (9.9.7)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'local_port_min', '', 'RWC', 'M', NumberDatum(2)),
        Attr(2, 'local_port_max', '', 'RWC', 'O', NumberDatum(2)),
        Attr(3, 'dscp_mark', '', 'RWC', 'M', NumberDatum(1)),
        Attr(4, 'piggyback_events', '', 'RWC', 'M', NumberDatum(1)),
        Attr(5, 'tone_events', '', 'RWC', 'M', NumberDatum(1)),
        Attr(6, 'dtmf_events', '', 'RWC', 'M', NumberDatum(1)),
        Attr(7, 'cas_events', '', 'RWC', 'M', NumberDatum(1)),
        Attr(8, 'ip_host_config_ptr', '', 'RW', 'O', NumberDatum(2)),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            local_port_min = None,
            local_port_max = None,
            dscp_mark = None,
            piggyback_events = None,
            tone_events = None,
            dtmf_events = None,
            cas_events = None,
            ip_host_config_ptr = None
        ):
        """ RTP_PROFILE_DATA ME Constructor.

        Args:
            inst : ME instance.
            local_port_min : Attribute #1. .
            local_port_max : Attribute #2. .
            dscp_mark : Attribute #3. .
            piggyback_events : Attribute #4. .
            tone_events : Attribute #5. .
            dtmf_events : Attribute #6. .
            cas_events : Attribute #7. .
            ip_host_config_ptr : Attribute #8. .
        """
        super(rtp_profile_data_me, self).__init__(inst)
        if local_port_min is not None:
            self.set_attr_value(1, local_port_min)
        if local_port_max is not None:
            self.set_attr_value(2, local_port_max)
        if dscp_mark is not None:
            self.set_attr_value(3, dscp_mark)
        if piggyback_events is not None:
            self.set_attr_value(4, piggyback_events)
        if tone_events is not None:
            self.set_attr_value(5, tone_events)
        if dtmf_events is not None:
            self.set_attr_value(6, dtmf_events)
        if cas_events is not None:
            self.set_attr_value(7, cas_events)
        if ip_host_config_ptr is not None:
            self.set_attr_value(8, ip_host_config_ptr)


#################
# pots_uni: Physical path termination point POTS UNI (9.9.1)
#################

pots_uni_admin_state = EnumDatum(
    1,
    (
        ('UNLOCK', 0x0),
        ('LOCK', 0x1),
        ('SHUTDOWN', 0x2),
    )
)

pots_uni_impedance = EnumDatum(
    1,
    (
        ('600_OHMS', 0x0),
        ('900_OHMS', 0x1),
    )
)

pots_uni_oper_state = EnumDatum(
    1,
    (
        ('ENABLED', 0x0),
        ('DISABLED', 0x1),
    )
)

pots_uni_hook_state = EnumDatum(
    1,
    (
        ('ON_HOOK', 0x0),
        ('OFF_HOOK', 0x1),
    )
)



class pots_uni_me(ME):
    """ POTS_UNI (53) - Physical path termination point POTS UNI (9.9.1). """
    me_class = 53
    name = 'POTS_UNI'
    description = 'Physical path termination point POTS UNI (9.9.1)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'admin_state', 'Admin state', 'RW', 'M', pots_uni_admin_state),
        Attr(2, 'deprecated1', '', 'RW', 'O', NumberDatum(2)),
        Attr(3, 'arc', 'See A 1.4.3', 'RW', 'O', NumberDatum(1)),
        Attr(4, 'arc_interval', 'See A.1.4.3', 'RW', 'O', NumberDatum(1)),
        Attr(5, 'impedance', '', 'RW', 'O', pots_uni_impedance),
        Attr(6, 'transmission_path', '', 'RW', 'O', NumberDatum(1)),
        Attr(7, 'rx_gain', '', 'RW', 'O', NumberDatum(1)),
        Attr(8, 'tx_gain', '', 'RW', 'O', NumberDatum(1)),
        Attr(9, 'oper_state', '', 'R', 'O', pots_uni_oper_state),
        Attr(10, 'hook_state', '', 'R', 'O', pots_uni_hook_state),
        Attr(11, 'holdover_time', '', 'RW', 'O', NumberDatum(2)),
        Attr(12, 'nominal_feed_voltage', '', 'RW', 'O', NumberDatum(1)),
    )
    num_attrs = len(attrs)
    actions = ('set', 'get', 'test')

    def __init__(self,
            inst : int,
            admin_state = None,
            deprecated1 = None,
            arc = None,
            arc_interval = None,
            impedance = None,
            transmission_path = None,
            rx_gain = None,
            tx_gain = None,
            holdover_time = None,
            nominal_feed_voltage = None
        ):
        """ POTS_UNI ME Constructor.

        Args:
            inst : ME instance.
            admin_state : Attribute #1. Admin state.
            deprecated1 : Attribute #2. .
            arc : Attribute #3. See A 1.4.3.
            arc_interval : Attribute #4. See A.1.4.3.
            impedance : Attribute #5. .
            transmission_path : Attribute #6. .
            rx_gain : Attribute #7. .
            tx_gain : Attribute #8. .
            holdover_time : Attribute #11. .
            nominal_feed_voltage : Attribute #12. .
        """
        super(pots_uni_me, self).__init__(inst)
        if admin_state is not None:
            self.set_attr_value(1, admin_state)
        if deprecated1 is not None:
            self.set_attr_value(2, deprecated1)
        if arc is not None:
            self.set_attr_value(3, arc)
        if arc_interval is not None:
            self.set_attr_value(4, arc_interval)
        if impedance is not None:
            self.set_attr_value(5, impedance)
        if transmission_path is not None:
            self.set_attr_value(6, transmission_path)
        if rx_gain is not None:
            self.set_attr_value(7, rx_gain)
        if tx_gain is not None:
            self.set_attr_value(8, tx_gain)
        if holdover_time is not None:
            self.set_attr_value(11, holdover_time)
        if nominal_feed_voltage is not None:
            self.set_attr_value(12, nominal_feed_voltage)


#################
# circuit_pack: Circuit pack (9.1.6)
#################

circuit_pack_oper_state = EnumDatum(
    1,
    (
        ('ENABLED', 0x0),
        ('DISABLED', 0x1),
    )
)

circuit_pack_bridged_or_ip = EnumDatum(
    1,
    (
        ('BRIDGED', 0x0),
        ('ROUTED', 0x1),
        ('BRIDGED_AND_ROUTED', 0x2),
    )
)

circuit_pack_card_config = EnumDatum(
    1,
    (
        ('DS1', 0x0),
        ('E1', 0x1),
        ('J1', 0x2),
    )
)



class circuit_pack_me(ME):
    """ CIRCUIT_PACK (6) - Circuit pack (9.1.6). """
    me_class = 6
    name = 'CIRCUIT_PACK'
    description = 'Circuit pack (9.1.6)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'type', 'Table 9.1.5-1', 'RC', 'M', NumberDatum(1)),
        Attr(2, 'number_of_ports', '', 'R', 'O', NumberDatum(1)),
        Attr(3, 'serial_number', '', 'R', 'M', BytesDatum(8)),
        Attr(4, 'version', '', 'R', 'M', BytesDatum(14)),
        Attr(5, 'vendor_id', '', 'R', 'O', BytesDatum(4)),
        Attr(6, 'admin_state', 'Admin state', 'RW', 'M', NumberDatum(1)),
        Attr(7, 'oper_state', '', 'R', 'O', circuit_pack_oper_state),
        Attr(8, 'bridged_or_ip', '', 'RW', 'O', circuit_pack_bridged_or_ip),
        Attr(9, 'equip_id', '', 'R', 'O', BytesDatum(20)),
        Attr(10, 'card_config', '', 'RWC', 'M', circuit_pack_card_config),
        Attr(11, 'tcont_buffer_number', '', 'R', 'M', NumberDatum(1)),
        Attr(12, 'priority_queue_number', '', 'R', 'M', NumberDatum(1)),
        Attr(13, 'traffic_sched_number', '', 'R', 'M', NumberDatum(1)),
        Attr(14, 'power_shed_override', '', 'RW', 'O', NumberDatum(4)),
    )
    num_attrs = len(attrs)
    actions = ('create', 'delete', 'set', 'get')

    def __init__(self,
            inst : int,
            type = None,
            admin_state = None,
            bridged_or_ip = None,
            card_config = None,
            power_shed_override = None
        ):
        """ CIRCUIT_PACK ME Constructor.

        Args:
            inst : ME instance.
            type : Attribute #1. Table 9.1.5-1.
            admin_state : Attribute #6. Admin state.
            bridged_or_ip : Attribute #8. .
            card_config : Attribute #10. .
            power_shed_override : Attribute #14. .
        """
        super(circuit_pack_me, self).__init__(inst)
        if type is not None:
            self.set_attr_value(1, type)
        if admin_state is not None:
            self.set_attr_value(6, admin_state)
        if bridged_or_ip is not None:
            self.set_attr_value(8, bridged_or_ip)
        if card_config is not None:
            self.set_attr_value(10, card_config)
        if power_shed_override is not None:
            self.set_attr_value(14, power_shed_override)


#################
# enhanced_security_control: Enhanced Security Control (9.13.11)
#################


enhanced_security_control_broadcast_key_table_row_control = EnumDatum(
    1,
    (
        ('SET_ROW', 0x0),
        ('CLEAR_ROW', 0x1),
        ('CLEAR_TABLE', 0x2),
    )
)



class enhanced_security_control_olt_random_challenge_table(StructDatum):
    fields = (
        StructField('row_number', '', field_type=NumberDatum(1)),
        StructField('content', '', field_type=BytesDatum(16)),
    )
    def __init__(self, default: AttrValue = None, fixed: AttrValue = None, size = 17):
        super().__init__(size, default=default, fixed=fixed)


class enhanced_security_control_onu_random_challenge_table(StructDatum):
    fields = (
        StructField('content', '', field_type=BytesDatum(16)),
    )
    def __init__(self, default: AttrValue = None, fixed: AttrValue = None, size = 16):
        super().__init__(size, default=default, fixed=fixed)


class enhanced_security_control_onu_auth_result_table(StructDatum):
    fields = (
        StructField('content', '', field_type=BytesDatum(16)),
    )
    def __init__(self, default: AttrValue = None, fixed: AttrValue = None, size = 16):
        super().__init__(size, default=default, fixed=fixed)


class enhanced_security_control_olt_auth_result_table(StructDatum):
    fields = (
        StructField('row_number', '', field_type=NumberDatum(1)),
        StructField('content', '', field_type=BytesDatum(16)),
    )
    def __init__(self, default: AttrValue = None, fixed: AttrValue = None, size = 17):
        super().__init__(size, default=default, fixed=fixed)


class enhanced_security_control_broadcast_key_table(StructDatum):
    fields = (
        StructField('row_control', '', field_type=enhanced_security_control_broadcast_key_table_row_control),
        StructField('row_number', '', field_type=NumberDatum(1)),
        StructField('content', '', field_type=BytesDatum(16)),
    )
    def __init__(self, default: AttrValue = None, fixed: AttrValue = None, size = 18):
        super().__init__(size, default=default, fixed=fixed)

class enhanced_security_control_me(ME):
    """ ENHANCED_SECURITY_CONTROL (332) - Enhanced Security Control (9.13.11). """
    me_class = 332
    name = 'ENHANCED_SECURITY_CONTROL'
    description = 'Enhanced Security Control (9.13.11)'
    attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', 'R', 'M', NumberDatum(2, fixed=0)),
        Attr(1, 'crypto_capabilities', '', 'W', 'M', BytesDatum(16)),
        Attr(2, 'olt_random_challenge_table', '', 'RW', 'M', enhanced_security_control_olt_random_challenge_table()),
        Attr(3, 'olt_challenge_status', '', 'RW', 'M', NumberDatum(1)),
        Attr(4, 'onu_selected_crypto_capabilities', '', 'R', 'M', NumberDatum(1)),
        Attr(5, 'onu_random_challenge_table', '', 'R', 'M', enhanced_security_control_onu_random_challenge_table()),
        Attr(6, 'onu_auth_result_table', '', 'R', 'M', enhanced_security_control_onu_auth_result_table()),
        Attr(7, 'olt_auth_result_table', '', 'W', 'M', enhanced_security_control_olt_auth_result_table()),
        Attr(8, 'olt_result_status', '', 'RW', 'M', NumberDatum(1)),
        Attr(9, 'onu_auth_status', '', 'R', 'M', NumberDatum(1)),
        Attr(10, 'master_session_key_name', '', 'R', 'M', BytesDatum(16)),
        Attr(11, 'broadcast_key_table', '', 'RW', 'O', enhanced_security_control_broadcast_key_table()),
        Attr(12, 'effective_key_length', '', 'R', 'O', NumberDatum(2)),
    )
    num_attrs = len(attrs)
    actions = ('set', 'get', 'get_next')

    def __init__(self,
            inst : int,
            crypto_capabilities = None,
            olt_random_challenge_table = None,
            olt_challenge_status = None,
            olt_auth_result_table = None,
            olt_result_status = None,
            broadcast_key_table = None,
        ):
        """ ENHANCED_SECURITY_CONTROL ME Constructor.

        Args:
            inst : ME instance.
            crypto_capabilities : Attribute #1. .
            olt_random_challenge_table : Attribute #2. .
            olt_challenge_status : Attribute #3. .
            olt_auth_result_table : Attribute #7. .
            olt_result_status : Attribute #8. .
            broadcast_key_table : Attribute #11. .
        """
        super(enhanced_security_control_me, self).__init__(inst)
        if crypto_capabilities is not None:
            self.set_attr_value(1, crypto_capabilities)
        if olt_random_challenge_table is not None:
            self.set_attr_value(2, olt_random_challenge_table)
        if olt_challenge_status is not None:
            self.set_attr_value(3, olt_challenge_status)
        if olt_auth_result_table is not None:
            self.set_attr_value(7, olt_auth_result_table)
        if olt_result_status is not None:
            self.set_attr_value(8, olt_result_status)
        if broadcast_key_table is not None:
            self.set_attr_value(11, broadcast_key_table)


class MeClassMapper:

    me_dict = {
        272: gal_eth_prof_me,
        266: gem_iw_tp_me,
        268: gem_port_net_ctp_me,
        130: ieee_8021_p_mapper_svc_prof_me,
        47: mac_bridge_port_config_data_me,
        45: mac_bridge_svc_prof_me,
        84: vlan_tag_filter_data_me,
        262: tcont_me,
        171: ext_vlan_tag_oper_config_data_me,
        277: priority_queue_g_me,
        281: mcast_gem_iw_tp_me,
        309: mcast_operations_profile_me,
        310: mcast_subscriber_config_info_me,
        11: pptp_eth_uni_me,
        329: virtual_eth_intf_point_me,
        2: onu_data_me,
        256: onu_g_me,
        257: onu2_g_me,
        7: sw_image_me,
        263: ani_g_me,
        341: gem_port_net_ctp_pm_me,
        322: eth_frame_upstream_pm_me,
        321: eth_frame_downstream_pm_me,
        312: fec_pm_me,
        344: xgpon_tc_pm_me,
        134: ip_host_config_data_me,
        141: voip_line_status_me,
        142: voip_media_profile_me,
        153: sip_user_data_me,
        150: sip_agent_config_data_me,
        137: network_address_me,
        157: large_string_me,
        148: authentication_security_method_me,
        58: voice_service_profile_me,
        138: voip_config_data_me,
        139: voip_voice_ctp_me,
        136: tcp_udp_config_data_me,
        145: network_dial_plan_table_me,
        143: rtp_profile_data_me,
        53: pots_uni_me,
        6: circuit_pack_me,
        332: enhanced_security_control_me
    }

    @classmethod
    def me_by_class(cls, me_class: int) -> ME:
        if me_class not in cls.me_dict:
            return None
        return cls.me_dict[me_class]

#endif
