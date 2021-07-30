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


def test_simple_proxy_message():
    print("----Starting producer basic tests")
    producer = kafka_proto_interface.start_kafka_producer()
    msg = tr451_vomci_nbi_message_pb2.Msg()
    msg.header.msg_id="2"
    msg.header.sender_name="vOLTMF"
    msg.header.recipient_name="proxy-1"
    msg.header.object_type=msg.header.VOMCI_PROXY
    msg.header.object_name="proxy-1"
    msg.body.request.rpc.input_data = bytes("{\"bbf-vomci-proxy:create-onu\":{\"name\":\"ontA\"}}","utf-8")
    producer.send(KAFKA_CONSUMER_TOPIC,bytes(msg.SerializeToString()))
    assert kafka_if._consumer._last_rcvd_object is None

    #msg.body.request.action.input_data = bytes("{\"bbf-vomci-proxy:managed-onus\":{\"managed-onu\":[{\"name\":\"ont1\",\"delete-onu\":{}}]}}",
                                               #"utf-8")
    producer = kafka_proto_interface.start_kafka_producer()
    msg = tr451_vomci_nbi_message_pb2.Msg()
    msg.header.msg_id="4"
    msg.header.sender_name="vOLTMF"
    msg.header.recipient_name="proxy-1"
    msg.header.object_type=msg.header.VOMCI_PROXY
    msg.header.object_name="proxy-1"
    msg.body.request.action.input_data = bytes("{\"bbf-vomci-proxy:managed-onus\":{\"managed-onu\":[{\"name\":\"onuA\",\"set-onu-communication\":{\"onu-attachment-point\":{\"olt-name\":\"olt-grpc-2\",\"channel-termination-name\":\"CT_1\",\"onu-id\":1},\"onu-communication-available\":true,\"vomci-func-remote-endpoint-name\":\"obbaa-vomci\",\"olt-remote-endpoint-name\":\"olt-grpc-2\"}}]}}","utf-8")
    producer.send(KAFKA_CONSUMER_TOPIC,bytes(msg.SerializeToString()))
    assert kafka_if._consumer._last_rcvd_object is None

    """producer = kafka_proto_interface.start_kafka_producer()
    msg = tr451_vomci_nbi_message_pb2.Msg()
    msg.header.msg_id="6"
    msg.header.sender_name="vOLTMF"
    msg.header.recipient_name="proxy-1"
    msg.header.object_type=msg.header.VOMCI_PROXY
    msg.header.object_name="proxy-1"
    msg.body.request.action.input_data = bytes("{\"bbf-vomci-proxy:managed-onus\":{\"managed-onu\":[{\"name\":\"onuA\",\"delete-onu\":{}}]}}","utf-8")
    producer.send(KAFKA_CONSUMER_TOPIC,bytes(msg.SerializeToString()))
    assert kafka_if._consumer._last_rcvd_object is None"""


def main():
    start_v_omci_consumer_thread()
    test_simple_proxy_message()

if __name__ == '__main__':
    main()
