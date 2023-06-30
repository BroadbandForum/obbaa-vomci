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

import os
import time
import logging
import subprocess

logger = logging.getLogger('voltmf-simu')
logging.basicConfig(level=logging.INFO, format='%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def stop_dockers():
    logger.info('\n Stopping Dockers ...')
    cmd = 'docker-compose -f ./testing_framework/data/compose_data/docker-compose.yaml down'
    result = subprocess.run(cmd, shell=True, timeout= 60, capture_output=True, text=True)
    time.sleep(20)    
    logger.info(result.stderr)

def start_dockers():
    stop_dockers()
    logger.info('\n Starting Dockers ...')
    cmd = 'docker-compose -f ./testing_framework/data/compose_data/docker-compose.yaml up -d'
    result = subprocess.run(cmd, shell=True, timeout= 60, capture_output=True, text=True)
    time.sleep(90)
    logger.info(result.stderr)

def detect_onus():
    logger.info('\n Connecting OLT and ONU simulators ...')
    cmd = 'exec ./testing_framework/data/compose_data/init_olt_sim1.sh &'
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, text=True)
    cmd = 'exec ./testing_framework/data/compose_data/init_olt_sim2.sh &'
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, text=True)
    cmd = 'exec ./testing_framework/data/compose_data/init_olt_sim3.sh &'
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, text=True)
    cmd = 'exec ./testing_framework/data/compose_data/init_olt_sim4.sh &'
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, text=True)   
    time.sleep(90)
    p.kill()

def restart_docker(docker_name):
    os.system("docker restart " + docker_name)
    time.sleep(10)

def show_logs(docker_name):
    logger.info('\n\n\n Logs of %s ######################################### \n\n\n', docker_name)
    os.system("docker logs " + docker_name)
    logger.info('\n End of logs of %s ######################################### \n', docker_name)

def stop_dockers_if_test_fails(testcase):
        result = testcase.defaultTestResult()
        testcase._feedErrorsToResult(result, testcase._outcome.errors)
        ok = all(test != testcase for test, text in result.errors + result.failures)
        if not ok:
            logger.error('\n Faild test case name: %s', testcase._testMethodName)
            # show_logs("obbaa-vomci")
            # show_logs("obbaa-vomci2")
            # show_logs("obbaa-vomci3")
            # show_logs("obbaa-vproxy")            
            # show_logs("kafka-gpb-tester")
            # show_logs("onu-simulator")            
            stop_dockers()