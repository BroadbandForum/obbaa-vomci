#!/usr/bin/env python3

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
# gem_port_create and tcont_create OMH handlers test
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

""" Execute an OnuActivateHandler followed by UniSetHandler, TcontCreateHandler and GemPortCreateHandler
    invoke with -h, --help for command-line parameters help
"""
import sys
from bin.test_utils import TestOmhDriver
from omci_logger import OmciLogger
from omh_nbi.handlers.uni_set import UniSetHandler
from omh_nbi.handlers.onu_activate import OnuActivateHandler
from omh_nbi.handlers.tcont_create import TcontCreateHandler
from omh_nbi.handlers.gem_port_create import GemPortCreateHandler
logger = OmciLogger.getLogger(__name__)

DEFAULT_UNI_NAME = 'uni.1'
DEFAULT_UNI_ID = 0
DEFAULT_TCONT_NAME = 'tcont.1'
DEFAULT_ALLOC_ID = 1024
DEFAULT_GEM_PORT_NAME = 'gem.1'
DEFAULT_GEM_PORT_ID = 1025
DEFAULT_TC = 1
DEFAULT_DIRECTION = 'BIDIRECTIONAL'
DEFAULT_ENCRYPTION = 'NO_ENCRYPTION'

def main(argv=None) -> int:
    test = TestOmhDriver(name='UNI_TCONT_GEM_PORT', any_handler=False)
    test.parser.add_argument('--uni-name', type=str, default=DEFAULT_UNI_NAME,
        help='UNI name: %r' % DEFAULT_UNI_NAME)
    test.parser.add_argument('--uni-id', type=int, default=DEFAULT_UNI_ID,
        help='UNI id: %r' % DEFAULT_UNI_ID)
    test.parser.add_argument('--tcont-name', type=str, default=DEFAULT_TCONT_NAME,
        help='TCONT name: %r' % DEFAULT_TCONT_NAME)
    test.parser.add_argument('--alloc-id', type=int, default=DEFAULT_ALLOC_ID,
        help='ALLOC Id: %r' % DEFAULT_ALLOC_ID)
    test.parser.add_argument('--gemport-name', type=str, default=DEFAULT_GEM_PORT_NAME,
        help='GEM port name: %r' % DEFAULT_GEM_PORT_NAME)
    test.parser.add_argument('--gemport-id', type=int, default=DEFAULT_GEM_PORT_ID,
        help='GEMPORT Id: %r' % DEFAULT_GEM_PORT_ID)
    test.parser.add_argument('--tc', type=int, default=DEFAULT_TC,
        help='Traffic Class: %r' % DEFAULT_TC)
    test.parser.add_argument('--direction', type=str, default=DEFAULT_DIRECTION,
        help='GEM port direction: %r' % DEFAULT_DIRECTION)
    test.parser.add_argument('--encryption', type=str, default=DEFAULT_ENCRYPTION,
        help='GEM port encryption: %r' % DEFAULT_ENCRYPTION)
    test.set_handler_type((OnuActivateHandler, UniSetHandler, TcontCreateHandler, GemPortCreateHandler))
    test.parse_arguments()
    return test.run(extra_args=(
        (True,),
        (test.args.uni_name, test.args.uni_id),
        (test.args.tcont_name, test.args.alloc_id),
        (test.args.gemport_name, test.args.uni_name, test.args.tcont_name, test.args.gemport_id,
         test.args.tc, test.args.direction, test.args.encryption)))

if __name__ == "__main__":
    sys.exit(main())
