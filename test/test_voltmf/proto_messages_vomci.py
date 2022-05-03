import nbi.grpc.service_definition.tr451_vomci_nbi_message_pb2 as tr451_vomci_nbi_message_pb2

def getSampleProtoVomci(key):
    ret = tr451_vomci_nbi_message_pb2.Msg()
    ret.header.sender_name = "vOLTMF"
    ret.header.recipient_name = "obbaa-vomci"
    ret.header.object_type = ret.header.VOMCI_FUNCTION
    ret.header.object_name = "obbaa-vomci"
    if key == 'hello':
        ret.header.msg_id = "1"
        ret.header.sender_name = "vOLTMF"
        ret.header.recipient_name = "vomci1"
        ret.header.object_type = ret.header.VOMCI_FUNCTION
        ret.header.object_name = "vomci1"
        ret.body.request.hello.service_endpoint_name = "volmf-endpoint"
    elif key == 'create':
        ret.header.msg_id = "3"
        ret.body.request.action.input_data = b'{"bbf-vomci-function:managed-onus":{"create-onu":{"name":"ont1"}}}'
    elif key == 'set':
        ret.header.msg_id = "5"
        ret.body.request.action.input_data = b'{"bbf-vomci-function:managed-onus":{"managed-onu":[{"name":"ont1","set-onu-communication":{"onu-attachment-point":{"olt-name":"OLT1","channel-termination-name":"CT_1","onu-id":1},"voltmf-remote-endpoint-name":"vOLTMF_Kafka","onu-communication-available":true,"olt-remote-endpoint-name":"obbaa-vproxy-grpc-client-1"}}]}}'
    elif key == 'update_config':
        ret.header.msg_id = "7"
        ret.body.request.update_config.update_config_replica.delta_config = b'{"bbf-vomci-function:vomci":{"remote-network-function":{"nf-client":{"enabled":true,"nf-initiate":{"remote-endpoints":{"remote-endpoint":[{"name":"obbaa-vomci","nf-type":"bbf-network-function-types:voltmf-type","local-endpoint-name":"vOMCI-kfk-1","kafka-agent":{"kafka-agent-parameters":{"client-id":"client-id2","publication-parameters":{"topic":[{"name":"vomci1-response","purpose":"VOMCI_RESPONSE"},{"name":"vomci1-notification","purpose":"VOMCI_NOTIFICATION"}]},"consumption-parameters":{"topic":[{"name":"vomci1-request","purpose":"VOMCI_REQUEST"}]}}},"access-point":[{"name":"obbaa-vomci","kafka-agent":{"kafka-agent-transport-parameters":{"remote-address":"kafka-host"}}}]}]}}},"nf-server":{"enabled":true,"listen":{"listen-endpoint":[{"name":"vOMCI-grpc-1","grpc":{"grpc-server-parameters":{"local-endpoint-name":"vOMCI-grpc-1","local-address":"::","local-port":8100}}}]}}}}}'
    elif key == 'disable':
        ret.header.msg_id = "9"
        ret.body.request.update_config.update_config_replica.delta_config = b'{"bbf-vomci-function:vomci":{"remote-network-function":{"nf-client":{"enabled":false}}}}'
    else:
        ret = None
    return ret
    