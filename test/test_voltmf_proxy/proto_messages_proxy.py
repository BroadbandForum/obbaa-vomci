import nbi.grpc.service_definition.tr451_vomci_nbi_message_pb2 as tr451_vomci_nbi_message_pb2
import os

def getSampleProtoProxy(key):
    ret = tr451_vomci_nbi_message_pb2.Msg()
    ret.header.sender_name = "vOLTMF"
    ret.header.recipient_name = "proxy-1"
    ret.header.object_type = ret.header.VOMCI_FUNCTION
    ret.header.object_name = "proxy-1"
    if key == 'hello':
        ret.header.msg_id = "2"
        ret.header.sender_name = "vOLTMF"
        ret.header.recipient_name = "proxy-1"
        ret.header.object_type = ret.header.VOMCI_PROXY
        ret.header.object_name = "proxy-1"
        ret.body.request.hello.service_endpoint_name = "volmf-endpoint"
    elif key == 'create':
        ret.header.msg_id = "4"
        ret.body.request.action.input_data = b'{"bbf-vomci-proxy:vomci":{"managed-onus":{"create-onu":{"name":"ont1","xpon-onu-type":"bbf-vomci-types:gpon"}}}}'
    elif key == 'set':
        ret.header.msg_id = "6"
        ret.body.request.action.input_data = b'{"bbf-vomci-proxy:vomci":{"managed-onus":{"managed-onu":[{"name":"ont1","set-onu-communication":{"onu-communication-available":true,"olt-remote-endpoint":"olt-grpc-2","voltmf-remote-endpoint":"vOLTMF_Kafka_1","xpon-onu-type":"bbf-vomci-types:gpon","onu-attachment-point":{"olt-name":"olt-grpc-2","channel-termination-name":"CT_1","onu-id":1}}}]}}}'
    elif key == 'update_config':
        ret.header.msg_id = "8"
        mystr = b'{"bbf-vomci-proxy:vomci":{"remote-nf":{"nf-client":{"enabled": true,"initiate":{"remote-server":[{"name":"vOLTMF_Kafka_1","nf-type":"bbf-network-function-types:voltmf","local-service-endpoint":"vOMCI-kfk-1","bbf-vomci-function-kafka-agent:kafka-agent":{"client-id":"client-id2","publication-parameters":{"topic":[{"name":"vomci1-response","purpose":"VOMCI_RESPONSE"},{"name":"vomci1-notification","purpose":"VOMCI_NOTIFICATION"}]},"consumption-parameters":{"group-id":"group2","topic":[{"name":"vomci1-request","purpose":"VOMCI_REQUEST"}]},"access-point":[{"name":"vOLTMF_Kafka_1","kafka-agent-transport-parameters":{"bbf-vomci-function-kafka-agent-tcp:tcp-client-parameters":{"remote-address":"kafka-host","remote-port":9092}}}]}}]}},"nf-server":{"enabled":true,"listen":{"listen-endpoint":[{"name":"proxy-grpc-1","local-service-endpoint":"vOMCI-grpc-1","bbf-vomci-function-grpc-server:grpc-server":{"bbf-vomci-function-grpc-server-tcp:tcp-server-parameters":{"local-address":"::","local-port":8100}}}]}}}}}'
        encoded = bytes(mystr, 'utf-8')
        ret.body.request.update_config.update_config_replica.delta_config = encoded
    elif key == 'disable':
        ret.header.msg_id = "10"
        ret.body.request.update_config.update_config_replica.delta_config = b'{"bbf-vomci-function:vomci":{"remote-nf":{"nf-client":{"enabled":false}}}}'
    else:
        ret = None
    return ret
    