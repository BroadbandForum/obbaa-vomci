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
# Data types that that are used by multiple OMH handlers.
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

# Data types used in the OMH interface
from typing import Dict, Any
from enum import Enum
from omci_types import AutoGetter

PBIT_VALUE_ANY = -1
VID_VALUE_ANY = -1

class VlanTag(AutoGetter):
    """ VLAN Tag Descriptor """

    def __init__(self, vid: int, pbit: int = PBIT_VALUE_ANY, tpid: int = 0x8100):
        """ VLAN Tag Descriptor

        Args:
            vid
            pbit
            tpid
        """
        self._vid = vid
        self._pbit = pbit
        self._tpid = tpid


class PacketClassifier():
    """ Packet classifier is a dictionary containing field_name: field_value pairs.

    The following field names are supported:
    - o_vid: supported value: VlanTag
    - i_vid: supported value: VlanTag
    - other fields are TBD
    """

    def __init__(self, fields: Dict[str, any]):
        """ Packet classifier.

         Args:
             fields: classification fields dictionary
         """
        self._fields = fields

    def field(self, name: str) -> Any:
        """ Get classification field value, if any """
        if name not in self._fields:
            return None
        return self._fields[name]


class VlanAction(AutoGetter):
    """ VlanAction class.

    This class is internal and is instantiated through subclasses
    """
    class Action(Enum):
        PUSH = 0
        POP = 1
        TRANSLATE = 3
        # XXX TODO add more handlers

    def __init__(self, action: 'VlanAction.Action', num_tags: int,
                 o_vid: VlanTag = None, i_vid: VlanTag = None):
        self._action = action
        self._num_tags = num_tags
        self._o_vid = o_vid
        self._i_vid = i_vid

class VlanActionPush(VlanAction):
    """ Push 1 or 2 tags VLAN action """
    def __init__(self, num_tags: int, ovid: VlanTag, ivid: VlanTag = None):
        assert num_tags == 1 or num_tags == 2
        if num_tags == 2:
            assert ivid is not None
        super().__init__(VlanAction.Action.PUSH, num_tags, ovid, ivid)

class VlanActionPop(VlanAction):
    """ Pop 1 or 2 tags VLAN action """
    def __init__(self, num_tags: int):
        assert num_tags == 1 or num_tags == 2
        super().__init__(VlanAction.Action.POP, num_tags)

class VlanActionTranslate(VlanAction):
    """ Translate 1 or 2 tags VLAN action """
    def __init__(self, num_tags: int, ovid: VlanTag, ivid: VlanTag = None):
        assert num_tags == 1 or num_tags == 2
        if num_tags == 2:
            assert ivid is not None
        super().__init__(VlanAction.Action.TRANSLATE, num_tags, ovid, ivid)

class PacketAction():
    """ Packet action is a dictionary containing field_name: field_value pairs.

    The following field names are supported:
        - vlan: VlanAction
        - tc: supported value: integer traffic class
        - other fields are TBD
    """
    def __init__(self, actions: Dict[str, any]):
        self._actions = actions

    def action(self, name: str):
        """ Get an action by name """
        if name not in self._actions:
            return None
        return self._actions[name]
