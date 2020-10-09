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
# ONU activation test. Invokes onu_activate.py handler
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

""" Execute an OnuActivateHandler.
    invoke with -h, --help for command-line parameters help
"""
import sys
from bin.test_utils import TestOmhDriver
from omci_logger import OmciLogger
from omh_nbi.handlers.onu_activate import OnuActivateHandler
logger = OmciLogger.getLogger(__name__)

def main(argv=None) -> int:
    test = TestOmhDriver(name='ACTIVATE_ONU', any_handler=False)
    test.parser.add_argument('-r', '--force-reset', type=bool, default=False,
        help='Force ONU reset and re-sync: %r' % False)
    test.set_handler_type(OnuActivateHandler)
    test.parse_arguments()
    return test.run(extra_args=(test.args.force_reset,))

if __name__ == "__main__":
    sys.exit(main())
