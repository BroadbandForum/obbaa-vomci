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
#Yang to OMCI handlers for UNI, TCONT, GEM port, QOS & Vlan sub-interfaces
#
#Created by Karthik(Altran) & Maheswari (Altran) on 27th August 2020
#

from hashlib import new
from typing import Optional, Tuple, Any, Union
from omh_nbi.handlers.ani_set import AniSetHandler
from omh_nbi.handlers.onu_activate import OnuActivateHandler
from omh_nbi.handlers.uni_set import UniSetHandler
from omh_nbi.handlers.tcont_create import TcontCreateHandler
from omh_nbi.handlers.gem_port_create import GemPortCreateHandler
from omh_nbi.handlers.qos_policy_profile_set import QosPolicyProfile, QosPolicyProfileSetHandler
from omh_nbi.handlers.vlan_subinterface_set import VlanSubInterfaceSetHandler
from omh_nbi.handlers.get_hardware_state import GetHardwareStateHandler
from omh_nbi.handlers.onu_get_all_alarms import GetAllAlarmsHandler
from omh_nbi.handlers.get_interfaces_state import GetInterfacesStateHandler
from omh_nbi.handlers.vlan_subinterface_remove import VlanSubInterfaceDeleteHandler
from omh_nbi.handlers.omh_types import PacketClassifier, PacketAction, \
    VlanAction, VlanTag, PBIT_VALUE_ANY, VID_VALUE_ANY
from omh_nbi.omh_handler import OmhHandler, OMHStatus
from omh_nbi.onu_driver import OnuDriver
from database.omci_olt import OltDatabase
from omci_logger import OmciLogger
from omci_types import PoltId
#from vomci import VOmci
logger = OmciLogger.getLogger(__name__)

dict_vlan_subiface = dict()
default_netconf_op= " "


def extractPayload(vomci : 'VOmci', onuname: str, oltname: PoltId, payload: dict) -> OMHStatus:
    """
    Parse yang objects and invoke yangtoomci mapper handler class
    Args:
        onuname: onu name
        oltname: olt name
        payload: Dictionary which contains yang objects
    """

    subif_name = None
    uni_name = None
    classifier = None
    action = None
    qos_profile = None

    targetDict = None
    olt = OltDatabase().OltGet(oltname)
    if olt is None:
        logger.info("olt {} is not present in the database".format(olt.id))
        return OMHStatus.OLT_NOT_FOUND

    onu = olt.OnuGetByName(onuname, False)
    if onu is None:
        logger.info("onu {} is not present in the database".format(onuname))
        return OMHStatus.ONU_NOT_FOUND

    keys = payload.keys()
    logger.debug("yang_to_omci_mapper::extractPayload key=={} payload={}".format(keys, payload))
    copy_config = False
    get_data = False


    if 'config_inst' in keys:
        targetDict = payload['config_inst']
        copy_config = True
    
    elif 'current_config_inst' in keys:
        
        targetDict = payload['current_config_inst']
        currentDict = payload['current_config_inst']
        
        if 'delta_config' in keys:
            deltaDict = payload['delta_config']
            if deltaDict:
                targetDict = deltaDict

    elif 'delta_config' in keys:
        targetDict = payload['delta_config']
    elif 'operation' in keys:
        if 'copy-config' == payload['operation']:
            copy_config = True
            if 'target' in payload:
                targetDict = payload['target']
        elif 'edit-config' == payload['operation']:
            if 'delta' in payload:
                targetDict = payload['delta']
    elif 'get_data' in keys:
        targetDict = payload['get_data']
        get_data = True
    else:
        logger.error("The requested operation is not supported by vOMCI")
        return OMHStatus.NOT_SUPPORTED

    handlers = {'onu' : [], 'tcont': [], 'qos-policy-profile': [], 'uni': [], 'ani': [], 'gem': [], 'vlan-subif': []}
    handler_args = {'onu' : [], 'tcont': [], 'qos-policy-profile': [], 'uni': [], 'ani': [], 'gem': [], 'vlan-subif': []}
    pol_dict = {}
    cls_dict = {}
    prof_dict = {}
    

    if get_data:
        logger.info("yang_to_omci_mapper :: extractPayload :: handling get data request")
        # Currently, Get requests only report software images, regardless of given filters
        get_handlers = {}
        get_handler_args = {}

        mapperObj = YangtoOmciMapperHandler(vomci, onu)

        if 'ietf-hardware:hardware-state' in targetDict:
            get_handlers['hardware_state'] = []
            get_handler_args['hardware_state'] = []
            get_handlers['hardware_state'].append(GetHardwareStateHandler)
            get_handler_args['hardware_state'].append(())
            for i in range(len(get_handlers['hardware_state'])):
                mapperObj.add_handler(get_handlers['hardware_state'][i], get_handler_args['hardware_state'][i])
        if 'ietf-interfaces:interfaces-state' in targetDict:
            get_handlers['interfaces-state'] = []
            get_handler_args['interfaces-state'] = []
            get_handlers['interfaces-state'].append(GetInterfacesStateHandler)
            get_handler_args['interfaces-state'].append(())   
            for i in range(len(get_handlers['interfaces-state'])):
                mapperObj.add_handler(get_handlers['interfaces-state'][i], get_handler_args['interfaces-state'][i])
        if 'ietf-alarms:alarms' in targetDict:
            get_handlers['alarm-list'] = []
            get_handler_args['alarm-list'] = []
            get_handlers['alarm-list'].append(GetAllAlarmsHandler)
            get_handler_args['alarm-list'].append(())
            for i in range(len(get_handlers['alarm-list'])):
                mapperObj.add_handler(get_handlers['alarm-list'][i], get_handler_args['alarm-list'][i])

        status = mapperObj.run()
        return status




    # Must resync ONU in case of copy-config
    if copy_config:
        handlers['onu'].append(OnuActivateHandler)
        handler_args['onu'].append((False,))
  
    if targetDict is not None:
        if 'bbf-xpongemtcont:xpongemtcont' in targetDict:
            YangObjData = targetDict['bbf-xpongemtcont:xpongemtcont']

        # Mapper function for gemport and tcont
            if 'tconts' in YangObjData:
                for tcont in targetDict['bbf-xpongemtcont:xpongemtcont']['tconts']['tcont']:
                    if ('name' and 'alloc-id') in tcont:
                        tcont_name = tcont['name']
                        alloc_id   = tcont['alloc-id']
                        logger.info("mapper: tcontName:{}, allocid:{}".format(tcont_name, alloc_id))
                        handlers['tcont'].append(TcontCreateHandler)
                        handler_args['tcont'].append((tcont_name, alloc_id))
            if 'gemports' in YangObjData:
                for gemport in targetDict['bbf-xpongemtcont:xpongemtcont']['gemports']['gemport']:
                    if ('name' and 'interface' and 'gemport-id' and'traffic-class' and 'tcont-ref') in gemport:
                        gem_port_name = gemport['name']
                        uni_name      = gemport['interface']
                        gem_port_id   = gemport['gemport-id']
                        tc            = gemport['traffic-class']
                        tcont_name    = gemport['tcont-ref']
                        logger.info("mapper: gemport_name:{},uni_name:{}, tcont_name:{}, gemport_id:{},trafficClass:{}".format(
                                    gem_port_name, uni_name, tcont_name, gem_port_id, tc))
                        handlers['gem'].append(GemPortCreateHandler)
                        handler_args['gem'].append((gem_port_name, uni_name, tcont_name, gem_port_id, tc))

        # Mapper function for qos-classifiers
        if 'bbf-qos-classifiers:classifiers' in targetDict:
            YangObjData = targetDict['bbf-qos-classifiers:classifiers']
            if 'classifier-entry' in YangObjData:
                for cls in targetDict['bbf-qos-classifiers:classifiers']['classifier-entry']:
                    name = cls['name']
                    cls_dict[name] = {}
                    cls_dict[name]['pbit'] = 0  # default value
                    if 'classifier-action-entry-cfg' in cls:
                        for tc in cls['classifier-action-entry-cfg']:
                            if "scheduling-traffic-class" in tc['action-type']:
                                cls_dict[name]['traffic_class'] = tc['scheduling-traffic-class']
                    if 'match-criteria' in cls:
                        if 'bbf-qos-policing:pbit-marking-list' in cls['match-criteria']:
                            pbit_marking_list = cls['match-criteria']['bbf-qos-policing:pbit-marking-list']
                            if len(pbit_marking_list) > 0 and 'pbit-value' in pbit_marking_list[0]:
                                cls_dict[name]['pbit'] = pbit_marking_list[0]['pbit-value']
                        if 'tag' in cls['match-criteria']:
                            for pbit in cls['match-criteria']['tag']:
                                if 'in-pbit-list' in pbit:
                                    cls_dict[name]['pbit'] = pbit['in-pbit-list']

        # Mapper function for qos-policies
        if 'bbf-qos-policies:policies' in targetDict:
            YangObjData = targetDict['bbf-qos-policies:policies']
            if 'policy' in YangObjData:
                for pol in targetDict['bbf-qos-policies:policies']['policy']:
                    classifier_list = []
                    name = pol['name']
                    pol_dict[name] = {}
                    if 'classifiers' in pol:
                        for cls in pol['classifiers']:
                            classifier_list.append(cls)
                        pol_dict[name]['classifiers'] = classifier_list

        # Mapper function for qos-policy-profiles
        if 'bbf-qos-policies:qos-policy-profiles' in targetDict:
            YangObjData = targetDict['bbf-qos-policies:qos-policy-profiles']
            if 'policy-profile' in YangObjData:
                for prof in targetDict['bbf-qos-policies:qos-policy-profiles']['policy-profile']:
                    name = prof['name']
                    prof_dict[name] = {}
                    qos_profile_obj = QosPolicyProfile(name)
                    if qos_profile_obj is not None:
                        if 'policy-list' in prof:
                            for pol in prof['policy-list']:
                                rcvd_policy_name = pol['name']
                                for (policy_name, values) in pol_dict.items():
                                    if rcvd_policy_name in policy_name:
                                        for x in (values['classifiers']):
                                            rcvd_classifier_name = x['name']
                                            for (cls_name, values) in cls_dict.items():
                                                if rcvd_classifier_name in cls_name:
                                                    for y in values:
                                                        tc = values['traffic_class']
                                                        pbit = values['pbit']
                                                        qos_profile_obj.tc_set(int(pbit), int(tc))
                        prof_dict[name]['qos_profiles_obj'] = qos_profile_obj
        if 'ietf-interfaces:interfaces' in targetDict:
            YangObjData = targetDict['ietf-interfaces:interfaces']
            if 'interface' in YangObjData:
                for interfaceIter in targetDict['ietf-interfaces:interfaces']['interface']:
                    # Mapper function for uni-interface
                    if 'type' in interfaceIter and 'ethernetCsmacd' in interfaceIter['type']:
                        uni_name = interfaceIter['name']
                        
                        #search for parent-rel-pos. Assuming uni_id=0 if not found
                        uni_id = 0
                        
                        if 'bbf-interface-port-reference:port-layer-if' in interfaceIter:
                            hw_component_name = interfaceIter['bbf-interface-port-reference:port-layer-if']
                            for hwIter in targetDict['ietf-hardware:hardware']['component']:
                                if ('name' in hwIter) and (hw_component_name == hwIter['name']):
                                    if 'parent-rel-pos' in hwIter:
                                        logger.debug("found parent-rel-pos {} for uni_name:{}".format(hwIter['parent-rel-pos'], uni_name))
                                        uni_id = hwIter['parent-rel-pos']-1
                                        
                        pm_enabled = False
                        if 'bbf-interfaces-performance-management:performance' in interfaceIter:
                            if 'enable' in interfaceIter['bbf-interfaces-performance-management:performance']:
                                pm_enabled = interfaceIter['bbf-interfaces-performance-management:performance']['enable']

                        logger.info("uni_name:{}, uni_id:{}, hw_component_name:{}, pm_enabled:{}".format(
                            uni_name, uni_id, hw_component_name, pm_enabled))
                        handlers['uni'].append(UniSetHandler)
                        handler_args['uni'].append((uni_name, uni_id, hw_component_name, pm_enabled))
                    
                        if 'ingress-qos-policy-profile' in interfaceIter:
                            profile_name = interfaceIter['ingress-qos-policy-profile']
                            for (profiles, values) in prof_dict.items():
                                if profile_name in profiles:
                                    if values['qos_profiles_obj'] is not None:
                                        qos_profile = values['qos_profiles_obj']
                                        handlers['qos-policy-profile'].append(QosPolicyProfileSetHandler)
                                        handler_args['qos-policy-profile'].append((qos_profile, uni_name))

                    #Mapper function for ani-interface
                    if 'type' in interfaceIter and 'bbf-xpon-if-type:ani' in interfaceIter['type']:
                        ani_id = 0
                        ani_name = interfaceIter['name']
                        if 'bbf-interface-port-reference:port-layer-if' in interfaceIter:
                            hd_name = interfaceIter['bbf-interface-port-reference:port-layer-if']
                            
                        logger.info("ani_name:{}, ani_id:{}, hd_name:{}".format(ani_name, ani_id,hd_name))
                        handlers['ani'].append(AniSetHandler)
                        handler_args['ani'].append((ani_name,ani_id,hd_name))

                    #Mapper function for vlan-sub-interface
                     # Know the if is create, update,remove
                    if ('type' in interfaceIter and 'vlan-sub-interface' in interfaceIter['type']) or \
                        ('@' in interfaceIter and 'merge' in interfaceIter['@']['ietf-netconf:operation']) or \
                        ('@' in interfaceIter and default_netconf_op in interfaceIter['@']['ietf-netconf:operation']):
                        for (key,value) in interfaceIter.items():
                            if 'name' in key:
                                subif_name = value
                            elif 'subif-lower-layer' in key:
                                uni_name = value['interface']
                            elif 'ingress-qos-policy-profile' in key:
                                profile_name = value
                                qos_profile = None
                                for (profiles, values) in prof_dict.items():
                                    if profile_name in profiles:
                                        if values['qos_profiles_obj'] is not None:
                                            qos_profile = values['qos_profiles_obj']
                                            handlers['qos-policy-profile'].append(QosPolicyProfileSetHandler)
                                            handler_args['qos-policy-profile'].append((qos_profile, uni_name))
                                if qos_profile == None:
                                    #the profile is not present int he current configuration but may have 
                                    # been configured in the past (incremental configuration)
                                    #just store the name to retrieve the ME later
                                    qos_profile = QosPolicyProfile(profile_name)
                            elif 'inline-frame-processing' in key:
                                if 'ingress-rule' in value:
                                    for rule in value['ingress-rule']['rule']:
                                        for (rule_key,rule_value) in rule.items():
                                            if 'flexible-match' in rule_key:
                                                classifier_dict = {}
                                                for (flexible_match_key,flexible_match_value) in rule_value.items():
                                                    if 'match-criteria' in flexible_match_key:
                                                        if 'untagged' in flexible_match_value:
                                                            ing_i_vlan_tag = VID_VALUE_ANY
                                                            ing_o_vlan_tag = VID_VALUE_ANY
                                                            ing_i_pbit = PBIT_VALUE_ANY
                                                            ing_o_pbit = PBIT_VALUE_ANY
                                                        elif 'tag' in flexible_match_value:
                                                            ing_i_vlan_tag = None
                                                            ing_o_vlan_tag = None
                                                            #NOTE: only single values are being processed, but the YANG allows ranges for the VLAN and p-bit (eg: 1,2,4-6)
                                                            for taglist in flexible_match_value['tag']:
                                                                if 'tag-type' in taglist['dot1q-tag'] and taglist['dot1q-tag']['tag-type'] == 'bbf-dot1q-types:c-vlan':
                                                                    ing_i_vlan_tag = yang_mapper_parse_vlan_tag(taglist['dot1q-tag']['vlan-id'])
                                                                    ing_i_pbit = yang_mapper_parse_vlan_pbit(taglist['dot1q-tag']['pbit'])
                                                                if 'tag-type' in taglist['dot1q-tag'] and taglist['dot1q-tag']['tag-type'] == 'bbf-dot1q-types:s-vlan':
                                                                    ing_o_vlan_tag = yang_mapper_parse_vlan_tag(taglist['dot1q-tag']['vlan-id'])
                                                                    ing_o_pbit = yang_mapper_parse_vlan_pbit(taglist['dot1q-tag']['pbit'])
                                                        else:
                                                            #Give a meaningful message instead of a "reference before assignment error".  
                                                            raise Exception("Could not find a valid match-criteria for the ingress-rule.")
                                                        ingress_i_tag = (ing_i_vlan_tag != VID_VALUE_ANY and ing_i_vlan_tag != None) and \
                                                                        VlanTag(vid=ing_i_vlan_tag, pbit=ing_i_pbit) or None
                                                        ingress_o_tag = (ing_o_vlan_tag != VID_VALUE_ANY and ing_o_vlan_tag != None) and \
                                                                        VlanTag(vid=ing_o_vlan_tag, pbit=ing_o_pbit) or None
                                                        if ingress_o_tag is not None:
                                                            classifier_dict['o_vid'] = ingress_o_tag
                                                        if ingress_i_tag is not None:
                                                            classifier_dict['i_vid'] = ingress_i_tag
                                                classifier = PacketClassifier(fields=classifier_dict)
                                            if 'ingress-rewrite' in rule_key:
                                                num_push_tags = 0
                                                num_pop_tags = 0
                                                for (ingress_rewrite_key,ingress_rewrite_value) in rule_value.items():
                                                    if 'pop-tags' in ingress_rewrite_key:
                                                        num_pop_tags = int(ingress_rewrite_value)
                                                    elif 'push-tag' in ingress_rewrite_key:
                                                        for (push_action_key,push_action_value) in ingress_rewrite_value[0].items():
                                                            if 'dot1q-tag' in push_action_key:
                                                                num_push_tags = num_push_tags + 1
                                                                for (dot1q_tag_key,dot1q_tag_value) in push_action_value.items():
                                                                    if 'vlan-id' in dot1q_tag_key:
                                                                        egress_vlan_id = int(dot1q_tag_value)
                                                                        egress_pbit = None
                                                                    elif 'pbit-from-tag-index' in dot1q_tag_key:
                                                                        egress_pbit = int(dot1q_tag_value)
                                                                    elif 'dei-from-tag-index' in dot1q_tag_key:
                                                                        egress_pbit = int(dot1q_tag_value)
                                                                    elif 'write-pbit-0' in dot1q_tag_key:
                                                                        egress_pbit = 0
                                                                    elif 'write-pbit' in dot1q_tag_key:
                                                                        egress_pbit = int(dot1q_tag_value)
                                                if num_pop_tags == 0 and num_push_tags > 0:
                                                    vlan_action = 'PUSH'
                                                elif num_pop_tags==1 and num_push_tags==1:
                                                    vlan_action = 'TRANSLATE'
                                                else:
                                                    vlan_action = 'POP'
                                                egress_o_tag = (egress_vlan_id != VID_VALUE_ANY and egress_vlan_id != None) and \
                                                                VlanTag(vid=egress_vlan_id, pbit=egress_pbit) or None
                                                actions_dict = {}
                                                actions_dict['vlan'] = VlanAction(VlanAction.Action[vlan_action], num_push_tags, o_vid=egress_o_tag)
                                                action = PacketAction(actions=actions_dict)  
                         
                        if '@' in interfaceIter and 'create' in interfaceIter['@']['ietf-netconf:operation']:
                            logger.info("Create subinterface is request")    

                            if dict_vlan_subiface.get(subif_name) is None:
                                dict_vlan_subiface[subif_name] = {} 
                            
                            dict_vlan_subiface[subif_name]['uni_name'] = uni_name
                            dict_vlan_subiface[subif_name]['classifier'] = classifier
                            dict_vlan_subiface[subif_name]['action'] = action
                            dict_vlan_subiface[subif_name]['qos_profile'] = qos_profile
                            

                            handlers['vlan-subif'].append(VlanSubInterfaceSetHandler)
                            handler_args['vlan-subif'].append((subif_name, uni_name, classifier, action, qos_profile))
                        
                        elif '@' in interfaceIter and 'merge' in interfaceIter['@']['ietf-netconf:operation'] or \
                            '@' in interfaceIter and default_netconf_op in interfaceIter['@']['ietf-netconf:operation']:
                           
                            logger.info("Update subinterface is request")

                            if dict_vlan_subiface.get(subif_name) is None:
                                dict_vlan_subiface[subif_name] = {}

                            # if subif_name is None:                                                  
                            #     subif_name = dict_vlan_subiface[subif_name]
                            # else:
                            #     dict_vlan_subiface[subif_name] = subif_name                                   
                            if uni_name is None:
                                uni_name = dict_vlan_subiface[subif_name]['uni_name']
                            else:
                                dict_vlan_subiface[subif_name]['uni_name'] = uni_name
                            if classifier is None:
                                classifier = dict_vlan_subiface[subif_name]['classifier']
                            else:
                                dict_vlan_subiface[subif_name]['classifier'] = classifier
                            if action is None:
                                action = dict_vlan_subiface[subif_name]['action']
                            else:    
                                dict_vlan_subiface[subif_name]['action'] = action
                            if qos_profile is None:                                                                                                                                                                                                                                                                                                                                                                                                                     
                                qos_profile = dict_vlan_subiface[subif_name]['qos_profile']
                            else:
                                dict_vlan_subiface[subif_name]['qos_profile'] = qos_profile

                            
                            handlers['vlan-subif'].append(VlanSubInterfaceDeleteHandler)
                            handler_args['vlan-subif'].append((subif_name, uni_name, classifier, action, qos_profile, True))

                            
                            handlers['vlan-subif'].append(VlanSubInterfaceSetHandler)
                            handler_args['vlan-subif'].append((subif_name, uni_name, classifier, action, qos_profile))
     
                        else:
                            
                            if dict_vlan_subiface.get(subif_name) is None:
                                dict_vlan_subiface[subif_name] = {} 
                            
                            dict_vlan_subiface[subif_name]['uni_name'] = uni_name
                            dict_vlan_subiface[subif_name]['classifier'] = classifier
                            dict_vlan_subiface[subif_name]['action'] = action
                            dict_vlan_subiface[subif_name]['qos_profile'] = qos_profile
                            
                            handlers['vlan-subif'].append(VlanSubInterfaceSetHandler)
                            handler_args['vlan-subif'].append((subif_name, uni_name, classifier, action, qos_profile))

                    if '@' in interfaceIter and 'remove' in interfaceIter['@']['ietf-netconf:operation'] or \
                        '@' in interfaceIter and 'delete' in interfaceIter['@']['ietf-netconf:operation']:

                        logger.info("Delete subinterface is request")
                        if is_interface_name_config(currentDict, interfaceIter['name']):
                            if 'ietf-interfaces:interfaces' in currentDict:
                                YangObjData = currentDict['ietf-interfaces:interfaces']
                                if 'interface' in YangObjData:
                                    for interfaceIter in currentDict['ietf-interfaces:interfaces']['interface']:
                                         if ('type' in interfaceIter and 'vlan-sub-interface' in interfaceIter['type']) and ('@' in interfaceIter and 'create' in interfaceIter['@']['ietf-netconf:operation']):
                                            
                                            subif_name = interfaceIter['name']
                                            if dict_vlan_subiface.get(subif_name) is None:
                                                return OMHStatus.OK
                                            else:    
                                                
                                                uni_name = dict_vlan_subiface[subif_name]['uni_name']
                                                classifier = dict_vlan_subiface[subif_name]['classifier']
                                                action = dict_vlan_subiface[subif_name]['action']
                                                qos_profile = dict_vlan_subiface[subif_name]['qos_profile']
                                            
                                                handlers['vlan-subif'].append(VlanSubInterfaceDeleteHandler)
                                                handler_args['vlan-subif'].append((subif_name, uni_name, classifier, action, qos_profile, False))
                                                dict_vlan_subiface.pop(subif_name)
                            


        logger.info("yang_to_omci_mapper :: extractPayload :: calling YangtoOmciMapperHandler for invoking omh_nbi handlers")

        mapperObj = YangtoOmciMapperHandler(vomci, onu)
        for i in range(len(handlers['onu'])):
            mapperObj.add_handler(handlers['onu'][i], handler_args['onu'][i])
        for i in range(len(handlers['tcont'])):
            mapperObj.add_handler(handlers['tcont'][i], handler_args['tcont'][i])
        for i in range(len(handlers['uni'])):
            mapperObj.add_handler(handlers['uni'][i], handler_args['uni'][i])
        for i in range(len(handlers['ani'])):
            mapperObj.add_handler(handlers['ani'][i], handler_args['ani'][i])
        for i in range(len(handlers['gem'])):
            mapperObj.add_handler(handlers['gem'][i], handler_args['gem'][i])
        for i in range(len(handlers['qos-policy-profile'])):
            mapperObj.add_handler(handlers['qos-policy-profile'][i], handler_args['qos-policy-profile'][i])
        for i in range(len(handlers['vlan-subif'])):
            mapperObj.add_handler(handlers['vlan-subif'][i], handler_args['vlan-subif'][i])
        return mapperObj.run()

    else:
        logger.error("copy-config:payload[target] OR edit-config:payload[delta] is None")
        return OMHStatus.ERROR_IN_PARAMETERS
 
def yang_mapper_parse_vlan_tag(vlan):
    if vlan == "any":
        return VID_VALUE_ANY
    elif vlan == "priority-tagged":
        return 0
    else: 
        return int(vlan)
    
def yang_mapper_parse_vlan_pbit(pbit):
    if pbit == "any":
        return PBIT_VALUE_ANY
    else:
        return int(pbit)
        

def is_interface_name_config(currentConfig, intf_name):
    for intf in currentConfig['ietf-interfaces:interfaces']['interface']:
        if intf['name'] == intf_name:
            return True

    return False

def get_xpath_handler(xpath):
    if xpath == 'ietf-hardware:hardware-state':
        return GetHardwareStateHandler
    elif xpath == 'ietf-interfaces:interfaces-state':
        return GetInterfacesStateHandler
    else:
        logger.info("xpath {} is not currently supported, and will be replaced by interfaces-states".format(xpath))
        return GetInterfacesStateHandler


class YangtoOmciMapperHandler:
    def __init__(self, vomci : 'VOmci', onu: 'OnuDriver'):
        """
        Invoke omh_nbi handlers
        Args:
            onu: onu driver instance
        """
        self._vomci = vomci
        self._onu = onu
        self._status = OMHStatus.OK
        self._default_timeout = 3.0
        self._default_retries = 2
        self._handler_types = []
        self._handler_args = []
        self._subscription_id = None
        self._xpaths= []

    def set_subscription_xpaths(self, subscription_id, xpaths):
        self._subscription_id = subscription_id
        self._xpaths = xpaths

    def add_handler(self, handler_type: OmhHandler, handler_args):
        self._handler_types.append(handler_type)
        self._handler_args.append(handler_args)

    class OmhNbiHandler(OmhHandler):
        """ OmhNbiHandler that executes the requested sequence of OMH handlers as subsidiaries """
        def __init__(self, onu: OnuDriver, handler_types: Tuple[OmhHandler, ...], handler_args: Tuple[Any, ...]):
            handler_type_list = [t.__name__ for t in handler_types]
            super().__init__(name='OmhNbiHandler', onu=onu, description=' {}'.format(handler_type_list))
            self._handler_types = handler_types
            self._handler_args = handler_args

        def set_subscription_xpaths(self, subscription_id, xpaths):
            self._subscription_id = subscription_id
            self._xpaths = xpaths

        def run_to_completion(self) -> OMHStatus:
            logger.info(self.info())
            length = len(self._handler_types)
            logger.info("Number of omh_nbi handlers : {}".format(length))
            for i in range(length):
                handler_type = self._handler_types[i]
                args = self._handler_args[i]
                handler = args is None and handler_type(self._onu) or handler_type(self._onu, *args)
                status = self.run_subsidiary(handler)
                if status != OMHStatus.OK:
                    break
            return status

    def run(self) -> OMHStatus:
        if len(self._handler_types) == 0:
            logger.info('No handlers to run')
            return OMHStatus.OK

        self._onu.set_flow_control(self._default_retries, self._default_timeout)
        handler = YangtoOmciMapperHandler.OmhNbiHandler(self._onu, self._handler_types, self._handler_args)
        handler.set_subscription_xpaths(self._subscription_id, self._xpaths)
        logger.info("YangtoOmciMapperHandler: starting execution in the background")
        handler.start(self._vomci.trigger_kafka_response)

        logger.info("YangtoOmciMapperHandler: Finished execution. Status: {}".format(handler.status.name))

        return self._status

