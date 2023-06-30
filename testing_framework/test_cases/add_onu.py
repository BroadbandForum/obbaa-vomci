# Copyright 2022 Broadband Forum
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
# Created by Jafar Hamin (Nokia) in August 2023

import unittest
import time
from testing_framework.voltmf_api import *
from testing_framework.docker_api import *

class AddOnuTestCase(unittest.TestCase):

    def setUpClass():
        start_dockers()
        detect_onus()

    def tearDown(self):
        stop_dockers_if_test_fails(self)

    def test_add_onus_through_different_vomci_functions(self):

        onu_configuration = read_configuration_file('yang_data/configurations/basic_configuration.json')

        # Create and configure ONU1 in the first vOMCI function with vOMCI-Proxy
        self.assertTrue(create_onu(OnuInfo.ONU1))
        self.assertTrue(set_onu_communication_to_vproxy(OnuInfo.ONU1))
        self.assertTrue(set_onu_communication_to_vomci_with_proxy(OnuInfo.ONU1))
        time.sleep(20)
        self.assertTrue(check_alignment_notification(OnuInfo.ONU1, 'unaligned'))
        self.assertTrue(send_initial_config(OnuInfo.ONU1, onu_configuration))

        # Add second vOMCI function to the vProxy
        voltmf_send_update_config_replica_to_vproxy(delta_config_path="yang_data/vproxy_requests/add_vomci_endpoint.json")

        # Create and configure ONU3 in the second vOMCI function with vOMCI-Proxy
        self.assertTrue(create_onu(OnuInfo.ONU3))
        self.assertTrue(set_onu_communication_to_vproxy(OnuInfo.ONU3))
        self.assertTrue(set_onu_communication_to_vomci_with_proxy(OnuInfo.ONU3))
        # self.assertTrue(check_alignment_notification(OnuInfo.ONU3, 'unaligned'))
        self.assertTrue(send_initial_config(OnuInfo.ONU3, onu_configuration))

        # Create and configure ONU5 in the third vOMCI function without vOMCI-Proxy
        self.assertTrue(create_onu(OnuInfo.ONU5))
        self.assertTrue(set_onu_communication_to_vomci_no_proxy(OnuInfo.ONU5))
        # self.assertTrue(check_alignment_notification(OnuInfo.ONU5, 'unaligned'))
        self.assertTrue(send_initial_config(OnuInfo.ONU5, onu_configuration))

        # Create and configure ONU7 in the third vOMCI function without vOMCI-Proxy
        self.assertTrue(create_onu(OnuInfo.ONU7))
        self.assertTrue(set_onu_communication_to_vomci_no_proxy(OnuInfo.ONU7))
        # self.assertTrue(check_alignment_notification(OnuInfo.ONU7, 'unaligned'))
        self.assertTrue(send_initial_config(OnuInfo.ONU7, onu_configuration))


if __name__ == '__main__':
    unittest.main()