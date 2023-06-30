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
from testing_framework.onu_api import *
from testing_framework.docker_api import stop_dockers_if_test_fails


class UniConifgTestCase(unittest.TestCase):

    def tearDown(self):
        stop_dockers_if_test_fails(self)

    def test_configure_uni(self):
        self.assertTrue(onu_me_instance_not_exists(int(OnuInfo.ONU5['id']), OMCI.MAC_BRIDGE_PORT_CONFIG_DATA_ME_ID, 3))
        self.assertTrue(onu_me_instance_not_exists(int(OnuInfo.ONU5['id']), OMCI.EVTOCD_ME_ID, 2))
        voltmf_send_update_config_inst_to_vomci("yang_data/configurations/add_uni_if.json",
                                       "yang_data/configurations/basic_configuration.json",
                                       onu=OnuInfo.ONU5)
        self.assertTrue(onu_get_compare_me_attributes(int(OnuInfo.ONU5['id']), OMCI.MAC_BRIDGE_PORT_CONFIG_DATA_ME_ID, 3, {1:1, 2:3, 3:1, 4:2}))
        self.assertTrue(onu_get_compare_me_attributes(int(OnuInfo.ONU5['id']), OMCI.EVTOCD_ME_ID, 2, {1:2, 3:33024, 4:33024, 5:0}))


if __name__ == '__main__':
    unittest.main()