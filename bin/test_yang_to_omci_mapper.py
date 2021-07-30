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
#Yang to OMCI test handlers for UNI, TCONT, GEM port, QOS & Vlan sub-interfaces
#
#Created by Karthik(Altran) & Maheswari (Altran) on 27th August 2020
#

import logging
import json
from omcc.grpc.grpc_client import GrpcClientChannel
from mapper.yang_to_omci_mapper import extractPayload
from omci_logger import OmciLogger
from omh_nbi.handlers.onu_activate import OnuActivateHandler
logger = OmciLogger.getLogger(__name__)

def test_extractPayload():
    polt_host = '10.66.1.2'
    polt_port = 8433
    vomci_name = 'vomci1'
    cterm_name = 'channeltermination.1'
    onu_id = 0
    onu_name = 'onuTrial'
    tci = 1
    log_level = 2

    loglevel_map = {0: logging.WARN, 1: logging.INFO, 2: logging.DEBUG}
    OmciLogger(level=loglevel_map[log_level])
    logger = OmciLogger.getLogger(__name__)

    logger.info("test_YangtoOmciMapper: connecting to the pOLT {}:{}".format(polt_host, polt_port))
    channel = GrpcClientChannel(vomci_name)
    ret_val = channel.connect(polt_host, polt_port)
    if not ret_val:
        logger.info("test_YangtoOmciMapper: connection failed with pOLT")
        return -1
    olt = channel.add_managed_onu(channel.remote_endpoint_name, onu_name, (cterm_name, onu_id), tci)
    logger.info("test_YangtoOmciMapper: connected to the pOLT: {}".format(olt.id))
    onu = olt.OnuGet((cterm_name, onu_id))
    activate_handler = OnuActivateHandler(onu)
    status = activate_handler.run()
    logger.info("test_YangtoOmciMapper: activate_handler status: {}".format(status))

    payload = '{"identifier": "0", "operation": "edit-config", ' \
              '"delta":{"bbf-qos-classifiers:classifiers": {"classifier-entry": [{"name" : "classifier1",  ' \
              '"classifier-action-entry-cfg": [{"action-type": "bbf-qos-cls:scheduling-traffic-class", "scheduling-traffic-class": 0}], ' \
              '"match-criteria": {"tag": [{"index": 0, "in-pbit-list": 0}]}}]}, ' \
              '"bbf-qos-policies:policies": {"policy": [{"name" : "policy1", "classifiers": [{"name":"classifier1"}]}]}, ' \
              '"bbf-qos-policies:qos-policy-profiles": {"policy-profile": [{"name": "profile1", "policy-list": [{"name": "policy1"}]}]}, ' \
              '"ietf-interfaces:interfaces": {"interface": [{"name": "uni.1", "type": "ianaift:ethernetCsmacd", ' \
              '"enabled": "true", "port-layer-if": "ontUni_ont1_1_1", "ingress-qos-policy-profile": "profile1"}, ' \
              '{"name": "enet_vlan_ont1", "type": "bbfift:vlan-sub-interface", "subif-lower-layer": {"interface" : "uni.1"}, ' \
              '"inline-frame-processing": {"ingress-rule": {"rule": [{"name": "rule1", "priority": "100", "flexible-match": {"match-criteria": "untagged"}, ' \
              '"ingress-rewrite": {"pop-tags" : 0, "push-tag": [{"index": 0, "dot1q-tag": {"tag-type": "bbf-dot1qt:c-vlan", "vlan-id": 100, "pbit-from-tag-index": 0}}]}}]}}, ' \
              '"ingress-qos-policy-profile": "profile1"}]}, "bbf-xpongemtcont:xpongemtcont": {"tconts": {"tcont": [{"name": "tcont.1", "alloc-id": 1024}]}, ' \
              '"gemports": {"gemport": [{"name": "gemport.1", "interface": "uni.1", "gemport-id": 1025, "traffic-class": 0, "tcont-ref": "tcont.1"}]}}}}'

    payloadDict = json.loads(payload)
    extractPayload(onu_name, olt.id, payloadDict)

    if onu.olt.channel is not None:
        onu.olt.channel.disconnect()

def main():
    test_extractPayload()

if __name__ == '__main__':
    main()
