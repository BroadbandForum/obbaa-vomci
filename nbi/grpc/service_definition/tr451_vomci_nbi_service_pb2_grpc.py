# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
import tr451_vomci_nbi_message_pb2 as tr451__vomci__nbi__message__pb2


class VomciMessageNbiStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Hello = channel.unary_unary(
                '/tr451_vomci_nbi_service.v1.VomciMessageNbi/Hello',
                request_serializer=tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
                response_deserializer=tr451__vomci__nbi__message__pb2.Msg.FromString,
                )
        self.GetData = channel.unary_unary(
                '/tr451_vomci_nbi_service.v1.VomciMessageNbi/GetData',
                request_serializer=tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
                response_deserializer=tr451__vomci__nbi__message__pb2.Msg.FromString,
                )
        self.ReplaceConfig = channel.unary_unary(
                '/tr451_vomci_nbi_service.v1.VomciMessageNbi/ReplaceConfig',
                request_serializer=tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
                response_deserializer=tr451__vomci__nbi__message__pb2.Msg.FromString,
                )
        self.UpdateConfigReplica = channel.unary_unary(
                '/tr451_vomci_nbi_service.v1.VomciMessageNbi/UpdateConfigReplica',
                request_serializer=tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
                response_deserializer=tr451__vomci__nbi__message__pb2.Msg.FromString,
                )
        self.UpdateConfigInstance = channel.unary_unary(
                '/tr451_vomci_nbi_service.v1.VomciMessageNbi/UpdateConfigInstance',
                request_serializer=tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
                response_deserializer=tr451__vomci__nbi__message__pb2.Msg.FromString,
                )
        self.RPC = channel.unary_unary(
                '/tr451_vomci_nbi_service.v1.VomciMessageNbi/RPC',
                request_serializer=tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
                response_deserializer=tr451__vomci__nbi__message__pb2.Msg.FromString,
                )
        self.Action = channel.unary_unary(
                '/tr451_vomci_nbi_service.v1.VomciMessageNbi/Action',
                request_serializer=tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
                response_deserializer=tr451__vomci__nbi__message__pb2.Msg.FromString,
                )
        self.ListenForNotification = channel.unary_stream(
                '/tr451_vomci_nbi_service.v1.VomciMessageNbi/ListenForNotification',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=tr451__vomci__nbi__message__pb2.Msg.FromString,
                )


class VomciMessageNbiServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Hello(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReplaceConfig(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateConfigReplica(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateConfigInstance(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RPC(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Action(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListenForNotification(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_VomciMessageNbiServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Hello': grpc.unary_unary_rpc_method_handler(
                    servicer.Hello,
                    request_deserializer=tr451__vomci__nbi__message__pb2.Msg.FromString,
                    response_serializer=tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
            ),
            'GetData': grpc.unary_unary_rpc_method_handler(
                    servicer.GetData,
                    request_deserializer=tr451__vomci__nbi__message__pb2.Msg.FromString,
                    response_serializer=tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
            ),
            'ReplaceConfig': grpc.unary_unary_rpc_method_handler(
                    servicer.ReplaceConfig,
                    request_deserializer=tr451__vomci__nbi__message__pb2.Msg.FromString,
                    response_serializer=tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
            ),
            'UpdateConfigReplica': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateConfigReplica,
                    request_deserializer=tr451__vomci__nbi__message__pb2.Msg.FromString,
                    response_serializer=tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
            ),
            'UpdateConfigInstance': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateConfigInstance,
                    request_deserializer=tr451__vomci__nbi__message__pb2.Msg.FromString,
                    response_serializer=tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
            ),
            'RPC': grpc.unary_unary_rpc_method_handler(
                    servicer.RPC,
                    request_deserializer=tr451__vomci__nbi__message__pb2.Msg.FromString,
                    response_serializer=tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
            ),
            'Action': grpc.unary_unary_rpc_method_handler(
                    servicer.Action,
                    request_deserializer=tr451__vomci__nbi__message__pb2.Msg.FromString,
                    response_serializer=tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
            ),
            'ListenForNotification': grpc.unary_stream_rpc_method_handler(
                    servicer.ListenForNotification,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'tr451_vomci_nbi_service.v1.VomciMessageNbi', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class VomciMessageNbi(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Hello(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/tr451_vomci_nbi_service.v1.VomciMessageNbi/Hello',
            tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
            tr451__vomci__nbi__message__pb2.Msg.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/tr451_vomci_nbi_service.v1.VomciMessageNbi/GetData',
            tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
            tr451__vomci__nbi__message__pb2.Msg.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ReplaceConfig(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/tr451_vomci_nbi_service.v1.VomciMessageNbi/ReplaceConfig',
            tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
            tr451__vomci__nbi__message__pb2.Msg.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateConfigReplica(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/tr451_vomci_nbi_service.v1.VomciMessageNbi/UpdateConfigReplica',
            tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
            tr451__vomci__nbi__message__pb2.Msg.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateConfigInstance(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/tr451_vomci_nbi_service.v1.VomciMessageNbi/UpdateConfigInstance',
            tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
            tr451__vomci__nbi__message__pb2.Msg.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RPC(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/tr451_vomci_nbi_service.v1.VomciMessageNbi/RPC',
            tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
            tr451__vomci__nbi__message__pb2.Msg.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Action(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/tr451_vomci_nbi_service.v1.VomciMessageNbi/Action',
            tr451__vomci__nbi__message__pb2.Msg.SerializeToString,
            tr451__vomci__nbi__message__pb2.Msg.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ListenForNotification(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/tr451_vomci_nbi_service.v1.VomciMessageNbi/ListenForNotification',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            tr451__vomci__nbi__message__pb2.Msg.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)