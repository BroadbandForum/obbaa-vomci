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
# Created by Jafar Hamin (Nokia) in August 2023

from asyncio import subprocess
import logging
from time import time
import time
import re
import json
import subprocess

logger = logging.getLogger('voltmf-simu')
logging.basicConfig(level=logging.INFO, format='%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def voltmf_rest_api(api, request):
    url = "http://172.16.0.7:3001/" + api
    cmd = "curl -X POST " + url + " -H 'Content-Type: application/json' -d '" + json.dumps(request) +"'"
    attempts = 3
    while attempts > 0:
        try:
            result = subprocess.run(cmd, shell=True, timeout= 5, capture_output=True, text=True)
            output = result.stdout
            if output == '':
                logger.warning('Failure in calling vOLTMF-SIM REST API: %s', url)
            else:
                break
        except subprocess.TimeoutExpired:
            logger.warning('Time out in calling vOLTMF-SIM REST API: %s', url)
        attempts -= 1
    if attempts == 0 or output == '':
        return None, False
    output = json.loads(output)
    success = True
    if 'status' in output and output['status'] == 500:
        success = False
    return output, success

# def voltmf_rest_api(api, request):
#     url = "http://172.16.0.7:3001/" + api
#     response = requests.post(url, json = request)
#     success = True if response.status_code == 200 else False
#     if success == False:
#         logger.error('Failed request to URL: %s', url)
#     return response.json(), success

def send_yang_request(request):
    logger.info('Sending YANG request: \n%s\n', request)
    response, success = voltmf_rest_api('send_yang_request', request)
    if success == False:
        logger.info('Failed in sending YANG request: %s', request)
        return False
    result =response['result']
    if result == 'False':
        logger.info('False result in sending YANG request: %s', request)
        return False
    return True

def voltmf_keep_getting_received_response(request):
    logger.info('Keept getting received YANG response ...')
    attempts = 30
    while attempts > 0:
        attempts -= 1
        response, success = voltmf_rest_api('get_vnf_response', request)
        if success:
            result = response['result']
            if result != 'None':
                logger.info('Received YANG response: \n%s\n', result)
                return result
        time.sleep(1)
    logger.info('No YANG response is received')
    return None


def send_action(action, object_type, object_name, expected_response=None):
    request = {}
    msg_id = MsgId.get_next()
    request['msg_id'] = msg_id
    request['request_type'] = MessageData.ACTION
    request['sender_name'] = VoltmfInfo.VOLTMF1['name']
    request['recipient_name'] = object_name
    request['object_type'] = object_type
    request['object_name'] = object_name
    request['action'] = action
    if not send_yang_request(request):
        return False
    yang_response = voltmf_keep_getting_received_response({'msg_id': msg_id, 'vnf_name': object_name})
    if yang_response is None:
        return False
    expected_yang_response = expected_response    
    if expected_response is None:
        expected_yang_response = read_eval_file("yang_data/vomci_requests/success_action_response.yang")
    return yangs_are_similar(yang_response, expected_yang_response)

def create_onu(onu):
    action = read_eval_file("yang_data/vomci_requests/create_onu.json",
                            {"ONU_NAME": onu['name']})
    return send_action(action, MessageData.VOMCI_FUNCTION, onu['vomci']['name'])

def delete_onu(onu):
    action = read_eval_file("yang_data/vomci_requests/delete_onu.json",
                            {"ONU_NAME": onu['name']})
    return send_action(action, MessageData.VOMCI_FUNCTION, onu['vomci']['name'])

def set_onu_communication_to_vomci_with_proxy(onu):
    action = read_eval_file("yang_data/vomci_requests/set_onu_comm.json",
                {"ONU_NAME": onu['name'], "ONU_ID": onu['id'],
                 "OLT_NAME": onu['olt']['name'], "OLT_CONNECTION": onu['olt']['nbi_connection']})
    return send_action(action, MessageData.VOMCI_FUNCTION, onu['vomci']['name'])

def set_onu_communication_to_vproxy(onu):
    action = read_eval_file("yang_data/vproxy_requests/set_onu_comm.json",
                {"ONU_NAME": onu['name'], "ONU_ID": onu['id'], "VOMCI_ENDPOINT": onu['vomci']['endpoint'],
                 "OLT_NAME": onu['olt']['name'], "OLT_CONNECTION": onu['olt']['connection']})
    return send_action(action, MessageData.VOMCI_PROXY, onu['olt']['nbi']['name'])

def set_onu_communication_to_vomci_no_proxy(onu):
    action = read_eval_file("yang_data/vomci_requests/set_onu_comm.json",
                {"ONU_NAME": onu['name'], "ONU_ID": onu['id'],
                 "OLT_NAME": onu['olt']['connection'], "OLT_CONNECTION": onu['olt']['connection']})
    return send_action(action, MessageData.VOMCI_FUNCTION, onu['vomci']['name'])

def get_and_clear_vomci_notifications(vomci_name):
    logger.info('Get received notifications ...')
    request = {'vnf_name': vomci_name}
    response, success = voltmf_rest_api('get_and_clear_vnf_notifications', request)
    if success == False:
        logger.info('Failed in getting received notifications: %s', request)
        return False
    result = response['result']
    logger.info('Received notifications: \n%s\n', result)
    return response['result']

def get_and_clear_vomci_telemetry(vomci_name):
    logger.info('Get received telemetry notifications ...')
    request = {'vnf_name': vomci_name}
    response, success = voltmf_rest_api('get_and_clear_vnf_telemetry', request)
    if success == False:
        logger.info('Failed in getting received telemetry notifications: %s', request)
        return False
    result = response['result']
    logger.info('Received telemetry notifications: \n%s\n', result)
    return response['result']

def check_alignment_notification(onu, alignment_status='unaligned'):
    notifications = get_and_clear_vomci_notifications(onu['vomci']['name'])
    if len(notifications) < 1:
        return False
    last_notification = notifications[len(notifications)-1].replace('\\"', '"')
    expected_notification = read_eval_file("yang_data/vomci_requests/alignment_report.json",        
        {"ONU_NAME": onu['name'], "ALIGNMENT_STATUS": alignment_status})
    print('expected_notification = ', expected_notification)

    expected_notification = 'notification { data: "' + expected_notification + '"}'
    first_notification_no_tstame = remove_yang_attribute(last_notification, 'event-time')
    expected_notification_no_tstame = remove_yang_attribute(expected_notification, 'event-time')
    print('first_notification_no_tstame = ', first_notification_no_tstame)
    print('expected_notification_no_tstame = ', expected_notification_no_tstame)
    return yangs_are_similar(first_notification_no_tstame, expected_notification_no_tstame)

def remove_first_yang_attribute(yang, attribute_name):
    first_index = yang.find('"' + attribute_name + '"')
    if first_index == -1:
        return yang
    index = yang.find('"', first_index + 1)
    index = yang.find('"', index + 1)
    index = yang.find('"', index + 1)
    last_index = yang.find(',', index + 1)
    result = yang[:first_index] + yang[last_index + 1:]
    return result

def remove_yang_attribute(yang, attribute_name):
    while yang.find('"' + attribute_name + '"') != -1:
        yang = remove_first_yang_attribute(yang, attribute_name)
    return yang

def voltmf_send_update_config(update_config_type, delta_config_path, object_type, object_name, current_config_path=None, onu=None, expected_yang_response_path=None):
    logger.info('Update configuration of ONU: %s current configuration: %s , delta configuration: %s', onu, current_config_path, delta_config_path)
    if current_config_path is None:
        current_config = None
    else:
        current_config = read_configuration_file(current_config_path)
    delta_config = read_configuration_file(delta_config_path)
    request = {}
    msg_id = MsgId.get_next()
    request['msg_id'] = msg_id
    request['request_type'] = MessageData.UPDATE_CONFIG
    request['update_config_type'] = update_config_type
    request['sender_name'] = VoltmfInfo.VOLTMF1['name']
    request['recipient_name'] = object_name
    request['current_config'] = current_config
    request['delta_config'] = delta_config
    if onu is None:
        request['object_type'] = object_type
        request['object_name'] = object_name
    else:
        request['object_type'] = MessageData.ONU
        request['object_name'] = onu['name']
    if send_yang_request(request) == False:
        return False
    yang_response = voltmf_keep_getting_received_response({'msg_id': msg_id, 'vnf_name': object_name})
    if yang_response is None:
        return False
    if expected_yang_response_path is None:
        expected_yang_response = read_eval_file("yang_data/vomci_requests/success_update_config_response.yang")
    else:
        expected_yang_response = read_eval_file(expected_yang_response_path)
    return yangs_are_similar(yang_response, expected_yang_response)

def voltmf_send_update_config_inst_to_vomci(delta_config_path, current_config_path=None, onu=None, expected_yang_response_path=None):
    return voltmf_send_update_config(MessageData.UPDATE_CONFIG_INST, delta_config_path, MessageData.VOMCI_FUNCTION, onu['vomci']['name'], current_config_path, onu, expected_yang_response_path)

def voltmf_send_update_config_replica_to_vomci(delta_config_path, current_config_path=None, onu=None, expected_yang_response_path=None):
    return voltmf_send_update_config(MessageData.UPDATE_CONFIG_REPLICA, delta_config_path, MessageData.VOMCI_FUNCTION, onu['vomci']['name'], current_config_path, onu, expected_yang_response_path)

def voltmf_send_update_config_inst_to_vproxy(delta_config_path, current_config_path=None, onu=None, expected_yang_response_path=None):
    return voltmf_send_update_config(MessageData.UPDATE_CONFIG_INST, delta_config_path, MessageData.VOMCI_PROXY, VproxyInfo.VPROXY1['name'], current_config_path, onu, expected_yang_response_path)

def voltmf_send_update_config_replica_to_vproxy(delta_config_path, current_config_path=None, onu=None, expected_yang_response_path=None):
    return voltmf_send_update_config(MessageData.UPDATE_CONFIG_REPLICA, delta_config_path, MessageData.VOMCI_PROXY, VproxyInfo.VPROXY1['name'], current_config_path, onu, expected_yang_response_path)

def voltmf_send_get_data_request(get_request, recipient_name, object_type, object_name):
    request = {}
    msg_id = MsgId.get_next()
    request['msg_id'] = msg_id
    request['request_type'] = MessageData.GET_DATA
    request['sender_name'] = VoltmfInfo.VOLTMF1['name']
    request['recipient_name'] = recipient_name
    request['filter'] = get_request
    request['object_type'] = object_type
    request['object_name'] = object_name
    send_yang_request(request)
    response = voltmf_keep_getting_received_response({'msg_id': msg_id, 'vnf_name': recipient_name})
    return response.replace('\\"', '"')

def voltmf_send_get_onu_data_request(get_request, onu):
    return voltmf_send_get_data_request(get_request, onu['vomci']['name'], MessageData.ONU, onu['name'])

def voltmf_send_get_vomci_data_request(get_request, vomci_name):
    return voltmf_send_get_data_request(get_request, vomci_name, MessageData.VOMCI_FUNCTION, vomci_name)

def voltmf_send_get_onu_data_request_check_response(get_request, expected_response_path, onu):
    yang_response = voltmf_send_get_onu_data_request(get_request, onu)
    if yang_response is None:
        return False
    expected_yang_response = make_get_resp_file(expected_response_path)
    if not yangs_are_similar(yang_response, expected_yang_response):
        return False
    return True

def eval_expressions(str, globals1):
    for f in re.findall("[$].*?[$]", str):
        evaluated = eval(f[1:-1], globals1)
        if evaluated is None:
            logging.error('{} not found'.format(f[2:-2]))
        str = str.replace(f, evaluated)
    return str

def read_eval_file(path, globals=None):
    with open("./testing_framework/data/" + path, 'r') as f:
        content = f.read()
    if globals is not None:
        content = eval_expressions(content, globals)
    return content.replace(' ', '').replace('\n', '')

def read_configuration_file(path, globals=None):
    content = read_eval_file(path, globals)
    return content.replace('"', '\"').replace('\t', '')

def make_get_resp_file(path, globals=None):
    content = read_eval_file(path, globals)
    result = 'response { get_resp { data: "' + content + '"}}'
    return result

def yangs_are_similar(yang_response, expected_yang_response):
    yang_response = yang_response.replace(' ', '').replace('\n', '')
    expected_yang_response = expected_yang_response.replace(' ', '').replace('\n', '')
    similar = yang_response == expected_yang_response
    if similar == False:
        logging.error('\nExpected respons:\n{}\n\nIs not equal with the received response:\n\n{}'.format(expected_yang_response, yang_response))
    return similar

def create_telemetry_subscription(onu, expected_response):
    action = read_eval_file("yang_data/telemetry/establish_subscription.json",
                {"ONU_NAME": onu['name']})
    return send_action(action, MessageData.VOMCI_FUNCTION, onu['vomci']['name'], expected_response)

def remove_telemetry_subscription(onu, subscription_id):
    action = read_eval_file("yang_data/telemetry/remove_subscription.json",
                {"ONU_NAME": onu['name'], "SUBSCRIPTION_ID": subscription_id})
    expected_response = read_eval_file("yang_data/telemetry/subscription_response.yang",
                {"ONU_NAME": onu['name'], "SUBSCRIPTION_ID": subscription_id}) 
    return send_action(action, MessageData.VOMCI_FUNCTION, onu['vomci']['name'], expected_response)

def check_telemetry_notification(onu, expected_subscription_id):
    notifications = get_and_clear_vomci_telemetry(onu['vomci']['name'])
    if len(notifications) < 1:
        return False
    last_notification = notifications[len(notifications)-1].replace('\\"', '"')
    expected_notification = read_eval_file("yang_data/telemetry/notification.json",        
        {"ONU_NAME": onu['name'], "SUBSCRIPTION_ID": str(expected_subscription_id)})
    expected_notification = 'notification { data: "' + expected_notification + '"}'
    last_notification_no_tstame = remove_yang_attribute(last_notification, 'collection-time')
    last_notification_no_tstame = remove_yang_attribute(last_notification_no_tstame, 'time-stamp')
    expected_notification_no_tstame = remove_yang_attribute(expected_notification, 'collection-time')
    expected_notification_no_tstame = remove_yang_attribute(expected_notification_no_tstame, 'time-stamp')
    return yangs_are_similar(last_notification_no_tstame, expected_notification_no_tstame)

def send_initial_config(onu, config):
    request = {}
    msg_id = MsgId.get_next()
    request['msg_id'] = msg_id
    request['request_type'] = MessageData.REPLACE_CONFIG
    request['sender_name'] = VoltmfInfo.VOLTMF1['name']
    request['recipient_name'] = onu['vomci']['name']
    request['object_type'] = MessageData.ONU
    request['object_name'] = onu['name']
    request['config'] = config
    if not send_yang_request(request):
        return False
    yang_response = voltmf_keep_getting_received_response({'msg_id': msg_id, 'vnf_name': onu['vomci']['name']})
    if yang_response is None:
        return False
    expected_yang_response = read_eval_file("yang_data/vomci_requests/success_replace_config_response.yang")
    return yangs_are_similar(yang_response, expected_yang_response)

class MsgId:
    counter = 1

    def get_next():
        MsgId.counter +=1
        return str(MsgId.counter)

class MessageData:
    VOMCI_FUNCTION = 'VOMCI_FUNCTION'
    VOMCI_PROXY = 'VOMCI_PROXY'
    ONU = 'ONU'

    ACTION = 'ACTION'
    REPLACE_CONFIG = 'REPLACE_CONFIG'
    UPDATE_CONFIG = 'UPDATE_CONFIG'
    UPDATE_CONFIG_INST = 'UPDATE_CONFIG_INST'
    UPDATE_CONFIG_REPLICA = 'UPDATE_CONFIG_REPLICA'
    GET_DATA = 'GET_DATA'

class VoltmfInfo:
    VOLTMF1 = {'name': 'vOLTMF'}

class VomciInfo:
    VOMCI1 = {'name': 'vomci-vendor-1', 'endpoint': 'obbaa-vomci'}
    VOMCI2 = {'name': 'vomci-vendor-2', 'endpoint': 'obbaa-vomci2'}
    VOMCI3 = {'name': 'vomci-vendor-3', 'endpoint': 'obbaa-vomci3'}

class VproxyInfo:
    VPROXY1 = {'name': 'proxy-1'}

class OltInfo:
    OLT1 = {'name': 'OLT1', 'connection': 'olt-grpc-1', 'nbi': VproxyInfo.VPROXY1, 'nbi_connection': 'proxy-grpc-1'}
    OLT2 = {'name': 'OLT2', 'connection': 'olt-grpc-2', 'nbi': VproxyInfo.VPROXY1, 'nbi_connection': 'proxy-grpc-3'}
    OLT3 = {'name': 'OLT3', 'connection': 'olt-grpc-3', 'nbi': VomciInfo.VOMCI3}
    OLT4 = {'name': 'OLT4', 'connection': 'olt-grpc-4', 'nbi': VomciInfo.VOMCI3}

class OnuInfo:
    ONU1 = {'name': 'ONU1', 'id':'1', 'olt': OltInfo.OLT1, 'vomci': VomciInfo.VOMCI1}
    ONU2 = {'name': 'ONU2', 'id':'2', 'olt': OltInfo.OLT1, 'vomci': VomciInfo.VOMCI1}
    ONU3 = {'name': 'ONU3', 'id':'3', 'olt': OltInfo.OLT2, 'vomci': VomciInfo.VOMCI2}
    ONU4 = {'name': 'ONU4', 'id':'4', 'olt': OltInfo.OLT2, 'vomci': VomciInfo.VOMCI2}
    ONU5 = {'name': 'ONU5', 'id':'5', 'olt': OltInfo.OLT3, 'vomci': VomciInfo.VOMCI3}
    ONU6 = {'name': 'ONU6', 'id':'6', 'olt': OltInfo.OLT3, 'vomci': VomciInfo.VOMCI3}
    ONU7 = {'name': 'ONU7', 'id':'7', 'olt': OltInfo.OLT4, 'vomci': VomciInfo.VOMCI3}
    ONU8 = {'name': 'ONU8', 'id':'8', 'olt': OltInfo.OLT4, 'vomci': VomciInfo.VOMCI3}
