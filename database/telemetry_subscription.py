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
# Created by Jafar Hamin (Nokia) in Fubruady 2023

"""
This module handles subscriptions made for receiving ONU telemetry data
"""

import threading
import time
import json
import threading
import unittest

class Subscription:

    _periodicSubscriptions = {}     # type: dict[interval, _PeriodicSubscription]
    _threads = {}                   # type: dict[interval, threading.Timer]
    _subscription_id = 0            # unique ID generated for each subscription
    _push_call_back = None          # callback function invoked when interval expires
    _lock = threading.Lock()        # protect data from concurrent accesses

    @classmethod
    def export_subscriptions(cls):
        return cls.get_json_subscriptions()

    @classmethod
    def import_subscriptions(cls, exported_subscriptions):
        exported_subscriptions = json.loads(exported_subscriptions)
        if ('bbf-vomci-function:vomci' not in exported_subscriptions or
            'managed-onus' not in exported_subscriptions['bbf-vomci-function:vomci'] or
            'managed-onu' not in exported_subscriptions['bbf-vomci-function:vomci']['managed-onus']):
            return
        for onu_subscription in exported_subscriptions['bbf-vomci-function:vomci']['managed-onus']['managed-onu']:
            onu_name = onu_subscription['name']
            for subscriptions in onu_subscription['bbf-obbaa-vomci-telemetry:established_subscriptions']:
                subscription_id = subscriptions['subscription-id']
                updates = {'updates': subscriptions['updates']}
                cls.add_json_subscription(updates, onu_name, subscription_id)

    @classmethod
    def set_push_call_back(cls, push_call_back):
        cls._push_call_back = push_call_back

    @classmethod
    def add_json_subscription(cls, subscription, onu, subscription_id=None):
        with cls._lock:
            subscription_id = cls.__generate_new_subscription_id(subscription_id)
            for update in subscription['updates']:
                for xpath in update['xpaths']:
                    cls.__add_subscription(onu, subscription_id, update['name'], xpath, update['interval'])
        return subscription_id

    @classmethod
    def remove_subscription(cls, subscription_id, onu):
        with cls._lock:
            for interval in cls._periodicSubscriptions.copy():
                ps = cls._periodicSubscriptions[interval]
                ps.remove_subscription(subscription_id, onu)
                if ps.has_no_subscription():
                    cls._periodicSubscriptions.pop(interval)
                    cls._threads[interval].cancel()

    @classmethod
    def remove_all_subscriptions(cls, onu):
        with cls._lock:
            subscription_ids = cls.__get_subscriptions_ids(onu)
        for subscription_id in subscription_ids:
            cls.remove_subscription(subscription_id, onu)

    @classmethod
    def get_json_subscriptions(cls, onu=None):
        with cls._lock:
            subscriptions = cls.__get_subscriptions(onu)
        result = []
        for onu in subscriptions:
            onu_node = {'name': onu, 'bbf-obbaa-vomci-telemetry:established_subscriptions': []}
            for subscription in subscriptions[onu]:
                subscription_node = {'subscription-id': subscription, 'updates': []}
                for update in subscriptions[onu][subscription]:
                    update_value = subscriptions[onu][subscription][update]
                    update_node = {'name': update, 'xpaths': update_value['xpaths'], 
                                   'interval': update_value['interval']}
                    subscription_node['updates'].append(update_node)
                onu_node['bbf-obbaa-vomci-telemetry:established_subscriptions'].append(subscription_node)
            result.append(onu_node)
        if onu is not None and len(result) == 0:
            result.append({'name': onu, 'bbf-obbaa-vomci-telemetry:established_subscriptions': []})
        result = {'bbf-vomci-function:vomci': {'managed-onus': {'managed-onu': result}}}
        return json.dumps(result)

    @classmethod
    def __add_subscription(cls, onu, subscription_id, update_name, xpath, interval):
        ps = cls.__get_periodic_subscription(interval)
        if ps is None:
            first_interval = True
        else:
            first_interval = False
        ps = cls.__add_periodic_subscription(interval)
        ps.add_subscription(onu, subscription_id, update_name, xpath)
        if first_interval:
            cls.__push_periodically(ps, interval)


    @classmethod
    def __get_periodic_subscription(cls, interval):
        if interval in cls._periodicSubscriptions:
            return cls._periodicSubscriptions[interval]
        return None

    @classmethod
    def __add_periodic_subscription(cls, interval):
        ps = cls.__get_periodic_subscription(interval)
        if ps is None:
            ps = _PeriodicSubscription()
            cls._periodicSubscriptions[interval] = ps
        return ps

    @classmethod
    def __push_periodically(cls, ps, interval):
        cls.__push_updates(ps)
        cls._threads[interval] = threading.Timer(interval, cls.__push_periodically, [ps, interval])
        cls._threads[interval].start()

    @classmethod
    def __push_updates(cls, ps):
        subscriptions = ps.get_subscriptions()
        for onu in subscriptions:
            for subscription in subscriptions[onu]:
                xpaths = []
                for update in subscriptions[onu][subscription]:
                    xpaths = xpaths + subscriptions[onu][subscription][update]['xpaths']
                cls._push_call_back(onu, subscription, xpaths) 

    @classmethod
    def __generate_new_subscription_id(cls, subscription_id=None):
        if subscription_id is None:
            cls._subscription_id += 1
        else:
            cls._subscription_id = subscription_id
        return cls._subscription_id

    @classmethod
    def __get_subscriptions(cls, onu):
        subscriptions = {}
        for interval, ps in cls._periodicSubscriptions.items():
            s = ps.get_subscriptions(onu)
            Subscription.__add_interval(s, interval)
            DicUtil.merge_dic(subscriptions, s)
        return subscriptions

    @classmethod
    def __get_subscriptions_ids(cls, onu):
        subscriptions = cls.__get_subscriptions(onu)
        if onu not in subscriptions:
            return []
        return list(subscriptions[onu].keys())
    
    @staticmethod
    def __add_interval(subscriptions, interval):
        for onu in subscriptions:
            for subscription in subscriptions[onu]:
                for update in subscriptions[onu][subscription]:
                    DicUtil.add_to_dic(subscriptions[onu][subscription][update], 'interval', interval)


class _PeriodicSubscription:

    def __init__(self):
        self._xpathSubscriptions = {}       # type: dict[xpath, _XpathSubscription]

    def __get_xpath_subscription(self, xpath):
        if xpath in self._xpathSubscriptions:
            return self._xpathSubscriptions[xpath]
        return None

    def __add_xpath_subscription(self, xpath):
        xs = self.__get_xpath_subscription(xpath)
        if xs is None:
            xs = _XpathSubscription()
            self._xpathSubscriptions[xpath] = xs
        return xs

    def has_no_subscription(self):
        return len(self._xpathSubscriptions) == 0
        
    def add_subscription(self, onu, subscription_id, update_name, xpath):
        xs = self.__add_xpath_subscription(xpath)
        xs.add_subscription(onu, subscription_id, update_name)

    def remove_subscription(self, subscription_id, onu):
        for xpath in self._xpathSubscriptions.copy():
            xs = self._xpathSubscriptions[xpath]
            xs.remove_subscription(subscription_id, onu)
            if xs.has_no_subscription():
                self._xpathSubscriptions.pop(xpath)

    def get_subscriptions(self, onu=None):
        subscriptions = {}
        for xpath, xs in self._xpathSubscriptions.items():
            s = xs.get_subscriptions(onu)
            _PeriodicSubscription.__add_xpath(s, xpath)
            DicUtil.merge_dic(subscriptions, s)
        return subscriptions

    @staticmethod
    def __add_xpath(subscriptions, xpath):
        for onu in subscriptions:
            for subscription in subscriptions[onu]:
                for update in subscriptions[onu][subscription]:
                    DicUtil.add_to_dic(subscriptions[onu][subscription][update], 'xpaths', [xpath])

 
class _XpathSubscription:

    def __init__(self):
        self._onuSubscriptions = []     # type: list[_OnuSubscription]

    def __get_onu_subscription(self, onu, subscription_id, update_name):
        for os in self._onuSubscriptions:
            if os.equal(onu, subscription_id, update_name):
                return os
        return None

    def __add_onu_subscription(self, onu, subscription_id, update_name):
        os = self.__get_onu_subscription(onu, subscription_id, update_name)
        if os is None:
            os = _OnuSubscription(onu, subscription_id, update_name)
            self._onuSubscriptions.append(os)
        return os

    def has_no_subscription(self):
        return len(self._onuSubscriptions) == 0

    def add_subscription(self, onu, subscription_id, update_name):
        os = self.__add_onu_subscription(onu, subscription_id, update_name)
        self._onuSubscriptions.append(os)

    def remove_subscription(self, subscription_id, onu):
        newOnuSubscriptions =[]
        for os in self._onuSubscriptions:
            if os.get_subscription_id() != subscription_id or os.get_onu() != onu:
                newOnuSubscriptions.append(os)
        self._onuSubscriptions = newOnuSubscriptions

    def get_subscriptions(self, onu):
        subscriptions = {}
        for os in self._onuSubscriptions:
            if onu is not None and onu != os.get_onu():
                continue
            s = os.get_subscription()
            DicUtil.merge_dic(subscriptions, s)            
        return subscriptions 


class _OnuSubscription:

    def __init__(self, onu, subscription_id, update_name):
        self._onu = onu
        self._subscription_id = subscription_id
        self._update_name = update_name

    def get_subscription_id(self):
        return self._subscription_id

    def get_onu(self):
        return self._onu

    def equal(self, onu, subscription_id, update_name):
        return (self._onu == onu and
                self._subscription_id == subscription_id and
                self._update_name == update_name)
    
    def get_subscription(self):
        return {self._onu: {self._subscription_id: {self._update_name: {}}}}


class DicUtil:

    @staticmethod
    def add_to_dic(dic, node, value):
        if node not in dic:
            dic[node] = value
        return dic[node]

    @staticmethod
    def merge_dic(dic1, dic2):
        for node in dic2:
            if node not in dic1:
                dic1[node] = dic2[node]
            else:
                if isinstance(dic1[node], dict) and isinstance(dic2[node], dict):
                    DicUtil.merge_dic(dic1[node], dic2[node])
                else:
                    dic1[node] = dic1[node] + dic2[node]


class SubscriptionTestCase(unittest.TestCase):

    def test_subscriptions(self):
        Subscription.set_push_call_back(SubscriptionTestCase.push_call_back_test)

        # Add new subscription for ONU1
        sid1 = Subscription.add_json_subscription(SubscriptionTestCase.subscription1, 'ONU1')
        self.assertEqual(sid1, 1)
        subscriptions = Subscription.get_json_subscriptions('ONU1')
        self.assertTrue(SubscriptionTestCase.similar(SubscriptionTestCase.expected_onu1_subscriptions_1, subscriptions))

        # Add second subscription for ONU1
        sid2 = Subscription.add_json_subscription(SubscriptionTestCase.subscription2, 'ONU1')
        self.assertEqual(sid2, 2)
        subscriptions = Subscription.get_json_subscriptions('ONU1')
        self.assertTrue(SubscriptionTestCase.similar(SubscriptionTestCase.expected_onu1_subscriptions_2, subscriptions))


        # Still no subscription for ONU2
        subscriptions = Subscription.get_json_subscriptions('ONU2')
        self.assertTrue(SubscriptionTestCase.similar(SubscriptionTestCase.expected_onu2_subscriptions_1, subscriptions))

        # Trying to remove a wrong subscription does not remove it
        Subscription.remove_subscription(3, 'ONU1')
        subscriptions = Subscription.get_json_subscriptions('ONU1')
        self.assertTrue(SubscriptionTestCase.similar(SubscriptionTestCase.expected_onu1_subscriptions_2, subscriptions))

        # Trying to remove a wrong subscription does not remove it
        Subscription.remove_subscription(2, 'ONU2')
        subscriptions = Subscription.get_json_subscriptions('ONU1')
        self.assertTrue(SubscriptionTestCase.similar(SubscriptionTestCase.expected_onu1_subscriptions_2, subscriptions))

        # Remove second subscription from ONU1 
        Subscription.remove_subscription(2, 'ONU1')
        subscriptions = Subscription.get_json_subscriptions('ONU1')
        self.assertTrue(SubscriptionTestCase.similar(SubscriptionTestCase.expected_onu1_subscriptions_1, subscriptions))

        # Add new subscription for ONU2 
        sid3 = Subscription.add_json_subscription(SubscriptionTestCase.subscription2, 'ONU2')
        self.assertEqual(sid3, 3)
        subscriptions = Subscription.get_json_subscriptions('ONU2')
        self.assertTrue(SubscriptionTestCase.similar(SubscriptionTestCase.expected_onu2_subscriptions_2, subscriptions))

        # Subscriptions of ONU1 are untouched 
        subscriptions = Subscription.get_json_subscriptions('ONU1')
        self.assertTrue(SubscriptionTestCase.similar(SubscriptionTestCase.expected_onu1_subscriptions_1, subscriptions))

        # Remove subscription of ONU2 
        Subscription.remove_subscription(3, 'ONU2')
        subscriptions = Subscription.get_json_subscriptions('ONU2')
        self.assertTrue(SubscriptionTestCase.similar(SubscriptionTestCase.expected_onu2_subscriptions_1, subscriptions))

        # Subscriptions of ONU1 are untouched 
        subscriptions = Subscription.get_json_subscriptions('ONU1')
        self.assertTrue(SubscriptionTestCase.similar(SubscriptionTestCase.expected_onu1_subscriptions_1, subscriptions))

        Subscription.remove_subscription(1, 'ONU1')

        # Test subscription notifications:
        Subscription.set_push_call_back(SubscriptionTestCase.push_call_back_test_with_counter)
        Subscription.add_json_subscription(SubscriptionTestCase.subscription1, 'ONU1')
        Subscription.add_json_subscription(SubscriptionTestCase.subscription2, 'ONU1')
        Subscription.add_json_subscription(SubscriptionTestCase.subscription2, 'ONU2')
        time.sleep(11)
        Subscription.remove_subscription(4, 'ONU1')
        Subscription.remove_subscription(5, 'ONU1')
        Subscription.remove_subscription(6, 'ONU2')
        print(SubscriptionTestCase.pushes)
        for subscription in SubscriptionTestCase.pushes:
            for xpath in SubscriptionTestCase.pushes[subscription]:
                pushes = SubscriptionTestCase.pushes[subscription][xpath]
                expected_min_pushes = SubscriptionTestCase.expected_minimum_pushes[subscription][xpath]
                self.assertGreaterEqual(pushes, expected_min_pushes)

        # Test subscriptions export and import:
        Subscription.set_push_call_back(SubscriptionTestCase.push_call_back_test)
        Subscription.add_json_subscription(SubscriptionTestCase.subscription1, 'ONU1')
        Subscription.add_json_subscription(SubscriptionTestCase.subscription2, 'ONU1')
        Subscription.add_json_subscription(SubscriptionTestCase.subscription2, 'ONU2')
        exported_subscriptions = Subscription.export_subscriptions()
        self.assertTrue(SubscriptionTestCase.similar(
            SubscriptionTestCase.expected_exported_subscriptions, exported_subscriptions))

        # Remove subscriptions and export subscriptions
        Subscription.remove_subscription(7, 'ONU1')
        Subscription.remove_subscription(8, 'ONU1')
        Subscription.remove_subscription(9, 'ONU2')
        no_subscription = Subscription.export_subscriptions()
        self.assertTrue(SubscriptionTestCase.similar(
            SubscriptionTestCase.no_subscription, no_subscription))

        # Import the subscriptions which was already exported
        Subscription.import_subscriptions(exported_subscriptions)
        new_subscriptions = Subscription.export_subscriptions()
        self.assertTrue(SubscriptionTestCase.similar(
            SubscriptionTestCase.expected_exported_subscriptions, new_subscriptions))
        
        Subscription.remove_all_subscriptions('ONU2')
        subscriptions = Subscription.get_json_subscriptions('ONU2')
        self.assertTrue(SubscriptionTestCase.similar(SubscriptionTestCase.expected_onu2_subscriptions_1, subscriptions))
        Subscription.remove_all_subscriptions('ONU1')

    def similar(str1, str2):
        return str1.replace(' ', '').replace('\n', '') == str2.replace(' ', '').replace('\n', '')

    def push_call_back_test(onu, subscription, xpaths):
        print('Test function for pushing telemetry for subscription %s ONU %s XPaths %s'
                %(subscription, onu, xpaths))

    def push_call_back_test_with_counter(onu, subscription, xpaths):
        SubscriptionTestCase.push_call_back_test(onu, subscription, xpaths)
        for xpath in xpaths:
            SubscriptionTestCase.pushes[str(subscription)][xpath] += 1

    pushes = {
            '4': 
                {
                    'xpath1': 0,
                    'xpath2': 0,
                    'xpath3': 0
                },
            '5':
                {
                    'xpath1': 0,
                    'xpath2': 0,
                    'xpath3': 0,
                    'xpath4': 0                        
                },
            '6': 
                {
                    'xpath1': 0,
                    'xpath2': 0,
                    'xpath3': 0,
                    'xpath4': 0
                }
            }

    expected_minimum_pushes = {
            '4': 
                {
                    'xpath1': 7,
                    'xpath2': 4,
                    'xpath3': 2
                },
            '5':
                {
                    'xpath1': 3,
                    'xpath2': 3,
                    'xpath3': 2,
                    'xpath4': 2                        
                },
            '6': 
                {
                    'xpath1': 3,
                    'xpath2': 3,
                    'xpath3': 2,
                    'xpath4': 2
                }
            }

    subscription1 = {
        'updates': [
            {
                'name':'pm1',
                'xpaths':['xpath1', 'xpath2'],
                'interval': 2
            },
            {
                'name':'pm2',
                'xpaths':['xpath1', 'xpath3'],
                'interval': 3
            }
        ]
    }

    subscription2 = {
        'updates': [
            {
                'name':'pm1',
                'xpaths':['xpath1', 'xpath2'],
                'interval': 3
            },
            {
                'name':'pm2',
                'xpaths':['xpath3', 'xpath4'],
                'interval': 4
            }
        ]
    }

    expected_onu1_subscriptions_1 = json.dumps({
        "bbf-vomci-function:vomci":{
            "managed-onus":{
                "managed-onu":[
                    {
                    "name":"ONU1",
                    "bbf-obbaa-vomci-telemetry:established_subscriptions":[
                        {
                            "subscription-id":1,
                            "updates": subscription1['updates']
                        }
                    ]
                    }
                ]
            }
        }
    })        

    expected_onu1_subscriptions_2 = json.dumps({
        "bbf-vomci-function:vomci":{
            "managed-onus":{
                "managed-onu":[
                    {
                        "name":"ONU1",
                        "bbf-obbaa-vomci-telemetry:established_subscriptions":[
                        {
                            "subscription-id": 1,
                            "updates":subscription1['updates']
                        },
                        {
                            "subscription-id": 2,
                            "updates":subscription2['updates']
                        }
                        ]
                    }
                ]
            }
        }
    })


    expected_onu2_subscriptions_1 = json.dumps({
        "bbf-vomci-function:vomci":{
            "managed-onus":{
                "managed-onu":[
                    {
                        "name": "ONU2",
                        "bbf-obbaa-vomci-telemetry:established_subscriptions": []
                    }
                ]
            }
        }
    })

    expected_onu2_subscriptions_2 = json.dumps({
        "bbf-vomci-function:vomci":{
            "managed-onus":{
                "managed-onu":[
                    {
                        "name": "ONU2",
                        "bbf-obbaa-vomci-telemetry:established_subscriptions": [
                            {
                                "subscription-id": 3,
                                "updates": [
                                    {
                                        "name": "pm1",
                                        "xpaths": ["xpath1", "xpath2"],
                                        "interval": 3
                                    }, 
                                    {
                                        "name": "pm2",
                                        "xpaths": ["xpath3", "xpath4"],
                                        "interval": 4
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
    })

    expected_exported_subscriptions = json.dumps({
        "bbf-vomci-function:vomci":{
            "managed-onus":{
                "managed-onu":[
                {
                    "name": "ONU1",
                    "bbf-obbaa-vomci-telemetry:established_subscriptions": [
                        {
                            "subscription-id": 7,
                            "updates": [
                                {
                                    "name": "pm1",
                                    "xpaths": [
                                        "xpath1",
                                        "xpath2"
                                    ],
                                    "interval": 2
                                },
                                {
                                    "name": "pm2",
                                    "xpaths": [
                                        "xpath1",
                                        "xpath3"
                                    ],
                                    "interval": 3
                                }
                            ]
                        },
                        {
                            "subscription-id": 8,
                            "updates": [
                                {
                                    "name": "pm1",
                                    "xpaths": [
                                        "xpath1",
                                        "xpath2"
                                    ],
                                    "interval": 3
                                },
                                {
                                    "name": "pm2",
                                    "xpaths": [
                                        "xpath3",
                                        "xpath4"
                                    ],
                                    "interval": 4
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "ONU2",
                    "bbf-obbaa-vomci-telemetry:established_subscriptions": [
                        {
                            "subscription-id": 9,
                            "updates": [
                                {
                                    "name": "pm1",
                                    "xpaths": [
                                        "xpath1",
                                        "xpath2"
                                    ],
                                    "interval": 3
                                },
                                {
                                    "name": "pm2",
                                    "xpaths": [
                                        "xpath3",
                                        "xpath4"
                                    ],
                                    "interval": 4
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }})

    no_subscription = json.dumps({
        "bbf-vomci-function:vomci":{
            "managed-onus":{
                "managed-onu":[]
            }
        }
    })


if __name__ == '__main__':
    unittest.main()
