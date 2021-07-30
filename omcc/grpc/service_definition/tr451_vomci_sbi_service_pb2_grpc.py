# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from . import tr451_vomci_sbi_message_pb2 as tr451__vomci__sbi__message__pb2


class VomciHelloSbiStub(object):
    """Missing associated documentation comment in .proto file"""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.HelloVomci = channel.unary_unary(
                '/tr451_vomci_sbi_service.v1.VomciHelloSbi/HelloVomci',
                request_serializer=tr451__vomci__sbi__message__pb2.HelloVomciRequest.SerializeToString,
                response_deserializer=tr451__vomci__sbi__message__pb2.HelloVomciResponse.FromString,
                )


class VomciHelloSbiServicer(object):
    """Missing associated documentation comment in .proto file"""

    def HelloVomci(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_VomciHelloSbiServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'HelloVomci': grpc.unary_unary_rpc_method_handler(
                    servicer.HelloVomci,
                    request_deserializer=tr451__vomci__sbi__message__pb2.HelloVomciRequest.FromString,
                    response_serializer=tr451__vomci__sbi__message__pb2.HelloVomciResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'tr451_vomci_sbi_service.v1.VomciHelloSbi', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class VomciHelloSbi(object):
    """Missing associated documentation comment in .proto file"""

    @staticmethod
    def HelloVomci(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/tr451_vomci_sbi_service.v1.VomciHelloSbi/HelloVomci',
            tr451__vomci__sbi__message__pb2.HelloVomciRequest.SerializeToString,
            tr451__vomci__sbi__message__pb2.HelloVomciResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)


class VomciMessageSbiStub(object):
    """Missing associated documentation comment in .proto file"""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ListenForVomciRx = channel.unary_stream(
                '/tr451_vomci_sbi_service.v1.VomciMessageSbi/ListenForVomciRx',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=tr451__vomci__sbi__message__pb2.VomciMessage.FromString,
                )
        self.VomciTx = channel.unary_unary(
                '/tr451_vomci_sbi_service.v1.VomciMessageSbi/VomciTx',
                request_serializer=tr451__vomci__sbi__message__pb2.VomciMessage.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )


class VomciMessageSbiServicer(object):
    """Missing associated documentation comment in .proto file"""

    def ListenForVomciRx(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def VomciTx(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_VomciMessageSbiServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ListenForVomciRx': grpc.unary_stream_rpc_method_handler(
                    servicer.ListenForVomciRx,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=tr451__vomci__sbi__message__pb2.VomciMessage.SerializeToString,
            ),
            'VomciTx': grpc.unary_unary_rpc_method_handler(
                    servicer.VomciTx,
                    request_deserializer=tr451__vomci__sbi__message__pb2.VomciMessage.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'tr451_vomci_sbi_service.v1.VomciMessageSbi', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class VomciMessageSbi(object):
    """Missing associated documentation comment in .proto file"""

    @staticmethod
    def ListenForVomciRx(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/tr451_vomci_sbi_service.v1.VomciMessageSbi/ListenForVomciRx',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            tr451__vomci__sbi__message__pb2.VomciMessage.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def VomciTx(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/tr451_vomci_sbi_service.v1.VomciMessageSbi/VomciTx',
            tr451__vomci__sbi__message__pb2.VomciMessage.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)