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
from testing_framework.docker_api import *



class RestartTestCase(unittest.TestCase):

    def tearDown(self):
        stop_dockers_if_test_fails(self)

    def test_restart_vomci3_telemetry_subscriptions_restore(self):
        # Add a new subscription for ONU5
        expected_subscription_id = '3'
        get_and_clear_vomci_telemetry(OnuInfo.ONU5['vomci']['name'])
        expected_response = read_eval_file("yang_data/telemetry/subscription_response.yang",
            {"ONU_NAME": OnuInfo.ONU5['name'], "SUBSCRIPTION_ID": expected_subscription_id}) 
        self.assertTrue(create_telemetry_subscription(OnuInfo.ONU5, expected_response))
        self.assertTrue(RestartTestCase.has_one_telemetry_subscription(OnuInfo.ONU5, expected_subscription_id))

        restart_docker("obbaa-vomci3")

        onu_configuration = read_configuration_file('yang_data/configurations/basic_configuration.json')
        self.assertTrue(set_onu_communication_to_vomci_no_proxy(OnuInfo.ONU5))
        self.assertTrue(send_initial_config(OnuInfo.ONU5, onu_configuration))
        # Check that the subscription made before restart is restored
        time.sleep(10)
        self.assertTrue(RestartTestCase.has_one_telemetry_subscription(OnuInfo.ONU5, expected_subscription_id))

    def has_one_telemetry_subscription(onu, expected_subscription_id):
        expected_get_response = make_get_resp_file("yang_data/telemetry/get_subscriptions_response_1.json",
            {"ONU_NAME": onu['name'], "SUBSCRIPTION_ID": expected_subscription_id})
        get_request = read_configuration_file("yang_data/telemetry/get_subscriptions.json",
            {"ONU_NAME": onu['name']})
        get_response = voltmf_send_get_vomci_data_request(get_request, onu['vomci']['name'])
        if get_response is None:
            return False
        return yangs_are_similar(get_response, expected_get_response)

if __name__ == '__main__':
    unittest.main()
