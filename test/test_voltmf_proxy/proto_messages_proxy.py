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
        ret.body.request.action.input_data = b'{"bbf-vomci-proxy:managed-onus":{"create-onu":{"name":"ont1"}}}'
    elif key == 'set':
        ret.header.msg_id = "6"
        ret.body.request.action.input_data = b'{"bbf-vomci-proxy:managed-onus":{"managed-onu":[{"name":"ont1","set-onu-communication":{"onu-attachment-point":{"olt-name":"OLT1","channel-termination-name":"CT_1","onu-id":1},"vomci-function-remote-endpoint-name":"vomci1","onu-communication-available":true,"olt-remote-endpoint-name":"proxy-grpc-1"}}]}}'
    elif key == 'update_config':
        ret.header.msg_id = "8"
        mystr = '{"bbf-vomci-proxy:vomci":{"remote-network-function":{"nf-client":{"enabled":true,"nf-initiate":{"remote-endpoints":{"remote-endpoint":[{"name":"obbaa-vproxy","nf-type":"bbf-network-function-types:voltmf-type","local-endpoint-name":"proxy-kfk-1","kafka-agent":{"kafka-agent-parameters":{"client-id":"client-id3","publication-parameters":{"topic":[{"name":"vomci-proxy-response","purpose":"VOMCI_RESPONSE"},{"name":"vomci-proxy-notification","purpose":"VOMCI_NOTIFICATION"}]},"consumption-parameters":{"topic":[{"name":"vomci-proxy-request","purpose":"VOMCI_REQUEST"}]}}},"access-point":[{"name":"obbaa-vproxy","kafka-agent":{"kafka-agent-transport-parameters":{"remote-address":"kafka-host","remote-port":9092}}}]},{"name":"vOMCI-grpc-1","nf-type":"bbf-network-function-types:vomci-function-type","local-endpoint-name":"proxy-grpc-2","access-point":[{"name":"vOMCI-grpc-1","grpc":{"grpc-transport-parameters":{"remote-address":"obbaa-vomci","remote-port":8100}}}]}]}}},"nf-server":{"enabled":true,"listen":{"listen-endpoint":[{"name":"proxy-grpc-2","grpc":{"grpc-server-parameters":{"local-endpoint-name":"proxy-grpc-2","local-address":"::","local-port":8433}}}]}}}}}'
        encoded = bytes(mystr, 'utf-8')
        ret.body.request.update_config.update_config_replica.delta_config = encoded
    elif key == 'disable':
        ret.header.msg_id = "10"
        ret.body.request.update_config.update_config_replica.delta_config = b'{"bbf-vomci-function:vomci":{"remote-network-function":{"nf-client":{"enabled":false}}}}'
    else:
        ret = None
    return ret
    