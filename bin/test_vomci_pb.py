import logging
import threading
import time
import nbi.kafka_proto_interface as kafka_proto_interface
from omci_logger import OmciLogger
import vomci
import nbi.grpc.service_definition.tr451_vomci_nbi_message_pb2 as tr451_vomci_nbi_message_pb2

DEFAULT_BOOTSTRAP_SERVERS = kafka_proto_interface.DEFAULT_BOOTSTRAP_SERVERS
#logger = OmciLogger.getDebugLogger(__name__)
# logger.basicConfig(level=logging.DEBUG)
KAFKA_CONSUMER_TOPIC = kafka_proto_interface.KAFKA_REQUEST_TOPICS[0]
KAFKA_RESPONSE_TOPIC = kafka_proto_interface.KAFKA_RESPONSE_TOPICS


def create_consumer():
    print("--Starting Consumer")
    nbi_consumer = kafka_proto_interface.RequestConsumer(topics=[KAFKA_CONSUMER_TOPIC, 'abc'],
                                                   bootstrap_servers=[DEFAULT_BOOTSTRAP_SERVERS])
    return nbi_consumer


def create_consumer_with_timeout():
    print("--Starting Consumer with_timeout")
    nbi_consumer = kafka_proto_interface.RequestConsumer(topics=[KAFKA_CONSUMER_TOPIC, 'abc'],
                                                   bootstrap_servers=[DEFAULT_BOOTSTRAP_SERVERS],
                                                   consumer_timeout_ms=10000)
    return nbi_consumer


def start_v_omci_consumer_thread():
    global kafka_if
    # Create a thread that will listen for kafka
    # consumer_thread = threading.Thread(name="consumer", target=kafka_proto_interface.start_kafka_consumer)
    '''nbi = create_consumer_with_timeout()
    consumer_thread = threading.Thread(name="consumer", target=nbi.consume)
    consumer_thread.start()
    time.sleep(2)'''
    v_omci = vomci.VOmci()
    kafka_if = kafka_proto_interface.KafkaProtoInterface(v_omci)
    consumer_thread = threading.Thread(name="consumer", target=kafka_if.start)
    consumer_thread.start()
    # time.sleep(2)


def test_simple_kafka_message():
    print("----Starting producer basic tests")
    producer = kafka_proto_interface.start_kafka_producer()
    msg = tr451_vomci_nbi_message_pb2.Msg()
    msg.header.msg_id="1"
    msg.header.sender_name="VOLTMF"
    msg.header.recipient_name="vomci-vendor-1"
    msg.header.object_type=msg.header.VOMCI_FUNCTION
    msg.header.object_name="vOMCI"
    msg.body.request.rpc.input_data = bytes("{\"bbf-vomci-function:create-onu\":{\"name\":\"ontA\"}}","utf-8")
    producer.send(KAFKA_CONSUMER_TOPIC,bytes(msg.SerializeToString()))
    assert kafka_if._consumer._last_rcvd_object is None

    producer = kafka_proto_interface.start_kafka_producer()
    msg = tr451_vomci_nbi_message_pb2.Msg()
    msg.header.msg_id="3"
    msg.header.sender_name="VOLTMF"
    msg.header.recipient_name="vomci-vendor-1"
    msg.header.object_type=msg.header.VOMCI_FUNCTION
    msg.header.object_name="vomci-vendor-1"
    #msg.body.request.rpc.input_data = bytes("{\"bbf-vomci-function:create-onu\":{\"name\":\"ontA\"}}","utf-8")
    msg.body.request.action.input_data = bytes("{\"bbf-vomci-function:managed-onus\":{\"managed-onu\":[{\"name\":\"onuA\",\"set-onu-communication\":{\"onu-attachment-point\":{\"olt-name\":\"olt-grpc-2\",\"channel-termination-name\":\"CT_1\",\"onu-id\":1},\"voltmf-remote-endpoint-name\":\"vOLTMF_Kafka\",\"onu-communication-available\":true,\"olt-remote-endpoint-name\":\"obbaa-vproxy-grpc-client-1\"}}]}}","utf-8")
    producer.send(KAFKA_CONSUMER_TOPIC,bytes(msg.SerializeToString()))
    assert kafka_if._consumer._last_rcvd_object is None

    """producer = kafka_proto_interface.start_kafka_producer()
    msg = tr451_vomci_nbi_message_pb2.Msg()
    msg.header.msg_id="5"
    msg.header.sender_name="VOLTMF"
    msg.header.recipient_name="vomci-vendor-1"
    msg.header.object_type=msg.header.VOMCI_FUNCTION
    msg.header.object_name="vomci-vendor-1"
    msg.body.request.action.input_data = bytes("{\"bbf-vomci-function:managed-onus\":{\"managed-onu\":[{\"name\":\"onuA\",\"delete-onu\":{}}]}}","utf-8")
    producer.send(KAFKA_CONSUMER_TOPIC,bytes(msg.SerializeToString()))
    assert kafka_if._consumer._last_rcvd_object is None"""

    producer = kafka_proto_interface.start_kafka_producer()
    msg = tr451_vomci_nbi_message_pb2.Msg()
    msg.header.msg_id="10"
    msg.header.sender_name="VOLTMF"
    msg.header.recipient_name="vomci-vendor-1"
    msg.header.object_type=msg.header.ONU
    msg.header.object_name="onuA"
    """msg.body.request.replace_config.config_inst = bytes("{\"bbf-qos-filters:filters\":{},\"ietf-ipfix-psamp:ipfix\":{},\"ietf-hardware:hardware\":{},\"bbf-qos-classifiers:classifiers\":{},\"ietf-pseudowires:pseudowires\":{},\"bbf-ghn:ghn\":{},\"bbf-qos-policies:qos-policy-profiles\":{},\"bbf-vdsl:vdsl\":{},\"bbf-xpongemtcont:xpongemtcont\":{},\"ietf-system:system\":{},\"bbf-qos-policer-envelope-profiles:envelope-profiles\":{},\"bbf-ghs:ghs\":{},\"ietf-interfaces:interfaces\":{},\"bbf-qos-policies:policies\":{},\"bbf-qos-traffic-mngt:tm-profiles\":{},\"bbf-qos-policing:policing-profiles\":{},\"bbf-selt:selt\":{},\"bbf-l2-dhcpv4-relay:l2-dhcpv4-relay-profiles\":{},\"ieee802-dot1x:nid-group\":{},\"ietf-alarms:alarms\":{},\"ietf-netconf-acm:nacm\":{},\"bbf-hardware-rpf-dpu:rpf\":{},\"bbf-pppoe-intermediate-agent:pppoe-profiles\":{},\"bbf-fast:fast\":{},\"bbf-mgmd:multicast\":{},\"bbf-melt:melt\":{},\"bbf-subscriber-profiles:subscriber-profiles\":{},\"bbf-ldra:dhcpv6-ldra-profiles\":{},\"bbf-l2-forwarding:forwarding\":{}}", "utf-8")"""
    msg.body.request.replace_config.config_inst = bytes("{\"ietf-hardware:hardware\":{\"component\":[{\"name\":\"ont1\",\"admin-state\":\"unlocked\",\"parent-rel-pos\":1,\"class\":\"iana-hardware:chassis\"},{\"parent\":\"ont1\",\"name\":\"ontCard_ont1_1\",\"admin-state\":\"unlocked\",\"parent-rel-pos\":1,\"class\":\"bbf-hardware-types:board\"},{\"parent\":\"ontCard_ont1_1\",\"name\":\"ontCage_ont1\",\"parent-rel-pos\":1,\"class\":\"bbf-hardware-types:cage\"},{\"parent\":\"ontCage_ont1\",\"name\":\"ontSfp_ont1\",\"parent-rel-pos\":1,\"class\":\"bbf-hardware-types:transceiver\"},{\"parent\":\"ontSfp_ont1\",\"name\":\"ontAniPort_ont1\",\"parent-rel-pos\":1,\"class\":\"bbf-hardware-types:transceiver-link\"},{\"parent\":\"ontCard_ont1_1\",\"name\":\"ontUni_ont1_1_1\",\"parent-rel-pos\":1,\"class\":\"bbf-hardware-types:transceiver-link\"}]},\"bbf-qos-classifiers:classifiers\":{\"classifier-entry\":[{\"name\":\"classifier_eg0\",\"classifier-action-entry-cfg\":[{\"action-type\":\"bbf-qos-classifiers:scheduling-traffic-class\",\"scheduling-traffic-class\":0}],\"filter-operation\":\"bbf-qos-classifiers:match-all-filter\",\"match-criteria\":{\"bbf-qos-policing:pbit-marking-list\":[{\"index\":0,\"pbit-value\":0}],\"any-protocol\":[null],\"dscp-range\":\"any\",\"match-all\":[null]}},{\"name\":\"classifier_eg1\",\"classifier-action-entry-cfg\":[{\"action-type\":\"bbf-qos-classifiers:scheduling-traffic-class\",\"scheduling-traffic-class\":1}],\"filter-operation\":\"bbf-qos-classifiers:match-all-filter\",\"match-criteria\":{\"bbf-qos-policing:pbit-marking-list\":[{\"index\":0,\"pbit-value\":1}],\"any-protocol\":[null],\"dscp-range\":\"any\",\"match-all\":[null]}},{\"name\":\"classifier_eg2\",\"classifier-action-entry-cfg\":[{\"action-type\":\"bbf-qos-classifiers:scheduling-traffic-class\",\"scheduling-traffic-class\":2}],\"filter-operation\":\"bbf-qos-classifiers:match-all-filter\",\"match-criteria\":{\"bbf-qos-policing:pbit-marking-list\":[{\"index\":0,\"pbit-value\":2}],\"any-protocol\":[null],\"dscp-range\":\"any\",\"match-all\":[null]}},{\"name\":\"classifier_eg3\",\"classifier-action-entry-cfg\":[{\"action-type\":\"bbf-qos-classifiers:scheduling-traffic-class\",\"scheduling-traffic-class\":3}],\"filter-operation\":\"bbf-qos-classifiers:match-all-filter\",\"match-criteria\":{\"bbf-qos-policing:pbit-marking-list\":[{\"index\":0,\"pbit-value\":3}],\"any-protocol\":[null],\"dscp-range\":\"any\",\"match-all\":[null]}},{\"name\":\"classifier_eg4\",\"classifier-action-entry-cfg\":[{\"action-type\":\"bbf-qos-classifiers:scheduling-traffic-class\",\"scheduling-traffic-class\":4}],\"filter-operation\":\"bbf-qos-classifiers:match-all-filter\",\"match-criteria\":{\"bbf-qos-policing:pbit-marking-list\":[{\"index\":0,\"pbit-value\":4}],\"any-protocol\":[null],\"dscp-range\":\"any\",\"match-all\":[null]}},{\"name\":\"classifier_eg5\",\"classifier-action-entry-cfg\":[{\"action-type\":\"bbf-qos-classifiers:scheduling-traffic-class\",\"scheduling-traffic-class\":5}],\"filter-operation\":\"bbf-qos-classifiers:match-all-filter\",\"match-criteria\":{\"bbf-qos-policing:pbit-marking-list\":[{\"index\":0,\"pbit-value\":5}],\"any-protocol\":[null],\"dscp-range\":\"any\",\"match-all\":[null]}},{\"name\":\"classifier_eg6\",\"classifier-action-entry-cfg\":[{\"action-type\":\"bbf-qos-classifiers:scheduling-traffic-class\",\"scheduling-traffic-class\":6}],\"filter-operation\":\"bbf-qos-classifiers:match-all-filter\",\"match-criteria\":{\"bbf-qos-policing:pbit-marking-list\":[{\"index\":0,\"pbit-value\":6}],\"any-protocol\":[null],\"dscp-range\":\"any\",\"match-all\":[null]}},{\"name\":\"classifier_eg7\",\"classifier-action-entry-cfg\":[{\"action-type\":\"bbf-qos-classifiers:scheduling-traffic-class\",\"scheduling-traffic-class\":7}],\"filter-operation\":\"bbf-qos-classifiers:match-all-filter\",\"match-criteria\":{\"bbf-qos-policing:pbit-marking-list\":[{\"index\":0,\"pbit-value\":7}],\"any-protocol\":[null],\"dscp-range\":\"any\",\"match-all\":[null]}},{\"name\":\"classifier_ing0\",\"classifier-action-entry-cfg\":[{\"action-type\":\"bbf-qos-classifiers:scheduling-traffic-class\",\"scheduling-traffic-class\":0}],\"filter-operation\":\"bbf-qos-classifiers:match-all-filter\",\"match-criteria\":{\"any-protocol\":[null],\"dscp-range\":\"any\",\"tag\":[{\"index\":0,\"in-pbit-list\":\"0\"}]}},{\"name\":\"classifier_ing1\",\"classifier-action-entry-cfg\":[{\"action-type\":\"bbf-qos-classifiers:scheduling-traffic-class\",\"scheduling-traffic-class\":1}],\"filter-operation\":\"bbf-qos-classifiers:match-all-filter\",\"match-criteria\":{\"any-protocol\":[null],\"dscp-range\":\"any\",\"tag\":[{\"index\":0,\"in-pbit-list\":\"1\"}]}},{\"name\":\"classifier_ing2\",\"classifier-action-entry-cfg\":[{\"action-type\":\"bbf-qos-classifiers:scheduling-traffic-class\",\"scheduling-traffic-class\":2}],\"filter-operation\":\"bbf-qos-classifiers:match-all-filter\",\"match-criteria\":{\"any-protocol\":[null],\"dscp-range\":\"any\",\"tag\":[{\"index\":0,\"in-pbit-list\":\"2\"}]}},{\"name\":\"classifier_ing3\",\"classifier-action-entry-cfg\":[{\"action-type\":\"bbf-qos-classifiers:scheduling-traffic-class\",\"scheduling-traffic-class\":3}],\"filter-operation\":\"bbf-qos-classifiers:match-all-filter\",\"match-criteria\":{\"any-protocol\":[null],\"dscp-range\":\"any\",\"tag\":[{\"index\":0,\"in-pbit-list\":\"3\"}]}},{\"name\":\"classifier_ing4\",\"classifier-action-entry-cfg\":[{\"action-type\":\"bbf-qos-classifiers:scheduling-traffic-class\",\"scheduling-traffic-class\":4}],\"filter-operation\":\"bbf-qos-classifiers:match-all-filter\",\"match-criteria\":{\"any-protocol\":[null],\"dscp-range\":\"any\",\"tag\":[{\"index\":0,\"in-pbit-list\":\"4\"}]}},{\"name\":\"classifier_ing5\",\"classifier-action-entry-cfg\":[{\"action-type\":\"bbf-qos-classifiers:scheduling-traffic-class\",\"scheduling-traffic-class\":5}],\"filter-operation\":\"bbf-qos-classifiers:match-all-filter\",\"match-criteria\":{\"any-protocol\":[null],\"dscp-range\":\"any\",\"tag\":[{\"index\":0,\"in-pbit-list\":\"5\"}]}},{\"name\":\"classifier_ing6\",\"classifier-action-entry-cfg\":[{\"action-type\":\"bbf-qos-classifiers:scheduling-traffic-class\",\"scheduling-traffic-class\":6}],\"filter-operation\":\"bbf-qos-classifiers:match-all-filter\",\"match-criteria\":{\"any-protocol\":[null],\"dscp-range\":\"any\",\"tag\":[{\"index\":0,\"in-pbit-list\":\"6\"}]}},{\"name\":\"classifier_ing7\",\"classifier-action-entry-cfg\":[{\"action-type\":\"bbf-qos-classifiers:scheduling-traffic-class\",\"scheduling-traffic-class\":7}],\"filter-operation\":\"bbf-qos-classifiers:match-all-filter\",\"match-criteria\":{\"any-protocol\":[null],\"dscp-range\":\"any\",\"tag\":[{\"index\":0,\"in-pbit-list\":\"7\"}]}}]},\"bbf-qos-policies:qos-policy-profiles\":{\"policy-profile\":[{\"name\":\"IPP0\",\"policy-list\":[{\"name\":\"POLICY_ING\"}]},{\"name\":\"QPP0\",\"policy-list\":[{\"name\":\"POLICY_EG\"}]}]},\"bbf-xpongemtcont:xpongemtcont\":{\"tconts\":{\"tcont\":[{\"interface-reference\":\"ontAni_ont1\",\"name\":\"tcont_ont1\",\"alloc-id\":1024,\"traffic-descriptor-profile-ref\":\"TDP0\",\"bbf-xpongemtcont-qos:tm-root\":{}}]},\"traffic-descriptor-profiles\":{\"traffic-descriptor-profile\":[{\"fixed-bandwidth\":\"10000000\",\"assured-bandwidth\":\"10000000\",\"maximum-bandwidth\":\"30000000\",\"name\":\"TDP0\"}]},\"gemports\":{\"gemport\":[{\"gemport-id\":1024,\"tcont-ref\":\"tcont_ont1\",\"traffic-class\":0,\"upstream-aes-indicator\":false,\"downstream-aes-indicator\":false,\"name\":\"gem_ont1\",\"interface\":\"enet_uni_ont1_1_1\"}]}},\"ietf-interfaces:interfaces\":{\"interface\":[{\"bbf-qos-traffic-mngt:tm-root\":{},\"name\":\"ontAni_ont1\",\"bbf-interface-port-reference:port-layer-if\":\"ontAniPort_ont1\",\"type\":\"bbf-xpon-if-type:ani\",\"bbf-xponani:ani\":{\"upstream-fec\":true,\"management-gemport-aes-indicator\":false,\"onu-id\":1},\"enabled\":true,\"bbf-interfaces-performance-management:performance\":{\"enable\":false}},{\"ieee802-dot1x:pae\":{\"port-capabilities\":{},\"logon-process\":{\"logon\":false},\"logon-nid\":{}},\"bbf-l2-forwarding:mac-learning\":{\"number-committed-mac-addresses\":1,\"mac-learning-enable\":true,\"mac-learning-failure-action\":\"forward\",\"max-number-mac-addresses\":4294967295},\"bbf-qos-traffic-mngt:tm-root\":{},\"name\":\"enet_uni_ont1_1_1\",\"bbf-interface-port-reference:port-layer-if\":\"ontUni_ont1_1_1\",\"type\":\"iana-if-type:ethernetCsmacd\",\"enabled\":true,\"bbf-interfaces-performance-management:performance\":{\"enable\":false},\"ieee802-ethernet-interface:ethernet\":{\"duplex\":\"full\",\"flow-control\":{\"force-flow-control\":false,\"pfc\":{},\"pause\":{}},\"auto-negotiation\":{}},\"bbf-interface-usage:interface-usage\":{}},{\"bbf-l2-forwarding:mac-learning\":{\"number-committed-mac-addresses\":1,\"mac-learning-enable\":true,\"mac-learning-failure-action\":\"forward\",\"max-number-mac-addresses\":4294967295},\"bbf-qos-enhanced-scheduling:egress-tm-objects\":{},\"bbf-qos-traffic-mngt:tm-root\":{},\"bbf-subscriber-profiles:subscriber-profile\":{},\"bbf-sub-interfaces:subif-lower-layer\":{\"interface\":\"enet_uni_ont1_1_1\"},\"name\":\"enet_vlan_ont1\",\"bbf-qos-policies:ingress-qos-policy-profile\":\"IPP0\",\"type\":\"bbf-if-type:vlan-sub-interface\",\"bbf-sub-interfaces:inline-frame-processing\":{\"ingress-rule\":{\"rule\":[{\"name\":\"rule_1\",\"priority\":100,\"flexible-match\":{\"bbf-sub-interface-tagging:match-criteria\":{\"any-frame\":[null],\"any-protocol\":[null],\"untagged\":[null],\"ethernet-frame-type\":\"any\"}},\"ingress-rewrite\":{\"bbf-sub-interface-tagging:pop-tags\":0,\"bbf-sub-interface-tagging:push-tag\":[{\"index\":0,\"dot1q-tag\":{\"vlan-id\":11,\"tag-type\":\"bbf-dot1q-types:c-vlan\",\"pbit-from-tag-index\":0,\"dei-from-tag-index\":0}}]}}]},\"egress-rewrite\":{\"bbf-sub-interface-tagging:pop-tags\":1}},\"enabled\":true,\"bbf-interfaces-performance-management:performance\":{\"enable\":false},\"bbf-interface-usage:interface-usage\":{}}]},\"bbf-qos-policies:policies\":{\"policy\":[{\"name\":\"POLICY_ING\",\"classifiers\":[{\"name\":\"classifier_ing0\"},{\"name\":\"classifier_ing1\"},{\"name\":\"classifier_ing2\"},{\"name\":\"classifier_ing3\"},{\"name\":\"classifier_ing4\"},{\"name\":\"classifier_ing5\"},{\"name\":\"classifier_ing6\"},{\"name\":\"classifier_ing7\"}]},{\"name\":\"POLICY_EG\",\"classifiers\":[{\"name\":\"classifier_eg0\"},{\"name\":\"classifier_eg1\"},{\"name\":\"classifier_eg2\"},{\"name\":\"classifier_eg3\"},{\"name\":\"classifier_eg4\"},{\"name\":\"classifier_eg5\"},{\"name\":\"classifier_eg6\"},{\"name\":\"classifier_eg7\"}]}]}}","utf-8")
    producer.send(KAFKA_CONSUMER_TOPIC,bytes(msg.SerializeToString()))
    assert kafka_if._consumer._last_rcvd_object is None

def main():
    start_v_omci_consumer_thread()
    test_simple_kafka_message()

if __name__ == '__main__':
    main()
