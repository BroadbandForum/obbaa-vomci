# Copyright 2023 Broadband Forum
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
from testing_framework.docker_api import stop_dockers_if_test_fails


class TelemetryTestCase(unittest.TestCase):

    def tearDown(self):
        stop_dockers_if_test_fails(self)

    def test_create_subscription(self):
        # No initial subscription
        self.assertTrue(TelemetryTestCase.has_no_telemetry_subscription(OnuInfo.ONU5))

        # Add a new subscription for ONU5
        expected_subscription_id = '1'
        get_and_clear_vomci_telemetry(OnuInfo.ONU5['vomci']['name'])
        expected_response = read_eval_file("yang_data/telemetry/subscription_response.yang",
            {"ONU_NAME": OnuInfo.ONU5['name'], "SUBSCRIPTION_ID": expected_subscription_id}) 
        self.assertTrue(create_telemetry_subscription(OnuInfo.ONU5, expected_response))

        # Check that the new subscription is created
        self.assertTrue(TelemetryTestCase.has_one_telemetry_subscription(OnuInfo.ONU5, expected_subscription_id))

        # Check that new subscription generates telemetry notifications
        time.sleep(2)
        self.assertTrue(check_telemetry_notification(OnuInfo.ONU5, expected_subscription_id))

        # Wait and check that the subscription generates more telemetry notifications
        time.sleep(10)
        self.assertTrue(check_telemetry_notification(OnuInfo.ONU5, expected_subscription_id))
        
        # Remove subscription from ONU5
        self.assertTrue(remove_telemetry_subscription(OnuInfo.ONU5, expected_subscription_id))
        self.assertTrue(TelemetryTestCase.has_no_telemetry_subscription(OnuInfo.ONU5))

        # Check that the removed subscription does not generates any telemetry notification
        get_and_clear_vomci_telemetry(OnuInfo.ONU5['vomci']['name'])
        time.sleep(10)
        notifications = get_and_clear_vomci_telemetry(OnuInfo.ONU5['vomci']['name'])
        self.assertEqual(len(notifications), 0)

        # Add a second subscription for ONU5 and delete ONU5
        expected_subscription_id = '2'
        expected_response = read_eval_file("yang_data/telemetry/subscription_response.yang",
            {"ONU_NAME": OnuInfo.ONU5['name'], "SUBSCRIPTION_ID": expected_subscription_id}) 
        self.assertTrue(create_telemetry_subscription(OnuInfo.ONU5, expected_response))
        self.assertTrue(TelemetryTestCase.has_one_telemetry_subscription(OnuInfo.ONU5, expected_subscription_id))
        self.assertTrue(delete_onu(OnuInfo.ONU5))
        self.assertTrue(TelemetryTestCase.has_no_telemetry_subscription(OnuInfo.ONU5))

        # Add a subscription for ONU5 which does not exist
        expected_response = read_eval_file("yang_data/telemetry/subscription_failed_response.yang") 
        self.assertTrue(create_telemetry_subscription(OnuInfo.ONU5, expected_response))

        # Add ONU5
        self.assertTrue(create_onu(OnuInfo.ONU5))
        self.assertTrue(set_onu_communication_to_vomci_no_proxy(OnuInfo.ONU5))
        time.sleep(10)


    def has_no_telemetry_subscription(onu):
        expected_get_response = make_get_resp_file("yang_data/telemetry/get_subscriptions_response_0.json",
            {"ONU_NAME": onu['name']})
        get_request = read_configuration_file("yang_data/telemetry/get_subscriptions.json",
            {"ONU_NAME": onu['name']})
        get_response = voltmf_send_get_vomci_data_request(get_request, onu['vomci']['name'])
        if get_response is None:
            return False
        return yangs_are_similar(get_response, expected_get_response)

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