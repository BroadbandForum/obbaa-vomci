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
# Created by Jafar Hamin (Nokia) in August 2022

import logging
import threading
from sanic import Sanic
from sanic.response import json
import voltfm_simulator

app = Sanic("voltmf-simu")
logging.basicConfig(level=logging.INFO, format='%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger('voltmf-simu')

@app.route('/send_yang_request', methods=["POST"])
def send_yang_request(request):
    result = voltfm_simulator.send_yang_request(request.json)      
    return json({'result': str(result)})

@app.route('/get_vnf_response', methods=["POST"])
def get_vnf_response(request):
    result = voltfm_simulator.get_vnf_response(str(request.json['msg_id']), request.json['vnf_name'])      
    return json({'result': str(result)})

@app.route('/get_and_clear_vnf_notifications', methods=["POST"])
def get_and_clear_vnf_notifications(request):
    result = voltfm_simulator.get_and_clear_vnf_notifications(request.json['vnf_name'])
    return json({'result': result})

@app.route('/get_and_clear_vnf_telemetry', methods=["POST"])
def get_and_clear_vnf_telemetry(request):
    result = voltfm_simulator.get_and_clear_vnf_telemetry(request.json['vnf_name'])
    return json({'result': result})

def main():
    logger.setLevel(logging.INFO)
    omci_tread = threading.Thread(target=voltfm_simulator.consume_loop,name="consume_loop")
    omci_tread.start()
    logger.info('HTTP Server starts listening to port 3001')
    app.run(host="0.0.0.0", port=3001)

if __name__ == '__main__':
    main()

