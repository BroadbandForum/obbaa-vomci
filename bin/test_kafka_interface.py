import json
import threading
import time
import nbi.kafka_interface as kafka_interface
from omci_logger import OmciLogger
import vomci

DEFAULT_BOOTSTRAP_SERVERS = kafka_interface.DEFAULT_BOOTSTRAP_SERVERS
logger = OmciLogger.getDebugLogger(__name__)
# logger.basicConfig(level=logging.DEBUG)
KAFKA_CONSUMER_TOPIC = kafka_interface.KAFKA_CONSUMER_TOPICS[0]
KAFKA_RESPONSE_TOPIC = kafka_interface.KAFKA_RESPONSE_TOPIC


def create_consumer():
    print("--Starting Consumer")
    nbi_consumer = kafka_interface.RequestConsumer(topics=[KAFKA_CONSUMER_TOPIC, 'abc'],
                                                   bootstrap_servers=[DEFAULT_BOOTSTRAP_SERVERS])
    return nbi_consumer


def create_consumer_with_timeout():
    print("--Starting Consumer with_timeout")
    nbi_consumer = kafka_interface.RequestConsumer(topics=[KAFKA_CONSUMER_TOPIC, 'abc'],
                                                   bootstrap_servers=[DEFAULT_BOOTSTRAP_SERVERS],
                                                   consumer_timeout_ms=10000)
    return nbi_consumer


def start_v_omci_consumer_thread():
    global kafka_if
    # Create a thread that will listen for kafka
    # consumer_thread = threading.Thread(name="consumer", target=kafka_interface.start_kafka_consumer)
    '''nbi = create_consumer_with_timeout()
    consumer_thread = threading.Thread(name="consumer", target=nbi.consume)
    consumer_thread.start()
    time.sleep(2)'''
    v_omci = vomci.VOmci()
    kafka_if = kafka_interface.KafkaInterface(v_omci)
    consumer_thread = threading.Thread(name="consumer", target=kafka_if.start)
    consumer_thread.start()
    # time.sleep(2)


def test_simple_kafka_message():
    print("----Starting producer basic tests")
    producer = kafka_interface.start_kafka_producer()
    producer.send(KAFKA_CONSUMER_TOPIC, b'NudgeNudge')
    assert kafka_if._consumer._last_rcvd_object is None
    producer.send('not_451_topic', b'SayNoMore') # testing wrong topic
    assert kafka_if._consumer._last_rcvd_object is None


def test_json_kafka_producer():
    print("----Starting Json producer for Testing purposes")
    json_producer = kafka_interface.start_kafka_json_producer()
    print("----Sending Json as a string")
    json_producer.send(KAFKA_CONSUMER_TOPIC, "{'foo': 'bar'}")
    print("----Sending Json object")
    json_producer.send(KAFKA_CONSUMER_TOPIC, {'foo': 'bar'})

    """data = {'onu-id': '25'}
    payload = {'identifier': '0'}
    data['onu-name'] = 'exampleDevice'
    data['olt-name'] = 'olt1'
    data['channel-termination-ref'] = 'CT-2'
    payload['operation'] = 'DETECT'
    data['payload'] = payload
    test_string = json.dumps(data)
    print('the string representation is the following: ' + test_string)"""
    test_str2 = '{"onu-id": "25", "onu-name": "exampleDevice", "olt-name": "olt1", "channel-termination-ref": "CT-2",' \
                '"payload": {"identifier": "0", "operation": "DETECT"}} '
    json_producer.send(KAFKA_CONSUMER_TOPIC, json.loads(test_str2))

    # json_producer.send(KAFKA_CONSUMER_TOPIC, b"{'foo': 'bar'}")


def main():
    start_v_omci_consumer_thread()
    test_simple_kafka_message()
    test_json_kafka_producer()


if __name__ == '__main__':
    main()
