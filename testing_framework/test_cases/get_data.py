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
from testing_framework.voltmf_api import *
from testing_framework.onu_api import *
from testing_framework.docker_api import stop_dockers_if_test_fails

class GetDataTestCase(unittest.TestCase):

    def setUpClass():
        GetDataTestCase.onu_set_pm_counters(OnuInfo.ONU5, 1)

    def tearDown(self):
        stop_dockers_if_test_fails(self)

    def test_get_hw_state(self):
        self.assertTrue(GetDataTestCase.onu_update_sw_version(OnuInfo.ONU5, 'SW_VERSION_1'))
        expected_get_response = "yang_data/get_data/get_hw_response1.json"
        get_request = read_configuration_file("yang_data/get_data/get_hw.json")
        self.assertTrue(voltmf_send_get_onu_data_request_check_response(get_request, expected_get_response, OnuInfo.ONU5))

        self.assertTrue(GetDataTestCase.onu_update_sw_version(OnuInfo.ONU5, 'SW_VERSION_2'))
        expected_get_response = "yang_data/get_data/get_hw_response2.json"
        self.assertTrue(voltmf_send_get_onu_data_request_check_response(get_request, expected_get_response, OnuInfo.ONU5))

    def test_get_if_state(self):
        self.assertTrue(GetDataTestCase.onu_disable_oper_state_of_uni(OnuInfo.ONU5, 2))
        get_request = read_configuration_file("yang_data/get_data/get_if.json")
        expected_get_response = make_get_resp_file("yang_data/get_data/get_if_response1.json")
        get_response = voltmf_send_get_onu_data_request(get_request, OnuInfo.ONU5)
        self.assertIsNotNone(get_response)
        ok = yangs_are_similar(remove_yang_attribute(get_response, 'time-stamp'),
                             remove_yang_attribute(expected_get_response, 'time-stamp'))
        self.assertTrue(ok)

        self.assertTrue(GetDataTestCase.onu_enable_oper_state_of_uni(OnuInfo.ONU5, 2))
        expected_get_response = make_get_resp_file("yang_data/get_data/get_if_response2.json")
        get_response = voltmf_send_get_onu_data_request(get_request, OnuInfo.ONU5)
        self.assertIsNotNone(get_response)
        ok = yangs_are_similar(remove_yang_attribute(get_response, 'time-stamp'),
                               remove_yang_attribute(expected_get_response, 'time-stamp'))
        self.assertTrue(ok)

    def test_get_if_hw_state(self):
        self.assertTrue(GetDataTestCase.onu_enable_oper_state_of_uni(OnuInfo.ONU5, 2))
        get_request = read_configuration_file("yang_data/get_data/get_if_hw.json")
        expected_get_response = make_get_resp_file("yang_data/get_data/get_if_hw_response.json")
        get_response = voltmf_send_get_onu_data_request(get_request, OnuInfo.ONU5)
        self.assertIsNotNone(get_response)
        ok = yangs_are_similar(remove_yang_attribute(get_response, 'time-stamp'),
                               remove_yang_attribute(expected_get_response, 'time-stamp'))
        self.assertTrue(ok)

    def onu_update_sw_version(onu, sw_version):
        _, status = onu_send_action(int(onu['id']), OMCI.SET, OMCI.SW_IMAGE_ME_ID, 0, {1:sw_version})
        return status == 0

    def onu_disable_oper_state_of_uni(onu, instance_id):
        _, status = onu_send_action(int(onu['id']), OMCI.SET, OMCI.PPTP_ETH_UNI_ME_ID, instance_id, {6:'disabled'})
        return status == 0

    def onu_enable_oper_state_of_uni(onu, instance_id):
        _, status = onu_send_action(int(onu['id']), OMCI.SET, OMCI.PPTP_ETH_UNI_ME_ID, instance_id, {6:'enabled'})
        return status == 0

    def onu_set_pm_counters(onu, instance_id):
        _, status = onu_send_action(int(onu['id']), OMCI.SET, OMCI.ETH_FRAME_DOWNSTREAM_PM, instance_id, {4:10, 6:11, 7:12})
        _, status = onu_send_action(int(onu['id']), OMCI.SET, OMCI.ETH_FRAME_UPSTREAM_PM, instance_id, {4:20, 6:21, 7:22})
        return status == 0


if __name__ == '__main__':
    unittest.main()