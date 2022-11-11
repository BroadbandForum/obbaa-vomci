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
import datetime
import logging
from google.protobuf import message
import kafka
import json
import google.protobuf
#from protobuf_to_dict import protobuf_to_dict
#from protoc_gen_validate.validator import validate, ValidationFailed
from kafka import TopicPartition
from omci_logger import OmciLogger
from mapper.yang_to_omci_mapper import extractPayload
from mapper.get_yang_response import get_yang_response
from omh_nbi.omh_handler import OMHStatus
from database.onu_management_chain import ManagementChain
import nbi.grpc.service_definition.tr451_vomci_nbi_message_pb2 as tr451_vomci_nbi_message_pb2


logger = OmciLogger.getLogger(__name__)


DEFAULT_BOOTSTRAP_SERVERS = list(os.environ.get('KAFKA_BOOTSTRAP_SERVER', "kafka:9092 localhost:9092").split())
DEFAULT_REQUEST_TOPICS = list(os.environ.get('KAFKA_REQUEST_TOPICS').split())
DEFAULT_NOTIFICATION_TOPICS = list(os.environ.get('KAFKA_NOTIFICATION_TOPICS').split())
DEFAULT_KAFKA_PORT = 9092
DEFAULT_GRPC_SERVER_PORT = 8443
KAFKA_CONSUMER_PARTITIONS = 3
KAFKA_CONSUMER_REPLICAS = 1

kafkaLogger = logging.getLogger('kafka')
kafkaLogger.setLevel(logging.WARN)

class RequestProtoConsumer:
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
                logger.info('Kafka: starting a consumer for topics {}..'.format(self._topics))
                if self._consumer_timeout_ms is not None:  # TODO improve kafka initialization.
                    self._consumer = kafka.KafkaConsumer(bootstrap_servers=self._bootstrap_servers,
                                                         consumer_timeout_ms=self._consumer_timeout_ms)
                else:
                    self._consumer = kafka.KafkaConsumer(bootstrap_servers=self._bootstrap_servers)
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
        mypartitions = set()
        while self._topics_ready is False:
            try:
                self._topics_ready = True
                for topic in self._topics:
                    topic_partitions = self._consumer.partitions_for_topic(topic)
                    if topic_partitions is None:
                        self._adminclient.create_topics([kafka.admin.NewTopic(topic, num_partitions=KAFKA_CONSUMER_PARTITIONS, replication_factor=KAFKA_CONSUMER_REPLICAS)])
                        self._topics_ready = False
                        time.sleep(2)
                        topic_partitions = self._consumer.partitions_for_topic(topic)
                    for part in topic_partitions:
                        tp = TopicPartition(topic, part)
                        mypartitions.add(tp) # keep partitions that will be assigned later
            except:
                self._topics_ready = False
                logger.info("Failed to create kafka topics. Error {}".format(sys.exc_info()))
                logger.info("Waiting 2s before retrying..")
                time.sleep(2)

        if self._adminclient != None:
            self._adminclient.close()
            self._adminclient = None
        logger.info("Kafka: Topics Created.")

        self._consumer.assign(mypartitions)

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

    def set_topics(self, topics: list):
        self._topics = list(set(topics)) #using set to avoid duplicates
        self._topics_ready = False
        self.create_kafka_consumer()

    def add_topics(self, topics: list):
        if topics == []:
            return
        myTopics = self._topics + topics
        self.set_topics(myTopics)

    @staticmethod
    def minimal_logger() -> None:
        logger.error('on_message is not set')

def start_kafka_producer(callback=None):
    producer = kafka.KafkaProducer(bootstrap_servers=DEFAULT_BOOTSTRAP_SERVERS)
    return producer

class VoltmfProtoProducer:
    """Kafka Producer to send messagges towards VOLTMF using protobuf GPB"""

    def __init__(self, topics: list = [], notification_topics: list = None, bootstrap_servers=None):
        self._topics = topics
        if notification_topics is None:
            notification_topics = DEFAULT_NOTIFICATION_TOPICS
        self._notification_topics = notification_topics
        if bootstrap_servers is None:
            bootstrap_servers = DEFAULT_BOOTSTRAP_SERVERS
        self._bootstrap_servers = bootstrap_servers

        self._producer = None
        while self._producer is None:
            try:
                logger.info('Kafka: starting a producer..')
                self._producer = kafka.KafkaProducer(bootstrap_servers=self._bootstrap_servers)
                logger.info('Kafka: producer started')
            except:
                logger.info("Failed to create kafka producer. Error {}".format(sys.exc_info()[0]))
                logger.info("Waiting 5s before retrying..")
                time.sleep(5)

    def send_proto_response(self, message : tr451_vomci_nbi_message_pb2):
        if self._producer == None:
            logger.warning("Failed to send message! No topic set..")
            return
        msg_str = message.SerializeToString()
        for topic in self._topics:
            logger.info("Sending response on topic {}".format(topic))
            self._producer.send(topic, bytes(msg_str))

    def send_proto_response_to(self, message : tr451_vomci_nbi_message_pb2, topics: list):
        if self._producer == None:
            logger.warning("Failed to send message! No topic set..")
            return
        msg_str = message.SerializeToString()
        for topic in topics:
            self._producer.send(topic, bytes(msg_str))

    def send_proto_notification(self, message : tr451_vomci_nbi_message_pb2):
        if self._notification_topics is None:
            logger.warning("Failed to send message! No topic set..")
            return
        msg_str = message.SerializeToString()
        for topic in self._notification_topics:
            logger.info("Sending notification on topic {}".format(topic))
            self._producer.send(topic, bytes(msg_str))

    def set_topics(self, topics: list):
        self._topics = list(set(topics)) #using set to avoid duplicates

    def add_topics(self, topics: list):
        if topics == []:
            return
        myTopics = self._topics + topics
        self.set_topics(myTopics)

    def set_notification_topics(self, topics: list):
        self._notification_topics = list(set(topics)) #using set to avoid duplicates

    def add_notification_topics(self, topics: list):
        if topics == []:
            return
        myTopics = self._notification_topics + topics
        self.set_notification_topics(myTopics)
class KafkaProtoInterface:

    def __init__(self, name, v_omci, bootstrap_servers=None):
        self.local_endpoint_name = name
        self.remote_endpoint_name = None
        if bootstrap_servers is None:
            bootstrap_servers = DEFAULT_BOOTSTRAP_SERVERS
        self._bootstrap_servers = bootstrap_servers
        self._consumer = None
        self._producer = None
        self.proto_resp = {}
        self.on_message = self.handle_incoming_proto_msg
        self._vomci = v_omci

    def start(self, producer_topics = [], notification_topics = [], consumer_topics=DEFAULT_REQUEST_TOPICS):
        self._producer = VoltmfProtoProducer(producer_topics, notification_topics, bootstrap_servers=self._bootstrap_servers)
        self._consumer = RequestProtoConsumer(consumer_topics, bootstrap_servers=self._bootstrap_servers,
                                                                                         on_message=self.on_message)
        self._consumer.create_kafka_consumer()
        self._consumer.consume()

    @staticmethod
    def process_proto_message(m):
        logger.info(">> Consumed Topic: {}, partition {}, offset: {}, key {}, value {}, "
                    "timestamp {}".format(m.topic, m.partition, m.offset, m.key, m.value, m.timestamp))
        try:
            message = tr451_vomci_nbi_message_pb2.Msg()
            message.ParseFromString(m.value)
            return message,None
        except Exception as e:
            logger.debug('Error Handling {} of Kafka message {}'.format(e, m.key))
            return None,e

    def handle_incoming_proto_msg(self,m):
        logger.info(
            '> Incoming Message Handled {}:{}:{}: key= {} value= {}'.format(m.topic, m.partition, m.offset, m.key,
                                                                            m.value))
        proto,e  = self.process_proto_message(m)

        # handle invalid proto message
        if proto is None:
            proto = tr451_vomci_nbi_message_pb2.Msg()
            self.send_unsuccessful_response(None, proto.ParseFromString(m.value),str(e))
            return

        er_rsp = tr451_vomci_nbi_message_pb2.Error()
        response = proto
        payload = None
        yangpayload = {}
        logger.debug("Parsed protobuf message is: {}".format(proto))

        # check if header and body exist
        if proto.HasField('header') and proto.HasField('body'):
            hdr = proto.header
            logger.info('Extracted Header of the protobuf msg: {}'.format(hdr))
            body = proto.body
            logger.info('Extracted Body of the protobuf msg: {}'.format(body))
        else:
            logger.error("Header and/or body of the received protobuf message is NULL")
            er_string = "Received a null protobuff"
            self.send_unsuccessful_response(None, proto, er_string)
            return

        # validate header
        if not(hdr.msg_id and hdr.sender_name and hdr.recipient_name and hdr.object_name):
            logger.error('ERROR. message Header is Malformed')
            return

        # validate body
        sender_name = hdr.sender_name
        obj_type = hdr.OBJECT_TYPE.Name(hdr.object_type)

        if obj_type == 'VOMCI_FUNCTION' or obj_type == 'VOMCI_PROXY':

            if body.WhichOneof('msg_body') == 'request':
                request = body.request
                if request.WhichOneof('req_type') == 'replace_config':
                    input_data = body.request.replace_config.config_inst.decode("utf-8")
                    try:
                        payload = json.loads(input_data)
                    except Exception as e:
                        logger.error('Error {} Handling of input_data {}'.format(e,input_data))
                        self.send_unsuccessful_response(None, proto, str(e))
                        return
                    logger.info('Json dict of yang data:{}'.format(payload))
                    #workaround. The first replace_config sent by the vOLTMF may come empty.
                    #Clearing the configurations would break connectivity with the vOLTMF
                    logger.warning("Treating replace_config as update config")

                elif request.WhichOneof('req_type') == 'action':
                    input_data = body.request.action.input_data.decode("utf-8")
                    try:
                        payload = json.loads(input_data)
                    except Exception as e:
                        logger.error('Error {} Handling of input_data {}'.format(e,input_data))
                        self.send_unsuccessful_response(None, proto, str(e))
                        return
                    logger.info('Json dict of received yang data:{}'.format(payload))
                    
                elif request.WhichOneof('req_type') == 'hello':
                    logger.info('Message Hello received!')
                    msg_hello=request.hello.service_endpoint_name
                    yangpayload['service_endpoint_name'] = msg_hello
                    logger.info('Jason Dict of received service_endpoint_name yang payload:{}'.format(yangpayload))                            
                    self.send_successful_response_hello(m)
                    return 
                
                elif request.WhichOneof('req_type') == 'update_config':
                    updconf = request.update_config
                    if updconf.WhichOneof('req_type') == 'update_config_replica':
                        inDelta = updconf.update_config_replica.delta_config.decode("utf-8")
                        try:
                            payload = json.loads(inDelta)
                        except Exception as e:
                            logger.error('Error {} Handling of delta_config {}'.format(e,inDelta))
                            self.send_unsuccessful_response(None, proto,str(e))
                            return
                        logger.info('Jason Dict of received delta config replica:{}'.format(payload))

                else:
                    logger.error('Error. type not Implemented yet:{}'.format(request.WhichOneof('req_type')))
                    return None

            elif body.WhichOneof('msg_body') == 'response':
                logger.info('msg_type response handling is not implemeneted')
                return None

            elif body.WhichOneof('msg_body') == 'notification':
                logger.info('msg_type notification handling is not implemented')
                return None
            else:
                er_string = "Unknown Message type"
                logger.error(er_string)
                self.send_unsuccessful_response(None, proto, er_string)
                return

        elif obj_type == 'ONU':
            # messages targeted towards ONU
            request = body.request
            if request.WhichOneof('req_type') == 'replace_config':
                input_data = request.replace_config.config_inst.decode("utf-8")
                try:
                    yangpayload['config_inst'] = json.loads(input_data)
                except Exception as e:
                    logger.error('Error {} Handling of config_inst {}'.format(e,input_data))
                    self.send_unsuccessful_response(None, proto, str(e))
                    return
                logger.info('Json dict of received yang request:{}'.format(yangpayload))
            elif request.WhichOneof('req_type') == 'update_config':
                updconf = request.update_config
                
                if updconf.WhichOneof('req_type') == 'update_config_inst':
                    inCurrent = updconf.update_config_inst.current_config_inst.decode("utf-8")
                    try:
                        current = json.loads(inCurrent)
                    except Exception as e:
                        logger.error('Error {} Handling of current_config_inst {}'.format(e,inCurrent))
                        self.send_unsuccessful_response(None, proto,str(e))
                        return
                    logger.info('Json dict of received current config yang request:{}'.format(current))
                    inDelta =  updconf.update_config_inst.delta_config.decode("utf-8")
                    try:
                        delta = json.loads(inDelta)
                    except Exception as e:
                        logger.error('Error {} Handling of delta_config {}'.format(e,inDelta))
                        self.send_unsuccessful_response(None, proto,str(e))
                        return
                    yangpayload['current_config_inst'] = current
                    yangpayload['delta_config'] = delta
                    logger.info('Json Dict of received delta config yang payload:{}'.format(yangpayload))
                
                elif updconf.WhichOneof('req_type') == 'update_config_replica':
                    inDelta = updconf.update_config_replica.delta_config.decode("utf-8")
                    try:
                        yangpayload['delta_config'] = json.loads(inDelta)
                    except Exception as e:
                        logger.error('Error {} Handling of delta_config {}'.format(e,inDelta))
                        self.send_unsuccessful_response(None, proto,str(e))
                        return
                    logger.info('Jason Dict of received delta config replica:{}'.format(yangpayload))
                
                else:
                    logger.info('unsupported update_config yang request {} for object type ONU'.format(
                        updconf.WhichOneof('req_type')))
                    return
            elif request.WhichOneof('req_type') == 'get_data':
                # filters are not supported yet
                first_filter = request.get_data.filter[0].decode("utf-8")
                try:
                    yangpayload['get_data'] = json.loads(first_filter)
                except Exception as e:
                    logger.error('Error {} Handling of config_inst {}'.format(e,input_data))
                    self.send_unsuccessful_response(None, proto, str(e))
                    return
                logger.info('Json dict of received yang request:{}'.format(yangpayload))
                pass
            else:
                logger.info('unsupported yang request {} for object type ONU'.format(
                    request.WhichOneof('req_type')))
                return
        
        elif obj_type == 'VOLTMF':
            logger.info('OBJECT TYPE is VOLTMF, Not Implemented Yet')
            return
        else:
            logger.error('Error. Unknown OBJECT TYPE')
            return

        # process the message
        onu_name = None
        olt_name = None
        channel_termination = None
        onu_id = None
        if payload is not None:
            if 'bbf-vomci-function:managed-onus' in payload:
                onudata = payload['bbf-vomci-function:managed-onus']
            elif 'bbf-vomci-proxy:managed-onus' in payload:
                onudata = payload['bbf-vomci-proxy:managed-onus']
            elif 'bbf-vomci-function:vomci' in payload:
                onudata = payload['bbf-vomci-function:vomci']
            elif 'bbf-vomci-proxy:vomci' in payload:
                onudata = payload['bbf-vomci-proxy:vomci']
            else:
                er_string = "Can't decode the payload"
                self.send_unsuccessful_response(None, proto, er_string)
                return
            logger.info('Extracted onu data:{}'.format(onudata))

            if 'create-onu' in onudata:
                data = onudata['create-onu']
                onu_name = data["name"]
                if onu_name is None:
                    er_string = "onu_name is NONE"
                    self.send_unsuccessful_response(None, proto, er_string)
                    return
                self.proto_resp[onu_name] = response
                self._vomci.trigger_create_onu(onu_name)
                self._vomci.update_configuration_in_db()
            elif 'managed-onu' in onudata:
                for data in onudata['managed-onu']:
                    onu_name = None
                    if 'name' in data:
                        onu_name = data['name']
                    if onu_name is None:
                        er_string = "onu-name is NONE"
                        logger.error(er_string)
                        self.send_unsuccessful_response(None, proto, er_string)
                        return

                    self.proto_resp[onu_name] = response
                    if 'delete-onu' in data:
                        logger.info('Triggering ONU Delete for:{}'.format(onu_name))
                        self._vomci.trigger_delete_onu(onu_name)
                        self._vomci.update_configuration_in_db()
                    elif 'set-onu-communication' in data:
                        epdata = data.get('set-onu-communication')
                        if epdata is None:
                            er_string = "ONU header is missing in the payload for ONU {}".format(onu_name)
                            logger.error(er_string)
                            self.send_unsuccessful_response(None, proto, er_string)
                            return
                        onu_header = epdata['onu-attachment-point']
                        olt_name = onu_header.get('olt-name')
                        channel_termination = onu_header.get('channel-termination-name')
                        onu_id = onu_header.get('onu-id')
                        if onu_id is not None:
                            try:
                                onu_tc_id = int(onu_id)
                            except:
                                er_string = "ONU {}: Invalid TC ONU ID {}".format(onu_name, onu_id)
                                logger.error(er_string)
                                self.send_unsuccessful_response(None, proto, er_string)
                                return
                        available = 'onu-communication-available' in epdata and \
                                    epdata['onu-communication-available'] or False
                        olt_endpoint_name = epdata.get('olt-remote-endpoint-name')
                        if 'voltmf-remote-endpoint-name' in epdata:
                            south_endpoint_name = epdata['voltmf-remote-endpoint-name']
                        elif 'vomci-function-remote-endpoint-name' in epdata:
                            south_endpoint_name = epdata['vomci-function-remote-endpoint-name']
                        if available:
                            if olt_endpoint_name is None:
                                er_string = "ONU {}: olt-remote-endpoint-name must be set if onu-communication-available is True".format(
                                    onu_name)
                                logger.error(er_string)
                                self.send_unsuccessful_response(None, proto, er_string)
                                return
                            if channel_termination is None:
                                er_string = "ONU {}: channel-termination must be set if onu-communication-available is True".format(
                                    onu_name)
                                logger.error(er_string)
                                self.send_unsuccessful_response(None, proto, er_string)
                                return
                            if onu_id is None:
                                er_string = "ONU {}: onu-id must be set if onu-communication-available is True".format(
                                    onu_name)
                                logger.error(er_string)
                                self.send_unsuccessful_response(None, proto, er_string)
                                return

                        # Handle set_onu_communication
                        logger.info('Triggering set_onu_communication for onu_id:{} \
                                    olt-name:{} olt_endpoint_name:{} \
                                    south_endpoint_name:{}'.format(onu_id,olt_name,olt_endpoint_name,south_endpoint_name))
                        self._vomci.trigger_set_onu_communication(olt_name, onu_name, channel_termination,
                                                                  onu_tc_id, available, olt_endpoint_name,
                                                                  south_endpoint_name, sender_name)
                        self._vomci.update_configuration_in_db()
                    else:
                        er_string = "UNIMPLEMENTED Request"
                        logger.error(er_string)
                        self.send_unsuccessful_response(None, proto, er_string)
                        return
            elif 'remote-network-function' in onudata:
                #handle nf-client
                nf_client = onudata['remote-network-function']['nf-client']
                if 'enabled' not in nf_client or nf_client['enabled']:
                    remote_endpoints = nf_client['nf-initiate']['remote-endpoints']['remote-endpoint']
                    for endpoint in remote_endpoints:
                        remote_endpoint_name = endpoint['name']
                        local_endpoint_name = endpoint['local-endpoint-name']
                        access_points = endpoint['access-point']
                        nf_type = endpoint['nf-type']

                        #kafka configuration
                        if nf_type == 'bbf-network-function-types:voltmf-type':
                            # a VNF can suppport only one kafka endpoint (with a VOLTMF). 
                            # The first kafka endpoint configured is assumed as the interface with the vOLTMF.
                            # If more kafka endpoints are present in the configuration sent to the vOMCI function/proxy, they will be ignored.
                            if self.local_endpoint_name is None and self.remote_endpoint_name is None: #if not assigned to an endpoint
                                self.local_endpoint_name = local_endpoint_name
                                self.remote_endpoint_name = remote_endpoint_name
                            #if configuration is not directed to this local endpoint or comes from a different remote endpoint than the assigned
                            if self.local_endpoint_name != local_endpoint_name or self.remote_endpoint_name != remote_endpoint_name:
                                continue #skip it

                            #kafka bootstrap servers
                            kafka_agent = endpoint['kafka-agent']['kafka-agent-parameters']
                            client_id = kafka_agent['client-id']
                            brokers = []
                            for access_point in access_points:
                                kafka_name = access_point['name']
                                transport_parameters = access_point['kafka-agent']['kafka-agent-transport-parameters']
                                kafka_server = transport_parameters['remote-address']
                                if 'remote-port' in transport_parameters:
                                    kafka_port = transport_parameters['remote-port']
                                else:
                                    kafka_port = DEFAULT_KAFKA_PORT
                                kafka_broker = kafka_server+':'+str(kafka_port)

                                brokers.append(kafka_broker)
                            self._vomci._kafka_if.add_bootstrap_servers(brokers)

                            #producer
                            if 'publication-parameters' in kafka_agent:
                                publication_topics = kafka_agent['publication-parameters']['topic']
                            else:
                                publication_topics = []
                            response_topics = []
                            notification_topics = []
                            for topic in publication_topics:
                                if topic['purpose'] == 'VOMCI_RESPONSE':
                                    response_topics.append(topic['name'])
                                elif topic['purpose'] == 'VOMCI_NOTIFICATION':
                                    notification_topics.append(topic['name'])
                            self._producer.add_topics(response_topics)
                            self._producer.add_notification_topics(notification_topics)

                            #consumer
                            if kafka_agent['consumption-parameters']:
                                consumption_topics = kafka_agent['consumption-parameters']['topic']
                            else:
                                consumption_topics = []
                            
                            consumer_topics = []
                            for topic in consumption_topics:
                                if topic['purpose'] == 'VOMCI_REQUEST':
                                    consumer_topics.append(topic['name'])
                            self._consumer.add_topics(consumer_topics)
                        
                        #grpc client configuration
                        elif nf_type == 'bbf-network-function-types:vomci-function-type':
                            for access_point in access_points:
                                point_name = access_point['name']
                                params = access_point['grpc']['grpc-transport-parameters']
                                adress = params['remote-address']
                                port = params['remote-port']
                                self._vomci.trigger_create_grpc_connection(adress, port)
                    self.send_successful_update_config_response(m)
                else:
                    #handle enabled: false
                    self._consumer.stop()
                    return

                #nf-server
                if 'nf-server' in onudata['remote-network-function']:
                    nf_server = onudata['remote-network-function']['nf-server']
                    if 'enabled' not in nf_server or nf_server['enabled']:
                        listen_endpoints = nf_server['listen']['listen-endpoint']
                        for endpoint in listen_endpoints:
                            endpoint_name = endpoint['name']
                            grpc_params = endpoint['grpc']['grpc-server-parameters']

                            name = grpc_params['local-endpoint-name']
                            adress = grpc_params['local-address']
                            if 'local-port' in grpc_params:
                                port = grpc_params['local-port']
                            else:
                                port = DEFAULT_GRPC_SERVER_PORT
                            self._vomci.trigger_start_grpc_server(name, adress, port)
                    else:
                        #TODO handle enabled: false
                        pass
                    self._vomci.update_configuration_in_db()
            else:
                if obj_type == 'ONU':
                    er_string = "missing ONU data"
                    logger.error(er_string)
                    self.send_unsuccessful_response(None, proto, er_string)
                else:
                    logger.info("Request for {} with empty data.".format(obj_type))
                    self.send_successful_update_config_response(m)
                return
        elif yangpayload:
            onu_name = hdr.object_name
            if onu_name is None:
                er_string = "ONU Name is None"
                logger.error(er_string)
                self.send_unsuccessful_response(None, proto, er_string)
                return

            self.proto_resp[onu_name] = response
            managed_onu = ManagementChain.GetOnu(onu_name)
            if managed_onu is None:
                er_string = 'ONU {} not in the managed-onus database'.format(onu_name)
                logger.error(er_string)
                self.send_unsuccessful_response(None, proto, er_string)
                return

            # Communication path to the ONU must be available
            if not managed_onu.IsConnected():
                er_string = 'ONU {}: communication path is not available'.format(onu_name)
                logger.error(er_string)
                self.send_unsuccessful_response(None, proto, er_string)
                return
            olt_name = (managed_onu.olt_name,managed_onu.downstream_endpoint_name)
            logger.info('Starting configuration of ONU {} at OLT {} ..'.format(onu_name, olt_name))
            try:
                ret_val = extractPayload(self._vomci, onu_name, olt_name, yangpayload)
                if ret_val != OMHStatus.OK:
                    er_string = "payload processsing failed for ONU:{},reason:{}".format(onu_name,str(ret_val))
                    logger.error(er_string)
                    self.send_unsuccessful_response(None, proto, er_string)
                    return
                # handler was submitted. response will be sent when it finishes
            except Exception as e:
                logger.error("extractPayload failed for ONU:{},reason:{}".format(onu_name,e))
                self.send_unsuccessful_response(None, proto, str(e))
                return
        else:
            logger.error('ERROR. Payload is NULL')
            er_string = "Yang Payload is NULL"
            self.send_unsuccessful_response(None, proto, er_string)
            return
        return

    def set_bootstrap_servers(self, servers: list):
        self._topics = list(set(servers)) #using set to avoid duplicates

    def add_bootstrap_servers(self, servers: list):
        myServers = self._bootstrap_servers + servers
        self.set_bootstrap_servers(myServers)
        logger.info('Added bootstrap servers {}'.format(servers))

    def send_successful_response(self, onu):
        if isinstance(onu, str):
            onu_name = onu
        else:
            onu_name = onu.onu_name
        if onu_name in self.proto_resp:
            rsp = tr451_vomci_nbi_message_pb2.Msg()
            msg = tr451_vomci_nbi_message_pb2.Msg()
            stat = tr451_vomci_nbi_message_pb2.Status()
            msg = self.proto_resp[onu_name]
            rsp.header.msg_id = msg.header.msg_id
            rsp.header.recipient_name = msg.header.sender_name
            rsp.header.sender_name = msg.header.recipient_name
            rsp.header.object_name = msg.header.object_name
            ob_type = msg.header.OBJECT_TYPE.Name(msg.header.object_type)
            if ob_type == tr451_vomci_nbi_message_pb2.Header.OBJECT_TYPE.VOMCI_FUNCTION:
                rsp.header.object_type = tr451_vomci_nbi_message_pb2.Header.OBJECT_TYPE.VOMCI_FUNCTION
            if ob_type == tr451_vomci_nbi_message_pb2.Header.OBJECT_TYPE.VOMCI_PROXY:
                rsp.header.object_type = tr451_vomci_nbi_message_pb2.Header.OBJECT_TYPE.VOMCI_PROXY
            if ob_type == tr451_vomci_nbi_message_pb2.Header.OBJECT_TYPE.ONU:
                rsp.header.object_type = tr451_vomci_nbi_message_pb2.Header.OBJECT_TYPE.ONU

            tp = msg.body.request.WhichOneof('req_type')
            del self.proto_resp[onu_name]
            if tp == 'rpc':
                stat.status_code = tr451_vomci_nbi_message_pb2.Status.StatusCode.OK
                rsp.body.response.rpc_resp.status_resp.CopyFrom(stat)
            elif tp == 'action':
                rsp.body.response.action_resp.status_resp.status_code = int()
            if tp == 'update_config':
                rsp.body.response.update_config_resp.status_resp.status_code = int()
            elif tp == 'replace_config':
                rsp.body.response.replace_config_resp.status_resp.status_code = int()
            elif tp == 'get_data':                
                first_filter = msg.body.request.get_data.filter[0].decode("utf-8")
                yang_response = bytes(get_yang_response(onu, first_filter),"utf-8")
                rsp.body.response.get_resp.data = yang_response
            else:
                logger.error('Unknown request type:{}'.format(tp))
            logger.info('sending the SUCCESS protobuf response to VOLTMF:{}'.format(rsp))
            self._producer.send_proto_response(rsp)

    def send_successful_update_config_response(self, m):
            rsp = tr451_vomci_nbi_message_pb2.Msg()
            msg = tr451_vomci_nbi_message_pb2.Msg()
            msg.ParseFromString(m.value)
            rsp.header.msg_id = msg.header.msg_id
            rsp.header.recipient_name = msg.header.sender_name
            rsp.header.sender_name = msg.header.recipient_name
            rsp.header.object_name = msg.header.object_name

            ob_type = msg.header.OBJECT_TYPE.Name(msg.header.object_type)
            if ob_type == tr451_vomci_nbi_message_pb2.Header.OBJECT_TYPE.VOMCI_FUNCTION:
                rsp.header.object_type = tr451_vomci_nbi_message_pb2.Header.OBJECT_TYPE.VOMCI_FUNCTION
            if ob_type == tr451_vomci_nbi_message_pb2.Header.OBJECT_TYPE.VOMCI_PROXY:
                rsp.header.object_type = tr451_vomci_nbi_message_pb2.Header.OBJECT_TYPE.VOMCI_PROXY
            if ob_type == tr451_vomci_nbi_message_pb2.Header.OBJECT_TYPE.ONU:
                rsp.header.object_type = tr451_vomci_nbi_message_pb2.Header.OBJECT_TYPE.ONU
            tp = msg.body.request.WhichOneof('req_type')
            if tp == 'update_config':
                rsp.body.response.update_config_resp.status_resp.status_code = int()
                logger.info('sending the SUCCESS protobuf response to VOLTMF:{}'.format(rsp))
                self._producer.send_proto_response(rsp)
            if tp == 'replace_config':
                rsp.body.response.replace_config_resp.status_resp.status_code = int()
                logger.info('sending the SUCCESS protobuf response to VOLTMF:{}'.format(rsp))
                self._producer.send_proto_response(rsp)
            else:
                logger.error('Unknown request type:{}'.format(tp))

    def send_successful_response_hello(self,m):

            rsp = tr451_vomci_nbi_message_pb2.Msg()
            msg = tr451_vomci_nbi_message_pb2.Msg()
            msg.ParseFromString(m.value)
            rsp.header.msg_id = msg.header.msg_id
            rsp.header.recipient_name = msg.header.sender_name
            rsp.header.sender_name = msg.header.recipient_name
            rsp.header.object_name = msg.header.object_name
            
            if (msg.header.object_type == tr451_vomci_nbi_message_pb2.Header.OBJECT_TYPE.VOMCI_FUNCTION or 
                 msg.header.object_type == tr451_vomci_nbi_message_pb2.Header.OBJECT_TYPE.VOMCI_PROXY):
                     rsp.header.object_type = msg.header.object_type

            else:
                #Should send a notification to the vOLTMF, but currently such notification is not yet definied
                logger.error('Wrong Object_Type.Name. Can t send a response to Hello')
                return
            tp = msg.body.request.WhichOneof('req_type')

            if tp == 'hello':
                rsp.body.response.hello_resp.service_endpoint_name = 'voltmf'
                endpoint_name = rsp.body.response.hello_resp.service_endpoint_name                                                                                                                                                                                                                                                                                                                                     

                nfInformation =  tr451_vomci_nbi_message_pb2.NFInformation()
                capabilities=tr451_vomci_nbi_message_pb2.NFInformation.NFCapability.ONU_STATE_ONLY_SUPPORT
                nfInformation.capabilities.extend([capabilities])
                nfInformation.nf_types.update({'vendor-name' : 'Broadband Forum', 'software-version': '5.0.0'})    

                rsp.body.response.hello_resp.network_function_info.extend([nfInformation])
                logger.info('sending the SUCCESS protobuf response to VOLTMF:{}'.format(rsp))
                self._producer.send_proto_response(rsp)
                
                                                                                                                                                                                      

    def send_error_msg(self, msg, er_string):  #To DO                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
        er_rsp = tr451_vomci_nbi_message_pb2.Error()                                                                                                                                                                                                                                                                                                                                                                                                         
        rsp = tr451_vomci_nbi_message_pb2.Msg()

        er_rsp.error_type = "application"
        er_rsp.error_tag = "invalid-value"
        er_rsp.error_severity = "error"
        er_rsp.error_app_tag = ""
        if er_string is not None:
            er_rsp.error_message  = er_string
        else:
            er_rsp.error_message = "Invalid parameter"
        tp = msg.body.request.WhichOneof('req_type')
        if tp == 'rpc':
            er_rsp.error_path = "/bbf-vomci-func:create-onu/name"
        self._producer.send_proto_response(msg)

    def send_unsuccessful_response(self, onu_name, gpb=None, error_msg=None):
        rsp = tr451_vomci_nbi_message_pb2.Msg()
        er_rsp = tr451_vomci_nbi_message_pb2.Error()

        logger.info("Sending unsuccessful response. onu_name={} gpb {} error_msg='{}'".format(
            onu_name, (gpb is None) and "set" or "None", error_msg))
        msg = None
        if gpb is not None:
            msg = gpb
        elif onu_name is not None and onu_name in self.proto_resp:
            msg = self.proto_resp[onu_name]
            del self.proto_resp[onu_name]
        if msg is None:
            logger.error('!!! Internal error. msg is None. onu_name={} proto_resp={} gpb={}'.format(onu_name, self.proto_resp, gpb))
            assert False

        rsp.header.msg_id = msg.header.msg_id
        rsp.header.recipient_name = msg.header.sender_name
        rsp.header.sender_name = msg.header.recipient_name
        rsp.header.object_name = msg.header.object_name
        ob_type = msg.header.OBJECT_TYPE.Name(msg.header.object_type)
        if onu_name is not None and onu_name in self.proto_resp:
            del self.proto_resp[onu_name]
        if ob_type == 'VOMCI_FUNCTION':
            rsp.header.object_type = tr451_vomci_nbi_message_pb2.Header.OBJECT_TYPE.VOMCI_FUNCTION
        if ob_type == 'VOMCI_PROXY':
            rsp.header.object_type = tr451_vomci_nbi_message_pb2.Header.OBJECT_TYPE.VOMCI_PROXY
        if ob_type == 'ONU':
            rsp.header.object_type = tr451_vomci_nbi_message_pb2.Header.OBJECT_TYPE.ONU

        tp = msg.body.request.WhichOneof('req_type')
        logger.info('received request type :{}'.format(tp))
        if error_msg is not None:
            er_rsp.error_message  = error_msg
        else:
            er_rsp.error_message = "Invalid parameter"
        er_rsp.error_severity = "error"
        er_rsp.error_type = "application"
        if tp == 'rpc':
            rsp.body.response.rpc_resp.status_resp.status_code = 1
            er_rsp.error_path = "/bbf-vomci-func:create-onu/name"
            rsp.body.response.rpc_resp.status_resp.error.append(er_rsp)
        elif tp == 'action':
            rsp.body.response.action_resp.status_resp.status_code = 1
            onu_str = "/bbf-vomci-function:managed-onus/managed-onu[name='onu1']"
            if onu_name is not None:
                st = onu_str.replace("onu1", onu_name)
                er_rsp.error_path = st
            else:
                er_rsp.error_path = onu_str
            rsp.body.response.action_resp.status_resp.error.append(er_rsp)
        elif tp == 'replace_config':
            rsp.body.response.replace_config_resp.status_resp.status_code = 1
            rsp.body.response.replace_config_resp.status_resp.error.append(er_rsp)
        else:
            logger.error('Unknown request type:{}'.format(tp))
        logger.info('GPB Processing failed,sending Unsuccessful response to VOLTMF:{}'.format(rsp))
        self._producer.send_proto_response(rsp)

    def send_alignment_notification(self, onu_name: str, is_aligned: bool):
        notification_gpb = self.make_alignment_notification(onu_name, is_aligned)
        self._producer.send_proto_notification(notification_gpb)

    def make_alignment_notification(self, onu_name: str, is_aligned: bool):
        notif = tr451_vomci_nbi_message_pb2.Msg()
        notif.header.msg_id = "1"
        notif.header.sender_name = self._vomci.name
        managed_onu = ManagementChain.GetOnu(onu_name)
        notif.header.recipient_name = managed_onu.voltmf_name
        notif.header.object_name = onu_name
        header = '{"bbf-vomci-function:onu-alignment-status":{'
        iso_time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc, microsecond=0).isoformat()
        event_time = '"event-time" : "'+iso_time+'"'
        onu = '"onu-name":"'+onu_name+'"'
        if is_aligned:
            alignment_status = '"alignment-status": "aligned"'
        else:
            alignment_status = '"alignment-status": "unaligned"'
        data_str = header + event_time + ',' + onu + ',' + alignment_status + '}}'
        notif.body.notification.data = bytes(data_str, 'utf-8')
        return notif

