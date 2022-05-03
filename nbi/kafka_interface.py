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
import os
import sys
import time
import logging
import kafka
import json, ast
from omci_logger import OmciLogger
from mapper.yang_to_omci_mapper import extractPayload
from omh_nbi.omh_handler import OMHStatus

logger = OmciLogger.getLogger(__name__)

DEFAULT_BOOTSTRAP_SERVERS = list(os.environ.get('KAFKA_BOOTSTRAP_SERVER', "kafka:9092 localhost:9092").split())
KAFKA_REQUEST_TOPICS = list(os.environ.get('KAFKA_REQUEST_TOPICS').split())
KAFKA_RESPONSE_TOPICS = list(os.environ.get('KAFKA_RESPONSE_TOPICS').split())
KAFKA_NOTIFICATION_TOPICS = list(os.environ.get('KAFKA_NOTIFICATION_TOPICS').split())
KAFKA_CONSUMER_PARTITIONS = 3
KAFKA_CONSUMER_REPLICAS = 1

kafkaLogger = logging.getLogger('kafka')
kafkaLogger.setLevel(logging.WARN)

class RequestConsumer:
    """Kafka consumer to read messages sent from VOLTMF"""

    def __init__(self, topics: object = None, bootstrap_servers: object = None, consumer_timeout_ms: object = None,
                 on_message: callable = None) -> None:
        """ Class contructor.
                Args:
                    :param topics: Topics to subscribe to
                    :param bootstrap_servers:
                """
        if topics is None:
            topics = []
        if bootstrap_servers is None:
            bootstrap_servers = DEFAULT_BOOTSTRAP_SERVERS
        else:
            logger.info('Connecting to bootstrap server: {}'.format(DEFAULT_BOOTSTRAP_SERVERS))
        self._consumer = None
        self._adminclient = None
        self._topics_ready = False
        self._topics = topics
        self._bootstrap_servers = bootstrap_servers
        self._consumer_timeout_ms = consumer_timeout_ms
        if on_message is None:
            self._on_message = self.minimal_logger
        else:
            self._on_message = on_message
        self._last_rcvd_object = None

    def create_kafka_consumer(self):
        # Create kafka consumer. Wait until kafka broker becomes available if necessary
        #
        while self._consumer is None:
            try:
                logger.info('Kafka: starting a consumer for topics {}..'.format(KAFKA_REQUEST_TOPICS))
                if self._consumer_timeout_ms is not None:  # TODO improve kafka initialization.
                    self._consumer = kafka.KafkaConsumer(*self._topics, bootstrap_servers=self._bootstrap_servers,
                                                         consumer_timeout_ms=self._consumer_timeout_ms)
                else:
                    self._consumer = kafka.KafkaConsumer(*self._topics, bootstrap_servers=self._bootstrap_servers)
            except:
                logger.info("Failed to create kafka consumer. Error {}".format(sys.exc_info()[0]))
                logger.info("Waiting 5s before retrying..")
                time.sleep(5)

        logger.info("Consumer Created.")
        while self._adminclient is None:
            try:
                self._adminclient = kafka.KafkaAdminClient(bootstrap_servers=self._bootstrap_servers)
            except:
                logger.info("Failed to create kafka admin client. Error {}".format(sys.exc_info()[0]))
                logger.info("Waiting 5s before retrying..")
                time.sleep(5)

        logger.info('Kafka: creating topics..')
        while self._topics_ready is False:
            try:
                self._topics_ready = True
                for topic in self._topics:
                    topic_partitions = self._consumer.partitions_for_topic(topic)
                    if topic_partitions is None:
                        self._adminclient.create_topics([kafka.admin.NewTopic(topic, num_partitions=KAFKA_CONSUMER_PARTITIONS, replication_factor=KAFKA_CONSUMER_REPLICAS)])
                        self._topics_ready = False
                        time.sleep(2)
            except:
                self._topics_ready = False
                logger.info("Failed to create kafka topics. Error {}".format(sys.exc_info()))
                logger.info("Waiting 2s before retrying..")
                time.sleep(2)

        self._adminclient.close()
        logger.info("Kafka: Topics Created.")

    def consume(self) -> None:
        # self.create_kafka_consumer()
        logger.info('Kafka: Waiting for messages')
        try:
            for message in self._consumer:
                logger.info('A message was received')
                self._last_rcvd_object = self._on_message(message)
        except KeyboardInterrupt:
            logger.error('User Aborted')

    def stop(self) -> None:
        logger.debug("Kafka: stopping consumer")
        self._consumer.close()
        logger.debug("closed")

    @staticmethod
    def minimal_logger() -> None:
        logger.error('on_message is not set')


def process_message(m) -> None:
    logger.debug('Dummy processing function\n')
    logger.warning('{}:{}:{}: key= {} value= {}'.format(m.topic, m.partition, m.offset, m.key, m.value))


def start_kafka_producer(callback=None):
    producer = kafka.KafkaProducer(bootstrap_servers=DEFAULT_BOOTSTRAP_SERVERS)
    return producer


def start_kafka_json_producer(callback=None):
    json_producer = kafka.KafkaProducer(bootstrap_servers=DEFAULT_BOOTSTRAP_SERVERS,
                                        value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    return json_producer


class VoltmfJsonProducer:
    """Kafka Producer to send messages towards VOLTMF"""

    def __init__(self, bootstrap_servers=None):
        """ Class contructor.
                Args:
                    :param bootstrap_servers:
                """
        if bootstrap_servers is None:
            bootstrap_servers = DEFAULT_BOOTSTRAP_SERVERS
        self._bootstrap_servers = bootstrap_servers

        self._producer = None
        while self._producer is None:
            try:
                logger.info('Kafka: starting a producer..')
                self._producer = kafka.KafkaProducer(bootstrap_servers=self._bootstrap_servers,
                                                     value_serializer=lambda v: json.dumps(v).encode('utf-8'))
                logger.info('Kafka: producer started')
            except:
                logger.info("Failed to create kafka producer. Error {}".format(sys.exc_info()[0]))
                logger.info("Waiting 5s before retrying..")
                time.sleep(5)

    def send_response(self, message_dict):
        self._producer.send(KAFKA_RESPONSE_TOPICS[0], message_dict)


def create_successful_response(command_dict):
    response_dict = command_dict
    response_dict['payload']['status'] = 'OK'
    payload = response_dict['payload']
    response_dict['payload'] = json.dumps(payload)
    response_dict['event'] = 'response'
    return response_dict


def create_unsuccessful_response(command_dict, error_msg=None):
    response_dict = command_dict
    response_dict['payload']['status'] = 'NOK'
    if error_msg is not None and isinstance(error_msg, str):
        response_dict['payload']['error'] = error_msg
    payload = response_dict['payload']
    response_dict['payload'] = json.dumps(payload)
    response_dict['event'] = 'response'
    return response_dict

class KafkaInterface:

    def __init__(self, v_omci, bootstrap_servers=None):
        if bootstrap_servers is None:
            bootstrap_servers = DEFAULT_BOOTSTRAP_SERVERS
        self._bootstrap_servers = bootstrap_servers
        self._consumer = None
        self._producer = None
        self.commands_dict = {}
        self.on_message = self.handle_incoming_msg
        self._vomci = v_omci


    def start(self):
        # time.sleep(60)
        self._consumer = RequestConsumer(topics=KAFKA_REQUEST_TOPICS, bootstrap_servers=self._bootstrap_servers,
                                     on_message=self.on_message)
        self._producer = VoltmfJsonProducer(bootstrap_servers=self._bootstrap_servers)

        self._consumer.create_kafka_consumer()
        self._consumer.consume()

    @staticmethod
    def process_json_message(m):
        # Temporary print to indicate a kafka message has been consumed
        logger.info(">> Consumed Topic: {}, partition {}, offset: {}, key {}, value {}, "
                    "timestamp {}".format(m.topic, m.partition, m.offset, m.key, m.value, m.timestamp))
        try:
            message_dict = json.loads(m.value.decode('utf-8'))
            return message_dict
        except Exception as e:
            logger.debug('Error Handling {} of Kafka message {}'.format(e, m.key))
            return None

    def log_incoming_msg(self, m):
        logger.info(
            '> Incoming Message Handled {}:{}:{}: key= {} value= {}'.format(m.topic, m.partition, m.offset, m.key,
                                                                            m.value))
        return

    def handle_incoming_msg(self, m):
        logger.info(
            '> Incoming Message Handled {}:{}:{}: key= {} value= {}'.format(m.topic, m.partition, m.offset, m.key,
                                                                            m.value))
        message_dict = self.process_json_message(m)
        onu_name = None
        olt_name = None
        event = None
        channel_termination = None
        onu_id = None
        payload_dict = None
        logger.debug("Parsed it the message is : {}".format(message_dict))
        if message_dict is not None:
            if 'onu-name' in message_dict:
                onu_name = message_dict['onu-name']
            if 'event' in message_dict:
                event = message_dict['event']
            if 'channel-termination-ref' in message_dict:
                channel_termination = message_dict['channel-termination-ref']
            if 'ct-ref' in message_dict:
                channel_termination = message_dict['ct-ref']
            if 'onu-id' in message_dict:
                onu_id = message_dict['onu-id']
            if 'olt-name' in message_dict:
                olt_name = message_dict['olt-name']
            if 'payload' in message_dict:
                payload = message_dict['payload']
                if isinstance(payload, str):
                    try:
                        payload_dict = json.loads(payload)
                        message_dict['payload'] = payload_dict
                    except Exception as e:
                        logger.error('Error {} Handling of payload {}'.format(e, message_dict['payload']))
                elif isinstance(payload, dict):
                    payload_dict = payload
            if onu_name is not None and event is not None:
                self.commands_dict[onu_name] = message_dict
                # Creating a transaction record
                logger.debug("Incoming----commands_dict size is {}".format(len(self.commands_dict)))
            else:
                logger.error("onu_name or event is NONE")
                return
        else:
            logger.error("message_dict is None")
            return

        # Patch to set olt_name if it was missing in the request
        if olt_name is None:
            olt_name = 'Broadcom_OLT'

        if onu_name is not None and event is not None:
            if event == "create":
                self._vomci.trigger_create_onu(onu_name)
            elif event == "detect":
                if channel_termination is None or onu_id is None or payload_dict is None:
                    logger.error("channel-termination-ref and onu-id are required in 'detect' event")
                    return
                try:
                    onu_tc_id = int(onu_id)
                except:
                    logger.error("Error. Can't convert onu-id {} to int".format(onu_id))
                    return
                available = payload_dict["onu-communication-available"]
                olt_endpoint_name = payload_dict["olt-remote-endpoint-name"]
                if "voltmf-remote-endpoint-name" in payload_dict.keys():
                    south_endpoint_name = payload_dict["voltmf-remote-endpoint-name"]
                elif "vomci-func-remote-endpoint-name" in payload_dict.keys():
                    south_endpoint_name = payload_dict["vomci-func-remote-endpoint-name"]
                self._vomci.trigger_set_onu_communication(olt_name, onu_name, channel_termination,
                                                          onu_tc_id, available, olt_endpoint_name, south_endpoint_name)
            elif event == "undetect":
                self._vomci.trigger_delete_onu(onu_name)
            elif event == "request":
                if 'copy-config' == payload_dict['operation']:
                    try:
                        ret_val = extractPayload(onu_name, olt_name, payload_dict)
                        if ret_val == OMHStatus.OK:
                            self.send_successful_response(onu_name)
                        else:
                            logger.error("Error. payload processsing failed")
                    except:
                        logger.error("Error. extractPayload failed for copy-config for ONU {}".format(onu_name))
                        return
                elif 'edit-config' == payload_dict['operation']:
                    try:
                        ret_val = extractPayload(onu_name, olt_name, payload_dict)
                        if ret_val == OMHStatus.OK:
                            self.send_successful_response(onu_name)
                        else:
                            logger.error("Error. payload processsing failed")
                            return
                    except:
                        logger.error("Error. extractPayload failed for edit-config for ONU {}".format(onu_name))
                        return
            else:
                logger.error("event {} is not supported yet".format(event))

    def send_successful_response(self, onu_name):
        if onu_name in self.commands_dict:
            response_dict = create_successful_response(self.commands_dict[onu_name])
            self._producer.send_response(response_dict)
            del self.commands_dict[onu_name]
            # Deleting a transaction record
            logger.info("Outgoing----commands_dict size is {}".format(len(self.commands_dict)))

    def send_unsuccessful_response(self, onu_name, error_msg=None):
        if onu_name in self.commands_dict:
            response_dict = create_unsuccessful_response(self.commands_dict[onu_name], error_msg)
            self._producer.send_response(response_dict)
            del self.commands_dict[onu_name]
            # Deleting a transaction record
            logger.info("Outgoing----commands_dict size is {}".format(len(self.commands_dict)))

    def send_msg(self, msg):
        self._producer.send_response(msg)
