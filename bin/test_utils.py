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

#
# Common test utilities. Implement a common subset of
# command line parameters and a test OMH handler that
# can execute multiple OMH nadlers in a sequence.
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

""" Initializatiuon common for all tests """
import argparse
import logging
import os
import sys
import threading
import time
from typing import Optional, Tuple, Any, Union
from omcc.grpc.grpc_client import GrpcClientChannel
from omcc.grpc.grpc_server import GrpcServer
from omh_nbi.omh_handler import OmhHandler, OMHStatus
from omh_nbi.onu_driver import OnuDriver
from omh_nbi.handlers.onu_mib_reset import OnuMibResetHandler
from omh_nbi.handlers.onu_mib_upload import OnuMibUploadHandler
from omh_nbi.handlers.onu_activate import OnuActivateHandler
from database.omci_olt import OltDatabase
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

class TestOmhDriver:
    handler_map = {'MIB_RESET': OnuMibResetHandler,
               'MIB_UPLOAD': OnuMibUploadHandler,
               'ACTIVATE_ONU': OnuActivateHandler}

    def __init__(self, name: Optional[str] = None, any_handler: bool = True):
        self._any_handler = any_handler
        self._olt = None
        self._handler_type = None
        self._onu = None
        self._args = None
        self._sem = threading.Semaphore(value=0)
        self._name = name
        self._status = OMHStatus.OK
        self._server = None

        valid_handler_names = ''
        for item in self.handler_map.items():
            valid_handler_names += ' ' + item[0]
        self._valid_handler_names = valid_handler_names
        # create the parser and add common arguments
        prog_basename = os.path.basename(sys.argv[0])
        (prog_root, _) = os.path.splitext(prog_basename)
        self._parser = argparse.ArgumentParser(prog=prog_root, description=__doc__,
                                               fromfile_prefix_chars='@',
                                               formatter_class=argparse.RawDescriptionHelpFormatter)
        # Initialize command line parameter parser
        # Default command line argument values
        default_polt_host = 'localhost'
        default_port = 50000
        default_server_mode = False
        default_log_level = 2 # debug 
        default_vomci_name = 'vomci1'
        default_onu_name = "onu.1.2"
        default_cterm_name = 'channeltermination.1'
        default_onu_id = 2
        default_background = False
        default_start_tci = 1
        default_iters = 1
        default_dump = False
        default_timeout = 2.0
        default_retries = 2

        if self._any_handler:
            self._parser.add_argument('-f', '--handler', type=str, default=None,
                help='OMH handler to execute: ' + valid_handler_names)
        self._parser.add_argument('-a', '--polt-host', type=str, default=default_polt_host,
            help='pOLT DNS name or IP address; default: %r' % default_polt_host)
        self._parser.add_argument('-p', '--port', type=int, default=default_port,
            help='pOLT/Server port number; default: %r' % default_port)
        self._parser.add_argument('-s', '--server-mode', type=bool, default=default_server_mode,
            help='Server Mode: %r' % default_server_mode)
        self._parser.add_argument('-l', '--loglevel', type=int, default=default_log_level,
            help='logging level (0=errors+warnings, 1=info, 2=debug); default: %r' % default_log_level)
        self._parser.add_argument('-v', '--vomci-name', type=str, default=default_vomci_name,
            help='vOMCI name; default: %r' % default_vomci_name)
        self._parser.add_argument('-n', '--onu-name', type=str, default=default_cterm_name,
            help='ONU name; default: %r' % default_onu_name)
        self._parser.add_argument('-c', '--cterm-name', type=str, default=default_cterm_name,
            help='channel-termination name; default: %r' % default_cterm_name)
        self._parser.add_argument('-o', '--onu-id', type=int, default=default_onu_id,
            help='ONU id; default: %r' % default_onu_id)
        self._parser.add_argument('-t', '--tci', type=int, default=default_start_tci,
            help='Starting TCI value; default: %r' % default_start_tci)
        self._parser.add_argument('-b', '--background', type=bool, default=default_background,
            help='Run OMH handler in the background: %r' % default_background)
        self._parser.add_argument('-i', '--iters', type=int, default=default_iters,
            help='Number of times to execute the OMH handler: %r' % default_iters)
        self._parser.add_argument('-d', '--dump-mib', type=bool, default=default_dump,
            help='Dump ONU MIB: %r' % default_dump)
        self._parser.add_argument('--timeout', type=float, default=default_timeout,
            help='Message timeout (s): %r' % default_timeout)
        self._parser.add_argument('--retries', type=int, default=default_retries,
            help='Max number of retries: %r' % default_retries)

    @property
    def parser(self):
        return self._parser

    @property
    def args(self):
        return self._args

    def parse_arguments(self, argv : Optional[Tuple[str, ...]] = None):
        """ Parse commend line arguments.
            Returns handler_type, args
        """
        prog_basename = os.path.basename(sys.argv[0])
        (prog_root, _) = os.path.splitext(prog_basename)

        if argv is None:
            argv = sys.argv

        self._args = self._parser.parse_args(argv[1:])

        # handler parameter is mandatory
        if self._any_handler:
            if self._args.handler is None:
                print("-f, --handler parameter is mandatory. Valid values:{}".format(self._valid_handler_names))
                return None, None
            if self._args.handler not in self.handler_map:
                print("--handler value is invalid. Supported values:{}".format(self._valid_handler_names))
                return None, None
            self._handler_type = self.handler_map[self._args.handler]
            self._name = self._name is None and self._args.handler or self._name

        loglevel_map = {0: logging.WARN, 1: logging.INFO, 2: logging.DEBUG}
        OmciLogger(level=loglevel_map[self._args.loglevel])
        logger = OmciLogger.getLogger(prog_root)
        logger.debug('args %r' % self._args)
        return self._handler_type, self._args

    def set_handler_type(self, handler_type: Union[OmhHandler, Tuple[OmhHandler, ...]]):
        self._handler_type = handler_type

    def _init_and_connect(self) -> OnuDriver:
        """ Initialize and connect
            Args: args : command line arguments
            Returns: OnuDriver or None of connection failed
        """
        # Create gRPC channel and try to connect
        if (self._args.server_mode):
            logger.info("Test {}: waiting for connection on port {}:{}..".
                format(self._name, self._args.polt_host, self._args.port))
            self._server = GrpcServer(port=self._args.port, name=self._args.vomci_name)
            connections = self._server.connections()
            while len(connections.values()) == 0:
                time.sleep(1)
            connection = list(connections.values())[0];
            connection.connected(connection.remote_endpoint_name)
            olt = OltDatabase.OltGetFirst()
            # Add ONU to the database
            onu = olt.OnuAdd(self._args.onu_name, (self._args.cterm_name, self._args.onu_id), tci=self._args.tci)
        else:
            logger.info("Test {}: connecting to {}:{}..".format(self._name, self._args.polt_host, self._args.port))
            channel = GrpcClientChannel(name=self._args.vomci_name)
            ret_val = channel.connect(host=self._args.polt_host, port=self._args.port)
            if not ret_val:
                logger.warning("Test {}: connection failed".format(self._name))
                return None
            olt = channel.add_managed_onu(channel.remote_endpoint_name, self._args.onu_name, (self._args.cterm_name, self._args.onu_id), tci=self._args.tci)
            logger.info("test_YangtoOmciMapper: connected to the pOLT: {}".format(olt.id))
            onu = olt.OnuGet((self._args.cterm_name, self._args.onu_id))
        logger.info("Test {}: connected to {}".format(self._name, olt.id))
        return onu

    def _update_status(self, status: OMHStatus):
        """ Update status. Preserve failure """
        self._status = (self._status == OMHStatus.OK) and status or self._status

    def _handler_completed(self, handler: OmhHandler):
        """ OMH handler completed callback. Called upon completion if OMH handler is executed in the background
        """
        self._sem.release()

    class TestHandler(OmhHandler):
        """ TestHandler that executes the requested sequnece of OMH handlers as subsidiaries """
        def __init__(self, onu: OnuDriver, handler_types: Tuple[OmhHandler, ...], extra_args: Tuple[Any, ...]):
            handler_type_list = [t.__name__ for t in handler_types]
            super().__init__(name='TestHandler', onu=onu,
                             description=' {}'.format(handler_type_list))
            self._handler_types = handler_types
            self._extra_args = extra_args

        def run_to_completion(self) -> OMHStatus:
            logger.info(self.info())
            for i in range(len(self._handler_types)):
                handler_type = self._handler_types[i]
                extra_args = (self._extra_args is not None and len(self._extra_args) > i) and self._extra_args[i] or None
                handler = extra_args is None and handler_type(self._onu) or handler_type(self._onu, *extra_args)
                status = self.run_subsidiary(handler)
                if status != OMHStatus.OK:
                    break
            return status

    def run(self, extra_args : Optional[Any] = None) -> int:
        """ Run an OMH handler or a list of OMH handlers --iter number of times """
        if self._args is None:
            self.parse_arguments()
        if self._handler_type is None:
            logger.error('handler type must be set')
            return -1
        if not isinstance(self._handler_type, tuple) and not isinstance(self._handler_type, list):
            self._handler_type = (self._handler_type,)
            extra_args = (extra_args, )

        self._onu = self._init_and_connect()
        if self._onu is None:
            return -1
        self._onu.set_flow_control(max_retries=self._args.retries, ack_timeout=self._args.timeout)

        # Run the sequence the requiured number of iterations
        for iter in range(self._args.iters):
            if self._args.iters > 1:
                logger.info("Test {}: iteration {}".format(self._name, iter + 1))
            handler = TestOmhDriver.TestHandler(self._onu, self._handler_type, extra_args)
            if self._args.background:
                logger.info("Test {}: starting execution in the background".format(self._name))
                handler.start(self._handler_completed)
                logger.info("Test {}: Waiting for completion..".format(handler._name))
                self._sem.acquire()
            else:
                logger.info("Test {}: starting execution in the foreground".format(self._name))
                handler.run()
            logger.info("Test {}: Finished execution. Status: {}".format(self._name, handler.status.name))
            self._update_status(handler.status)
            if handler.status != OMHStatus.OK:
                break

        if self._onu.olt.channel is not None:
            self._onu.olt.channel.disconnect()
        if self._server is not None:
            self._server.stop()
        if self._args.dump_mib:
            self._onu.dump_mib()

        return self._status.value
