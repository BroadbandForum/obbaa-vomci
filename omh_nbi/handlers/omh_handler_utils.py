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
# OMH handler utilities that that are used by multiple OMH handlers.
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

""" OMH Handler utilities """
from ..omh_handler import OmhHandler, OMHStatus
from .omh_types import PacketClassifier, PacketAction, VlanAction, VlanTag, PBIT_VALUE_ANY, VID_VALUE_ANY
from database.omci_me_types import *
from omh_nbi.onu_driver import OnuDriver
from encode_decode.omci_action_create import CreateAction
from encode_decode.omci_action_set import SetAction

def create_8021p_svc_mapper(handler:OmhHandler, name: str) -> OMHStatus:
    """ Create 802.1p Service Mapper

        handler: OMH handler that requested this service
        name: QoS profile name
    Returns:
        completion status
    """
    all_instance_ids = handler._onu.get_all_instance_ids(omci_me_class['IEEE_8021_P_MAPPER_SVC_PROF'])
    inst_id = len(all_instance_ids) > 0 and all_instance_ids[-1] + 1 or 1
    profile_me = ieee_8021_p_mapper_svc_prof_me(
        inst_id,
        tp_ptr=OMCI_NULL_PTR,
        interwork_tp_ptr_pri_0=OMCI_NULL_PTR,
        interwork_tp_ptr_pri_1=OMCI_NULL_PTR,
        interwork_tp_ptr_pri_2=OMCI_NULL_PTR,
        interwork_tp_ptr_pri_3=OMCI_NULL_PTR,
        interwork_tp_ptr_pri_4=OMCI_NULL_PTR,
        interwork_tp_ptr_pri_5=OMCI_NULL_PTR,
        interwork_tp_ptr_pri_6=OMCI_NULL_PTR,
        interwork_tp_ptr_pri_7=OMCI_NULL_PTR,
        unmarked_frame_opt='DERIVE_IMPLIED_PCP',
        mapper_tp_type='BRIDGING_MAPPING')
    profile_me.user_name = name
    if handler.transaction(CreateAction(handler, profile_me)) != OMHStatus.OK:
        return handler.logerr_and_return(
            handler._transaction_status,
            'Create IEEE 802.1p Mapper SVC Profile ME {}'.format(name))
    return OMHStatus.OK


def create_mac_bridge_port(handler: OmhHandler, tp: ME) -> OMHStatus:
    """Create MAC Bridge Port Config Data for an interface

    Args:
        handler: OMH handler that requested this service
        tp: Bridge port Termination Point
    Returns:
        completion status
    """

    # Get mac_bridge_svc_prof ME
    mac_bridge_svc_prof = handler._onu.get_first(omci_me_class['MAC_BRIDGE_SVC_PROF'])
    if mac_bridge_svc_prof is None:
        return handler.logerr_and_return(OMHStatus.INTERNAL_ERROR,
                                      "MAC Bridge Service Profile ME doesn't exist")

    all_bridge_ports = handler._onu.get_all_instance_ids(omci_me_class['MAC_BRIDGE_PORT_CONFIG_DATA'])
    port_num = len(all_bridge_ports) > 0 and all_bridge_ports[-1] + 1 or 1
    mac_bridge_port = mac_bridge_port_config_data_me(inst=port_num, bridge_id_ptr = mac_bridge_svc_prof.inst,
                                                     port_num = port_num, tp_ptr = tp.inst)
    if type(tp) is pptp_eth_uni_me:
        mac_bridge_port.tp_type = 'PHY_PATH_TP_ETH_UNI'
    elif type(tp) is virtual_eth_intf_point_me:
        mac_bridge_port.tp_type = 'VIRTUAL_ETH_INTERFACE_POINT'
    elif type(tp) is ieee_8021_p_mapper_svc_prof_me:
        mac_bridge_port.tp_type = 'IEEE_8021_P_MAPPER_SVC_PROF'
    else:
        return OMHStatus.NOT_SUPPORTED
    status = handler.transaction(CreateAction(handler, mac_bridge_port))
    if status == OMHStatus.OK:
        tp.set_user_attr('bridge_port', mac_bridge_port.inst)
    return OMHStatus.OK


def create_ext_vlan_tag_oper_config_data(handler: OmhHandler, iface: ME, input_tpid: int = 0, output_tpid: int = 0) -> OMHStatus:
    """Create MAC Bridge Port Config Data for an interface
    Requires user attribute iface.bridge_port_num to be set
    """
    all_instances = handler._onu.get_all_instance_ids(omci_me_class['EXT_VLAN_TAG_OPER_CONFIG_DATA'])
    inst = len(all_instances) > 0 and all_instances[-1] + 1 or 1
    ext_vlan_tag = ext_vlan_tag_oper_config_data_me(inst)
    if type(iface) is pptp_eth_uni_me:
        ext_vlan_tag.assoc_type = 'PPTP_ETH_UNI'
    elif type(iface) is virtual_eth_intf_point_me:
        ext_vlan_tag.assoc_type = 'VEIP'
    elif type(iface) is mac_bridge_port_config_data_me:
        ext_vlan_tag.assoc_type = 'MAC_BRIDGE_PORT_CFG_DATA'
    else:
        return OMHStatus.NOT_SUPPORTED
    ext_vlan_tag.assoc_me_ptr = iface.inst
    status = handler.transaction(CreateAction(handler, ext_vlan_tag))
    if status != OMHStatus.OK:
        return status
    # Now set attributes that can't be set by 'create' action
    ext_vlan_tag.input_tpid = input_tpid != 0 and input_tpid or 0x8100
    ext_vlan_tag.output_tpid = output_tpid != 0 and output_tpid or 0x8100
    # XXX TODO: need to support additional downstream_mode values?
    ext_vlan_tag.ds_mode = 'US_INVERSE'
    status = handler.transaction(SetAction(handler, ext_vlan_tag, ('input_tpid', 'output_tpid', 'ds_mode')))
    if status != OMHStatus.OK:
        return status
    iface.set_user_attr('ext_vlan_tag_op', inst)
    return OMHStatus.OK

def create_vlan_tagging_filter_data(handler: OmhHandler, inst: int, name: str,
                                    classifier: PacketClassifier, vlan_action: VlanAction)  -> OMHStatus:
    """ Create and configure VLAN Tagging Filter Data ME

    Please note that vlan tagging filter is applied BEFORE vlan_action in the ingress
    and AFTER vlan_action in the egress. Therefore, need to take 'action' into account.

    Args:
        handler: OMH handler that requested this service
        inst: instance id. Must be equal to the instance of the associated MAC Bridge Port Data ME
        classifier: Packet classifier
        vlan_action: Packet VLAN action
    Returns:
        completion status
    """

    # XXX: TODO: add support for multiple VLAN classifier in a sub-interface
    if vlan_action is not None:
        if vlan_action.action == VlanAction.Action.PUSH or vlan_action.action == VlanAction.Action.TRANSLATE:
            o_vid = vlan_action.o_vid
        elif vlan_action.action == VlanAction.Action.POP:
            o_vid = classifier is None and None or classifier.field('i_vid')
        else:
            return handler.logerr_and_return(OMHStatus.NOT_SUPPORTED,
                                             "VLAN action {} is not supported".format(vlan_action.action))
    else:
        o_vid = classifier is None and None or classifier.field('o_vid')

    tcid = 0
    if o_vid is None:
        action = 'TAGGED_BRIDGING_A_NO_INVESTIGATION_UNTAGGED_BRIDGING_A'
    elif o_vid.pbit != PBIT_VALUE_ANY:
        tcid |= (o_vid.pbit << 13)
        if o_vid.vid != VID_VALUE_ANY:
            action = 'TAGGED_ACTION_H_TCI_INVESTIGATION_UNTAGGED_DISCARDING_C_DUP'
            tcid |= o_vid.vid
        else:
            action = 'TAGGED_ACTION_H_PRI_INVESTIGATION_UNTAGGED_DISCARDING_C_DUP'
    elif o_vid.vid != VID_VALUE_ANY:
        # Classify by VID only
        action = 'TAGGED_ACTION_H_VID_INVESTIGATION_UNTAGGED_DISCARDING_C_DUP'
        tcid |= o_vid.vid

    vlan_filter = bytearray(2)
    vlan_filter[0] = tcid >> 8
    vlan_filter[1] = tcid & 0xff
    tag_filter_me = vlan_tag_filter_data_me(inst, vlan_filter_list=vlan_filter, forward_oper=action, num_of_entries=1)
    tag_filter_me.user_name = name
    return handler.transaction(CreateAction(handler, tag_filter_me))


def set_ext_vlan_tag_op(handler: OmhHandler, ext_vlan_tag_op: ext_vlan_tag_oper_config_data_me,
                        classifier: PacketClassifier, vlan_action: VlanAction) -> OMHStatus:
    """ Add entry to set_ext_vlan_tagging_op ME based on the requested PacketAction

     Args:
        handler: OMH handler that requested this service
        ext_vlan_tag_op: EXT VLAN TAG OP ME
        vlan_action: VLAN action
    Returns:
        completion status
    """
    o_vid = classifier is None and None or classifier.field('o_vid')
    i_vid = classifier is None and None or classifier.field('i_vid')

    EXT_VLAN_TAG_IGNORE_ENTRY = 15
    EXT_VLAN_TAG_DO_NOT_FILTER_ON_PRIORITY = 8
    EXT_VLAN_TAG_DO_NOT_FILTER_ON_VID = 4096
    EXT_VLAN_TAG_DO_NOT_ADD_TAG = 15
    EXT_VLAN_TAG_SET_TPID_BY_EXT_VLAN_TAG_OP_COPY_DEI_FROM_PACKET = 3
    EXT_VLAN_TAG_DO_NOT_FILTER_ON_TPID = 0

    # Create inner and outer filters based on the classifiers. If no classiofiers are set,
    # create an untagged rule.
    # Note that inner_filter is used for a single-tag rule. outer_filter is used only for
    # dual-tagged.
    outer_filter = {}
    if i_vid is not None and o_vid is not None:
        outer_filter['filter_outer_priority'] = (o_vid.pbit == PBIT_VALUE_ANY) \
            and EXT_VLAN_TAG_DO_NOT_FILTER_ON_PRIORITY or o_vid.pbit
        outer_filter['filter_outer_vid'] = (o_vid.vid == VID_VALUE_ANY) \
            and EXT_VLAN_TAG_DO_NOT_FILTER_ON_VID or o_vid.vid
    else:
        outer_filter['filter_outer_priority'] = EXT_VLAN_TAG_IGNORE_ENTRY
    outer_filter['filter_outer_tpid'] = EXT_VLAN_TAG_DO_NOT_FILTER_ON_TPID

    inner_filter = {}
    if o_vid is not None:
        vid = (i_vid is not None) and i_vid or o_vid
        inner_filter['filter_inner_priority'] = (vid.pbit == PBIT_VALUE_ANY) \
            and EXT_VLAN_TAG_DO_NOT_FILTER_ON_PRIORITY or vid.pbit
        inner_filter['filter_inner_vid'] = (vid.vid == VID_VALUE_ANY) \
            and EXT_VLAN_TAG_DO_NOT_FILTER_ON_VID or vid.vid
    else:
        inner_filter['filter_inner_priority'] = EXT_VLAN_TAG_IGNORE_ENTRY
    # XXX TODO no support for filter on TPID
    inner_filter['filter_inner_tpid'] = EXT_VLAN_TAG_DO_NOT_FILTER_ON_TPID

    # Done with filter, set up treatment. inner fields are used for single tag operations.
    # TRANSLATE == REMOVE + ADD
    if vlan_action.action == VlanAction.Action.POP or vlan_action.action == VlanAction.Action.TRANSLATE:
        num_to_delete = vlan_action.num_tags
    elif vlan_action.action == VlanAction.Action.PUSH:
        num_to_delete = 0
    else:
        return handler.logerr_and_return(OMHStatus.NOT_SUPPORTED,
                                     "VLAN action {} is not supported".format(vlan_action.action))
    # XXX TODO no support for dual PUSH
    outer_treatment = {}
    outer_treatment['treatment'] = num_to_delete
    outer_treatment['treatment_outer_priority'] = EXT_VLAN_TAG_DO_NOT_ADD_TAG
    inner_treatment = {}
    if vlan_action.action == VlanAction.Action.PUSH or vlan_action.action == VlanAction.Action.TRANSLATE:
        inner_treatment['treatment_inner_priority'] = vlan_action.o_vid.pbit
        inner_treatment['treatment_inner_vid'] = vlan_action.o_vid.vid
        inner_treatment['treatment_inner_tpid'] = EXT_VLAN_TAG_SET_TPID_BY_EXT_VLAN_TAG_OP_COPY_DEI_FROM_PACKET
    else:
        inner_treatment['treatment_inner_priority'] = EXT_VLAN_TAG_DO_NOT_ADD_TAG

    ext_vlan_tag_op.rx_frame_vlan_tag_oper_table =  {
        'outer_filter_word': outer_filter,
        'inner_filter_word': inner_filter,
        'outer_treatment_word': outer_treatment,
        'inner_treatment_word': inner_treatment }

    return handler.transaction(SetAction(handler, ext_vlan_tag_op, ('rx_frame_vlan_tag_oper_table',)))


def get_uni(onu: OnuDriver, uni: Union[str, int]) -> ME:
    """ Get UNI ME by name or index.

    Args:
         onu: OnuDriver
         uni: UNI name assigned using me.user_name or 0-based index
    Returns:
        UNI ME or None if not found
    """
    if isinstance(uni, str):
        return onu.get_by_name(uni)

    # uni is an index
    all_unis = onu.get_all_instances(omci_me_class['PPTP_ETH_UNI']) + \
                onu.get_all_instances(omci_me_class['VIRTUAL_ETH_INTF_POINT'])
    return uni < len(all_unis) and all_unis[uni] or None


def get_queue_by_owner_tc(onu: OnuDriver, is_upstream: bool, owner: ME, tc: int) -> ME:
    """ Get PRIORITY_QUEUE_G ME by ME that owns it and a traffic class.

        TODO: requires more work

        Args:
            onu: OnuDriver
            owner: ME that owns the priority queue
            tc: traffic class
        Returns:
            Priority queue ME or None if not found
    """
    all_queues = onu.get_all_instances(omci_me_class['PRIORITY_QUEUE_G'])
    last_queue = None
    for q in all_queues:
        # MS bit in the priority queue instance id represents direction 1=US
        if is_upstream and (q.inst & 0x8000) == 0:
            continue
        related_port = q.related_port
        related_inst = related_port[0] << 8 | related_port[1]
        if related_inst != owner.inst:
            continue
        last_queue = q
        priority = related_port[2] << 8 | related_port[3]
        if priority == tc:
            break

    return last_queue

def get_gem_ports_by_uni(onu: OnuDriver, uni_name: str) -> Tuple[ME, ...]:
    """ Get all GEM ports associated with UNI port """
    all_gem_ports = onu.get_all_instances(omci_me_class['GEM_PORT_NET_CTP'])
    all_gem_ports_by_uni = []
    for gem in all_gem_ports:
        gem_uni = gem.user_attr('uni')
        if gem_uni is not None and gem_uni == uni_name:
            all_gem_ports_by_uni.append(gem)
    return tuple(all_gem_ports_by_uni)

def get_gem_port_by_uni_tc(onu: OnuDriver, uni_name: str, tc: int) -> ME:
    """ Get GEM port by UNI it is associated with and traffic class """
    gem_ports_by_uni = get_gem_ports_by_uni(onu, uni_name)
    for gem in gem_ports_by_uni:
        gem_tc = gem.user_attr('tc')
        if gem_tc is not None and gem_tc == tc:
            return gem
    return None

def _set_8021p_priority(mapper_me: ieee_8021_p_mapper_svc_prof_me, pbit: int, value: int):
    if pbit == 0:
        mapper_me.interwork_tp_ptr_pri_0 = value
    elif pbit == 1:
        mapper_me.interwork_tp_ptr_pri_1 = value
    elif pbit == 2:
        mapper_me.interwork_tp_ptr_pri_2 = value
    elif pbit == 3:
        mapper_me.interwork_tp_ptr_pri_3 = value
    elif pbit == 4:
        mapper_me.interwork_tp_ptr_pri_4 = value
    elif pbit == 5:
        mapper_me.interwork_tp_ptr_pri_5 = value
    elif pbit == 6:
        mapper_me.interwork_tp_ptr_pri_6 = value
    elif pbit == 7:
        mapper_me.interwork_tp_ptr_pri_7 = value


def _set_8021p_mapper(handler: OmhHandler, mapper_me: ieee_8021_p_mapper_svc_prof_me,
                      pbit_to_tc: 'PbitToTCMapper', uni_name: str, pbit: int) -> (OMHStatus, bool):
    """ Set up 802_1p mapper ME for a specified priority and all other priorities that
        map to the same traffic class
    """
    tc = pbit_to_tc.tc(pbit)
    if tc is None:
        return OMHStatus.OK, False

    # Find a GEM port by UNI and TC
    gem = get_gem_port_by_uni_tc(handler.onu, uni_name, tc)
    if gem is None:
        return OMHStatus.OK, False

    # Find GAL ethernet profile
    gal_eth_prof = handler.onu.get_by_name('gal_eth_prof')
    if gal_eth_prof is None:
        logger.error("set_8021p_mapper: GAL Ethernet Profile is not found")
        return OMHStatus.INTERNAL_ERROR, False

    # Create GEM_IW_TP
    all_gem_iw_tp_inst = handler.onu.get_all_instance_ids(omci_me_class['GEM_IW_TP'])
    gem_iw_tp_inst = len(all_gem_iw_tp_inst) > 0 and all_gem_iw_tp_inst[-1] + 1 or 1
    gem_iw_tp = gem_iw_tp_me(
        gem_iw_tp_inst,
        gem_port_net_ctp_conn_ptr = gem.inst,
        iw_opt = 'IEEE_8021_P_MAPPER',
        svc_prof_ptr = mapper_me.inst,
        iw_tp_ptr = OMCI_NULL_PTR,
        gal_prof_ptr = gal_eth_prof.inst
    )
    status = handler.transaction(CreateAction(handler, gem_iw_tp))
    if status != OMHStatus.OK:
        return status, False

    # Plug GEM IW_TP into all priorities that map to the same tc
    pbits_by_tc = pbit_to_tc.pbits_by_tc(tc)
    for pbit in pbits_by_tc:
        _set_8021p_priority(mapper_me, pbit, gem_iw_tp.inst)

    return OMHStatus.OK, True


def set_8021p_mapper(handler: OmhHandler, mapper_me: ieee_8021_p_mapper_svc_prof_me,
                     pbit_to_tc: 'PbitToTCMapper', uni_name: str) -> OMHStatus:
    """ Set up 802_1p mapper ME.

        Go over all unassigned priorities and try to find GEM_PORT_NET_CTP ME
        by UNI and TC that maps to this priority.
        If fount, create GEM_IW_TP ME and plug it into the priority slots for
        all PBITs that map to the same TC.

    Args:
          handler: OMH handler that called this service
          mapper_me: 802.1p Mapper SVC Profile ME
          pbit_to_tc: PBIT to TC mapper
          uni_name: UNI interface name
    Returns: transaction status
    """
    ret = False
    status = OMHStatus.OK
    if mapper_me.interwork_tp_ptr_pri_0 == OMCI_NULL_PTR:
        status1, ret1 = _set_8021p_mapper(handler, mapper_me, pbit_to_tc, uni_name, 0)
        ret = ret1 or ret
        status = (status == OMHStatus.OK) and status1 or status
    if mapper_me.interwork_tp_ptr_pri_1 == OMCI_NULL_PTR:
        status1, ret1 = _set_8021p_mapper(handler, mapper_me, pbit_to_tc, uni_name, 1)
        ret = ret1 or ret
        status = (status == OMHStatus.OK) and status1 or status
    if mapper_me.interwork_tp_ptr_pri_2 == OMCI_NULL_PTR:
        status1, ret1 = _set_8021p_mapper(handler, mapper_me, pbit_to_tc, uni_name, 2)
        ret = ret1 or ret
        status = (status == OMHStatus.OK) and status1 or status
    if mapper_me.interwork_tp_ptr_pri_3 == OMCI_NULL_PTR:
        status1, ret1 = _set_8021p_mapper(handler, mapper_me, pbit_to_tc, uni_name, 3)
        ret = ret1 or ret
        status = (status == OMHStatus.OK) and status1 or status
    if mapper_me.interwork_tp_ptr_pri_4 == OMCI_NULL_PTR:
        status1, ret1 = _set_8021p_mapper(handler, mapper_me, pbit_to_tc, uni_name, 4)
        ret = ret1 or ret
        status = (status == OMHStatus.OK) and status1 or status
    if mapper_me.interwork_tp_ptr_pri_5 == OMCI_NULL_PTR:
        status1, ret1 = _set_8021p_mapper(handler, mapper_me, pbit_to_tc, uni_name, 5)
        ret = ret1 or ret
        status = (status == OMHStatus.OK) and status1 or status
    if mapper_me.interwork_tp_ptr_pri_6 == OMCI_NULL_PTR:
        status1, ret1 = _set_8021p_mapper(handler, mapper_me, pbit_to_tc, uni_name, 6)
        ret = ret1 or ret
        status = (status == OMHStatus.OK) and status1 or status
    if mapper_me.interwork_tp_ptr_pri_7 == OMCI_NULL_PTR:
        status1, ret1 = _set_8021p_mapper(handler, mapper_me, pbit_to_tc, uni_name, 7)
        ret = ret1 or ret
        status = (status == OMHStatus.OK) and status1 or status

    if status != OMHStatus.OK:
        return status

    # Update 8021.p mapper if there were changes
    if ret:
        status = handler.transaction(SetAction(handler, mapper_me))
        if status != OMHStatus.OK:
            return handler.logerr_and_return(status, 'Failed to set up qos profile ME {}'.format(mapper_me.user_name))

    return OMHStatus.OK
