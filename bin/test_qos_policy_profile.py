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
# qos_policy_profile_set.py OMH handler test
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

""" Execute an OnuActivateHandler followed by UniSetHandler, TcontCreateHandler,
    GemPortCreateHandler and QosPolicyProfileSetHandler
    invoke with -h, --help for command-line parameters help
"""
""" Execute an OnuActivateHandler.
    invoke with -h, --help for command-line parameters help
"""
import sys
from bin.test_utils import TestOmhDriver
from omci_logger import OmciLogger
from omh_nbi.handlers.uni_set import UniSetHandler
from omh_nbi.handlers.onu_activate import OnuActivateHandler
from omh_nbi.handlers.tcont_create import TcontCreateHandler
from omh_nbi.handlers.gem_port_create import GemPortCreateHandler
from omh_nbi.handlers.qos_policy_profile_set import QosPolicyProfile, QosPolicyProfileSetHandler
logger = OmciLogger.getLogger(__name__)

DEFAULT_PROFILE_NAME = 'qos_profile.1'
DEFAULT_UNI_NAME = 'uni.1'
DEFAULT_UNI_ID = 0
DEFAULT_TCONT_NAME = 'tcont'
DEFAULT_ALLOC_ID = 1024
DEFAULT_GEM_PORT_NAME = 'gem'
DEFAULT_GEM_PORT_ID = 1025
DEFAULT_NUM_PBITS_PER_TC = 2
DEFAULT_NUM_TCS = 2
DEFAULT_DIRECTION = 'BIDIRECTIONAL'
DEFAULT_ENCRYPTION = 'NO_ENCRYPTION'

def main(argv=None) -> int:
    test = TestOmhDriver(name='QOS_POLICY_PROFILE', any_handler=False)
    test.parser.add_argument('--profile-name', type=str, default=DEFAULT_PROFILE_NAME,
        help='QoS policy profile name: %r' % DEFAULT_PROFILE_NAME)
    test.parser.add_argument('--uni-name', type=str, default=DEFAULT_UNI_NAME,
        help='UNI name: %r' % DEFAULT_UNI_NAME)
    test.parser.add_argument('--uni-id', type=int, default=DEFAULT_UNI_ID,
        help='UNI id: %r' % DEFAULT_UNI_ID)
    test.parser.add_argument('--tcont-name', type=str, default=DEFAULT_TCONT_NAME,
        help='TCONT base name: %r' % DEFAULT_TCONT_NAME)
    test.parser.add_argument('--alloc-id', type=int, default=DEFAULT_ALLOC_ID,
        help='Base ALLOC Id: %r' % DEFAULT_ALLOC_ID)
    test.parser.add_argument('--gemport-name', type=str, default=DEFAULT_GEM_PORT_NAME,
        help='GEM port base name: %r' % DEFAULT_GEM_PORT_NAME)
    test.parser.add_argument('--gemport-id', type=int, default=DEFAULT_GEM_PORT_ID,
        help='GEMPORT Id: %r' % DEFAULT_GEM_PORT_ID)
    test.parser.add_argument('--num_pbits_per_tc', type=int, default=DEFAULT_NUM_PBITS_PER_TC,
        help='Number of PBIts that map to the same Traffic Class: %r' % DEFAULT_NUM_PBITS_PER_TC)
    test.parser.add_argument('--num_tcs', type=int, default=DEFAULT_NUM_TCS,
        help='Number of Traffic Classes: %r' % DEFAULT_NUM_TCS)
    test.parser.add_argument('--encryption', type=str, default=DEFAULT_ENCRYPTION,
        help='GEM port encryption: %r' % DEFAULT_ENCRYPTION)
    test.parse_arguments()
    if test.args.num_tcs * test.args.num_pbits_per_tc > 8:
        print("num-tcs * num-pbits-per-tc must be <= 8")
        return -1

    handler_types = [OnuActivateHandler, UniSetHandler]
    handler_extra_args = [(True,), (test.args.uni_name, test.args.uni_id)]

    # Create as many TCONts and GEMs as there are TCs
    for tc in range(test.args.num_tcs):
        tcont_name = test.args.tcont_name + '.' + str(tc)
        gemport_name = test.args.gemport_name + '.' + str(tc)
        alloc_id = test.args.alloc_id + tc
        gemport_id = test.args.gemport_id + tc
        handler_types += (TcontCreateHandler, GemPortCreateHandler)
        handler_extra_args += (
            (tcont_name, alloc_id),
            (gemport_name, test.args.uni_name, tcont_name, gemport_id,
             tc, DEFAULT_DIRECTION, test.args.encryption))

    # Create pbit_to_tc mapper
    qos_profile = QosPolicyProfile(test.args.profile_name)
    pbit = 0
    for tc in range(test.args.num_tcs):
        for p in range(test.args.num_pbits_per_tc):
            qos_profile.tc_set(pbit+p, tc)
        pbit += test.args.num_pbits_per_tc

    # Finally add QosPolicyProfileHandler
    handler_types.append(QosPolicyProfileSetHandler)
    handler_extra_args.append((qos_profile, test.args.uni_name))

    # Run the sequnece
    test.set_handler_type(tuple(handler_types))
    return test.run(tuple(handler_extra_args))

if __name__ == "__main__":
    sys.exit(main())
