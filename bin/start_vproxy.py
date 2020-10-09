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
import threading
import time
import logging

import proxy.proxy as proxy
from omci_logger import OmciLogger

OmciLogger(level=logging.DEBUG)
logger = OmciLogger.getLogger(__name__)


def start_proxy_threads():
    # Create a thread that will listen for kafka
    logger.debug('Starting a thread that will send gRPC messages')
    vproxy = proxy.Proxy("temp_proxy_name")
    # grpc_client_thread = threading.Thread(name="grpc_client", target=vproxy.create_vomci_connection)
    # grpc_client_thread.start()
    vproxy.create_polt_connection_server()


def start_gRPC_simulator():
    # Create a thread that will listen for kafka
    logger.debug('Starting a thread that will send gRPC messages')
    vproxy = proxy.Proxy("gRPC_simulator")
    grpc_client_thread = threading.Thread(name="grpc_client", target=vproxy.create_vomci_connection)
    grpc_client_thread.start()

def main():
    time.sleep(4)
    if os.getenv("IS_SIMULATOR"):
        start_gRPC_simulator()
    else:
        start_proxy_threads()


if __name__ == '__main__':
    main()
