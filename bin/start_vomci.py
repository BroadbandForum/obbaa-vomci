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
import threading
import time
import logging
from omci_logger import OmciLogger
import vomci
import sys

OmciLogger(level=logging.DEBUG)
logger = OmciLogger.getLogger(__name__)


def start_vomci_threads():
    logger.debug('Starting vomci')
    v_omci = vomci.VOmci()
    v_omci.start()


def main():
        if sys.version_info>=(3,6,0):
                start_vomci_threads()
        else:
                logger.error("Need python >=3.6 version to start the VOMCI")
                return

if __name__ == '__main__':
    main()
