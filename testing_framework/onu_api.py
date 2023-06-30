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
import json
import subprocess
import subprocess
import time

logger = logging.getLogger('voltmf-simu')
logging.basicConfig(level=logging.INFO, format='%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


def onu_sim_rest_api(socket, api, request):
    url = "http://" + socket + "/" + api
    cmd = "curl -X POST " + url + " -H 'Content-Type: application/json' -d '" + json.dumps(request) +"'"
    attempts = 3
    while attempts > 0:
        try:
            result = subprocess.run(cmd, shell=True, timeout= 5, capture_output=True, text=True)
            output = result.stdout
            if output == '':
                logger.warning('Failure in calling ONU-SIM REST API: %s', url)
            else:
                break
        except subprocess.TimeoutExpired:
            logger.warning('Time out in calling ONU-SIM REST API: %s', url)
        attempts -= 1
        time.sleep(5)
    if attempts == 0 or output == '':
        return None, False
    output = json.loads(output)
    success = True
    if 'status' in output and output['status'] == 500:
        success = False
    return output, success

# def onu_sim_rest_api(api, request, timeout=5):
#     url = "http://172.16.0.6:3000/" + api
#     response = requests.post(url, json = request)
#     success = True if response.status_code == 200 else False
#     if success == False:
#         logger.error('Failed request to URL: %s \n %s', url, response.text)
#     return response.json(), success

def action_on_onu(request, socket):
    logger.info('Sending action request: \n%s\n', request)
    response, success = onu_sim_rest_api(socket, 'onu/action_on_mes', request)
    if success == False:
        logger.info('Failed in sending action request: %s', request)
        return False
    logger.info('ONU response: \n%s\n', response)
    return response

def onu_send_action(onu_id, action, class_id, instance_id, attributes):
    attrs = []
    for key in attributes:
        attr = {
                    "index": key,
                    "value": attributes[key]
                }
        attrs.append(attr)
    request = {
        "requests":[
            {
                "onu_id": onu_id,
                "action": action,
                "class_id": class_id,
                "instance_id": instance_id,
                "attributes": attrs
            }
        ]
    }
    response = action_on_onu(request, ONU_SIM_SOCKET[str(onu_id)])
    if response == False:
        return None, False
    return response, response_statuses(response)

def onu_get_me_attribute(onu_id, class_id, instance_id, attribute_index):
    response, status = onu_send_action(onu_id, OMCI.GET, class_id, instance_id, {attribute_index:0})
    if status != 0:
        logger.warning('OMCI response result is not OK')
        return None
    for attr in response["responses"][0]["attributes"]:
        if attr["index"] == attribute_index:
            return attr["value"]
    return None

def onu_get_compare_me_attributes(onu_id, class_id, instance_id, attributes):
    response, status = onu_send_action(onu_id, OMCI.GET, class_id, instance_id, attributes)
    if status != 0:
        logger.warning('OMCI response result is not OK')
        return False
    resp_attrs = response["responses"][0]["attributes"]
    for key in attributes:
        for resp_attr in resp_attrs:
            if int(resp_attr["index"]) == key:
                if resp_attr["value"] != attributes[key]:
                    return False
    return True

def onu_me_instance_not_exists(onu_id, class_id, instance_id):
    _, status = onu_send_action(onu_id, OMCI.GET, class_id, instance_id, {1:0})
    return status == 5

def response_statuses(response):
    status = 0
    for res in response["responses"]:
        status += int(res["status"])
    return status


class OMCI:

    SET = "SET"
    CREATE = "CREATE"
    GET = "GET"
    DELETE = "DELETE"

    SW_IMAGE_ME_ID = 7
    PPTP_ETH_UNI_ME_ID = 11
    MAC_BRIDGE_PORT_CONFIG_DATA_ME_ID = 47
    EVTOCD_ME_ID = 171
    ETH_FRAME_DOWNSTREAM_PM = 321
    ETH_FRAME_UPSTREAM_PM = 322

ONU_SIM_SOCKET = {'1': '172.16.0.61:3018', '2': '172.16.0.61:3018', '3': '172.16.0.62:3019', '4': '172.16.0.62:3019', 
              '5': '172.16.0.63:3020', '6': '172.16.0.63:3020', '7': '172.16.0.64:3021', '8': '172.16.0.64:3021'}