# Copyright 2022 Broadband Forum
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
# Created by Jafar Hamin (Nokia) in Fubruady 2023

from database.omci_me import ME
from database.omci_me_types import omci_me_class
import datetime
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

me_to_yang_value = {
    'UNCOMMITTED': 'false',
    'COMMITTED': 'true',
    'INACTIVE': 'false',
    'ACTIVE': 'true',
    'INVALID': 'false',
    'VALID': 'true',
    'UNLOCK': 'up',
    'LOCK': 'down',
    'ENABLED': 'up',
    'DISABLED': 'down',    
    }

def software_image_state(committed, active, valid):
    if active or committed:
        return "in-use"
    if valid:
        return "available"
    return "not-available"

def get_software_revisions(onu):
    onu_name = onu.onu_name
    sw_images = onu.get_all_instances(omci_me_class['SW_IMAGE'])
    result = {"revision" : []}
    for sw in sw_images:
        revision = {
            "id": sw.me_inst,
            "alias": onu_name + '-software-rev' + str(sw.me_inst),
            "state": software_image_state(me_to_yang_value[sw.is_committed], me_to_yang_value[sw.is_active], me_to_yang_value[sw.is_valid]),
            "version": sw.version.decode("utf-8"),
            "product-code": sw.product_code.decode("utf-8"),
            "hash": sw.image_hash.decode("utf-8"),
            "is-committed": me_to_yang_value[sw.is_committed],
            "is-active": me_to_yang_value[sw.is_active],
            "is-valid": me_to_yang_value[sw.is_valid]
        }
        result["revision"].append(revision)
    return result 
    
def get_yang_hardware_state(onu):
    onu_name = onu.onu_name
    revisions = get_software_revisions(onu)
    onu_g = onu.get_all_instances(omci_me_class['ONU_G'])
    onu2_g = onu.get_all_instances(omci_me_class['ONU2_G'])
    result = {
        "ietf-hardware-state:hardware": {
            "component": [
                {
                    "name": onu_name,
                    "model-name": onu2_g[0].equipment_id.decode("utf-8"),
                    "mfg-name": str(onu_g[0].vendor_id),
                    "serial-num": onu_g[0].serial_number.decode("utf-8")
                }
            ]
        },
        "ietf-hardware:hardware": {
            "component": [
                {
                    "name": onu_name + '-software',
                    "bbf-software-management:software": {
                        "software": [
                            {
                                "name": onu_name,
                                "revisions": revisions
                            }
                        ]
                    }
                }
            ]
        }
    }
    return result 

def generate_unique_name(name, me_inst, configured_names):
    while name in configured_names:
        name += "_" + str(me_inst)
    return name
   
def generate_uni_name(onu_name, me_inst, configured_names):
    name = "uni" + str(me_inst) + "_" + onu_name
    return generate_unique_name(name, me_inst, configured_names)

def generate_uni_port_name(onu_name, me_inst, configured_names):
    name = "port_uni" + str(me_inst) + "_" + onu_name
    return generate_unique_name(name, me_inst, configured_names)

def generate_ani_name(onu_name, me_inst, configured_names):
    name = "ani" + str(me_inst) + "_" + onu_name
    return generate_unique_name(name, me_inst, configured_names)

def get_pm_uni_interface(onu):
    unis_pm_down_me = {}
    unis_pm_up_me = {}
    unis = onu.get_all_instances(omci_me_class['PPTP_ETH_UNI'])
    mbpcds = onu.get_all_instances(omci_me_class['MAC_BRIDGE_PORT_CONFIG_DATA'])
    pm_ups = onu.get_all_instances(omci_me_class['ETH_FRAME_UPSTREAM_PM'])
    pm_downs = onu.get_all_instances(omci_me_class['ETH_FRAME_DOWNSTREAM_PM'])
    for mbpcd in mbpcds:
        if str(mbpcd.tp_type) == 'PHY_PATH_TP_ETH_UNI':
            uni_inst = mbpcd.tp_ptr
            mbpcd_inst = mbpcd.me_inst
            for pm_down in pm_downs:
                if pm_down.me_inst == mbpcd_inst:
                    unis_pm_down_me[uni_inst] = pm_down
                    break
            for pm_up in pm_ups:
                if pm_up.me_inst == mbpcd_inst:
                    unis_pm_up_me[uni_inst] = pm_up
                    break

    unis_pm = {}
    for uni in unis:
        uni_inst = uni.me_inst
        unis_pm[uni_inst] = {}
        if uni_inst not in unis_pm_down_me or uni_inst not in unis_pm_up_me:
            continue
        pm_down = unis_pm_down_me[uni_inst]
        pm_up = unis_pm_up_me[uni_inst]
        unis_pm[uni_inst] = {
              "intervals-15min":{
                "history":[
                  {
                    "interval-number": 1,
                    "invalid-data-flag": "false",
                    "measured-time": 900,
                    "in-broadcast-pkts": pm_up.up_broadcast_packets,
                    "in-multicast-pkts": pm_up.up_multicast_packets,
                    "in-octets": pm_up.up_octets,
                    "out-broadcast-pkts": pm_down.dn_broadcast_packets,
                    "out-multicast-pkts": pm_down.dn_multicast_packets,
                    "out-octets": pm_down.dn_octets,
                    "time-stamp": str(datetime.datetime.now())
                  }
                ]
              }
        }
    return unis_pm

def get_uni_interfaces(onu):
    unis = onu.get_all_instances(omci_me_class['PPTP_ETH_UNI'])
    result = []
    configured_names = set()
    for uni in unis:
        uni_name = uni.user_name
        if uni_name is not None:
            configured_names.add(uni_name)
    unis_pm = get_pm_uni_interface(onu)
    for uni in unis:
        uni_name = uni.user_name
        if uni_name is None:
            uni_name = generate_uni_name(onu.onu_name, uni.me_inst, configured_names)
        uni_port_name = uni.hd_name
        if uni_port_name is None:
            uni_port_name = generate_uni_port_name(onu.onu_name, uni.me_inst, set())
        interface = {
            "name": uni_name,
            "type": "iana-if-type:ethernetCsmacd",
            "bbf-interface-port-reference:port-layer-if": [uni_port_name],
            "admin-status": me_to_yang_value[uni.admin_state],
            "oper-status": me_to_yang_value[uni.oper_state]
        }
        if uni.me_inst in unis_pm:
            interface["bbf-interfaces-performance-management:performance"] = unis_pm[uni.me_inst]
        result.append(interface)
    return result 

def get_ani_interfaces(onu):
    anis = onu.get_all_instances(omci_me_class['ANI_G'])
    result = []
    configured_names = set()
    for ani in anis:
        ani_name = ani.user_name
        if ani_name is not None:
            configured_names.add(ani_name)
    for ani in anis:
        ani_name = ani.user_name
        if ani_name is None:
            ani_name = generate_ani_name(onu.onu_name, ani.me_inst, configured_names)
        interface = {
            "name": ani_name,
            "type": "bbf-xpon-if-type:ani",
            "admin-status": "up",
            "oper-status": "up"
        }
        result.append(interface)
    return result 

def get_yang_interfaces_state(onu):
    interfaces = get_uni_interfaces(onu)
    interfaces.extend(get_ani_interfaces(onu))
    result = {
            "ietf-interfaces:interfaces-state": {
                "interface": interfaces
            }
        }
    return result



def get_all_alarms_state(onu):

    def get_resource(me,alarm):
        resource = alarm.resource + "[name='{}']"
        if alarm.resource == "/ietf-hardware:hardware/component":
            resource = resource.format(me.hd_name)
        if alarm.resource == "/ietf-interfaces:interfaces/interface":
            resource = resource.format(me.user_name)
        return resource

    result = {
        "ietf-alarms:alarms" : {
            "alarm-list" : {
                "number-of-alarms" : 0,
                "last-changed" : "",
                "alarm": 0*[{}]
            }
        }
    }

    alarm_obj = {
        "resource" : "",
        "alarm-type-id" : "",
        "alarm-type-qualifier": "",
        "status-change": [{}]
    }

    status_change_obj = {
        "time": "",
        "perceived-severity": "",
        "alarm-text": ""
    }
    d = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    no_ms = d.replace(microsecond=0)
    time =  no_ms.isoformat() 

    number_of_alarms = 0
    for me_class in onu.get_all_me_classes():
        for me in onu.get_all_instances(me_class):
            if hasattr(me,"alarms"):
                for alarm in me.alarms:
                    if alarm.get_state() is True:
                        #constroi status_change_obj com o me
                        status_change_obj["time"] = time
                        status_change_obj["perceived-severity"] = "major"
                        status_change_obj["alarm-text"] = alarm.description + " detected."

                        #adiciona alarm_obj ao "alarm" do result
                        alarm_obj["resource"] = get_resource(me,alarm)
                        alarm_obj["alarm-type-id"] = alarm.name
                        alarm_obj["status-change"] = [status_change_obj.copy()]

                        result["ietf-alarms:alarms"]["alarm-list"]["alarm"].append(alarm_obj.copy())
                        number_of_alarms += 1

    result["ietf-alarms:alarms"]["alarm-list"]["number-of-alarms"] = number_of_alarms
    result["ietf-alarms:alarms"]["alarm-list"]["last-changed"] = time
    return result


def get_yang_response(onu, filter):
    result = {}
    if 'ietf-hardware:hardware-state' in filter:
        hardware_state = get_yang_hardware_state(onu)
        result.update(hardware_state)
    if 'ietf-interfaces:interfaces-state' in filter:
        interfaces_state = get_yang_interfaces_state(onu)
        result.update(interfaces_state)
    if 'ietf-alarms:alarms' in filter:
        alarms_state = get_all_alarms_state(onu)
        result.update(alarms_state)
    return result
