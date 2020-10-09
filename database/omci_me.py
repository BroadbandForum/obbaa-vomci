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
# omci_me.py : base classes for all OMCI ME types and ME attributes
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

"""An ME (Managed Entity)

   ME is the base class of all OMCI MEs and includes methods and properties
   for manipulating Attributes.
"""

import logging
from typing import Dict, Optional, Tuple, Union
from omci_types import *
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

### OMCI ME Attribute Descriptor
class Attr(NumberName, AutoGetter):
    """ME attribute class.
    """

    def __init__(self, number: int, name: str, description: Optional[str] = None,
                 access: str = '', requirement: str='',
                 data_type: Datum = None):
        """ME attribute constructor.

        Args:
            number: attribute number; MUST be unique within its ME; 0-16.

            name: attribute name; MUST be unique within its ME.

            description: attribute description; used only for documentation
                purposes.

            access: attribute access level.

            requirement: attribute support requirement

            data: attribute data specification.
        """
        assert 0 <= number <= 16
        assert data_type != None
        super().__init__(number, name, description)

        self._access = access
        self._requirement = requirement
        self._data_type = data_type
        self._is_table = issubclass(type(self), StructDatum)

    def default_value(self) -> AttrValue:
        return self._data_type.default_value()

    def default_raw_value(self) -> AttrValue:
        return self._data_type.default_raw_value()

    def raw_value(self, value: AttrValue) -> AttrValue:
        return self._data_type.raw_value(value)

    def value(self, raw_value: AttrValue) -> AttrValue:
        return self._data_type.value(raw_value)

    @property
    def mask(self):
        """Get this attribute's mask, e.g. the value to use when forming the
        `Get` command's ``attr_mask`` field.

        Note:
            Don't call this on attribute 0 (``me_inst``). You'll get an
            assertion failure.
        """
        # 'me_id' is attribute 0 but it makes no sense to get its mask
        assert 1 <= self._number <= 16
        shift = 16 - self._number  # 15, ..., 0
        return 1 << shift

    @property
    def size(self):
        """Get this attribute's value size in bytes."""
        return self._data_type.size

class MEAttrGetter(AutoGetter):
    """ME attribute getter mixin class.

    Allows ME attributes to be accessed by name.
    """

    def __getattr__(self, name: str) -> Any:
        if name != '_attr_names' and name in self._attr_names:
            return self.attr_value(name)
        return super().__getattr__(name)

class MEAttrSetter():
    """ME attribute setter mixin class.

    Allows ME attributes to be set by name.
    """

    def __setattr__(self, name: str, value):
        if name != '_attr_names' and name in self._attr_names:
            return self.set_attr_value(name, value)
        super().__setattr__(name, value)

class ME(NumberName, MEAttrGetter, MEAttrSetter):
    """ME definition class.
       This is a base class that is never instantiated by itself.
       The derived class must have a few pre-defined class variables.
            me_class: ME class; MUST be unique across all ME
                instances; 0-65535.

            name: ME name; MUST be unique across all ME instances.

            description: ME description; used only for documentation purposes.

            attrs: ME attributes.

            handlers: Actions valid for use with this ME.

            notifications: Notifications generated by this ME.

            changes: Changes generated by this ME.

            alarms: Alarms generated by this ME.
    """

    def __init__(self, inst: int):
        """ME class constructor.

        Args:
            inst: ME instance number 1-65534
        """
        self._attr_names = [a.name for a in self.attrs]
        super().__init__(self.me_class, self.name, self.description)
        # validate that attr id is equal to the index in attr array
        self._attr_values=[inst]
        self._attr_encoded=[True]
        for i in range(1, len(self.attrs)):
            self._attr_values.append(None)
            self._attr_encoded.append(False)
            assert self.attrs[i].number == i
        self._user_data = None
        self.user_name = None

    @property
    def inst(self) -> int:
        return self._attr_values[0]

    def user_attr(self, name: str):
        """ Retrieve user-defined attribute stored in ME instance

        Args:
            name: user attribute name
        Returns:
            user attribute value or None if not found
        """
        if self._user_data is None or name not in self._user_data:
            return None
        return self._user_data[name]

    def set_user_attr(self, name: str, value: Any):
        """ Store user-defined attribute in ME instance

        Args:
            name: user attribute name
            value: user attribute value
        """
        if self._user_data is None:
            self._user_data = {}
        self._user_data[name] = value

    def clear_user_attr(self, name: str):
        """ Clear user-defined attribute stored in ME instance

        Args:
            name: user attribute name
        """
        if self._user_data is not None and name in self._user_data:
            del self._user_data[name]

    def attr(self, number_or_name: Union[int, str]) -> Attr:
        """Find a ME attribute descriptor by number or name.

        Args:
            number_or_name: ME attribute number or name.
        Returns:
            `Attr` descriptor.
        """
        if isinstance(number_or_name, int):
            assert number_or_name >= 0 and number_or_name < len(self.attrs)
            return self.attrs[number_or_name]
        assert number_or_name in self._attr_names
        return self.attrs[self._attr_names.index(number_or_name)]

    def attr_value(self, number_or_name: Union[int, str]) -> AttrValue:
        """Find a ME attribute by number or name and return its value.

        Args:
            number_or_name: ME attribute number or name.
        Returns:
            `Attr` value.
        """
        a = self.attr(number_or_name)
        val = self._attr_values[a.number]
        if val is None:
            val = a.default_value()
        return val

    def set_attr_value(self, number_or_name: Union[int, str], value: AttrValue, set_encoded: bool = False):
        """Find a ME attribute by number or name and set its value.

        Args:
            number_or_name: ME attribute number or name.
            value: value
        """
        a = self.attr(number_or_name)
        raw_val = a.raw_value(value) # validation
        self._attr_values[a.number] = value
        if set_encoded:
            self._attr_encoded[a.number] = True

    def attr_is_set(self, number_or_name: Union[int, str]) -> bool:
        """Find a ME attribute by number or name and return True if the attr is set explicitly.

        Args:
            number_or_name: ME attribute number or name.
        """
        a = self.attr(number_or_name)
        return self._attr_values[a.number] is not None

    def attr_is_encoded(self, number_or_name: Union[int, str]) -> bool:
        """Find a ME attribute by number or name and return True if the attr is set explicitly.

        Args:
            number_or_name: ME attribute number or name.
        """
        a = self.attr(number_or_name)
        return self._attr_encoded[a.number]

    def attr_encode(self, number_or_name: Union[int, str]) -> bytearray:
        """Encode a ME attribute value.
        Args:
            number_or_name: ME attribute number or name.
            value: single value or ``None``.
        Returns:
            Encoded buffer. If ``None`` was supplied, an empty buffer is
            returned.
        """
        a = self.attr(number_or_name)
        val = self._attr_values[a.number]
        buffer = a.data_type.encode(val)
        self._attr_encoded[a.number] = True
        return buffer

    def merge(self, with_me: 'ME'):
        """Merge this ME with another ME by copying all attributes that are explicitly set
        in 'with_me' into self
        """
        if self is with_me:
            return
        assert type(self) is type(with_me)
        for i in range(1, len(self.attrs)):
            if with_me.attr_is_set(i):
                self._attr_values[i] = with_me._attr_values[i]
        if with_me.user_name is not None:
            self.user_name = with_me.user_name
        if with_me._user_data is not None:
            self._user_data = self._user_data and {**self._user_data, **with_me._user_data} or with_me._user_data


    def attr_names(self, access: str = '', assigned_only: BoolDatum = False) -> tuple:
        """Return a list of all attribute names,
        optionally restricted to those with a specified access level.

        Args:
            access: Desired access level, or ``None`` to return all attributes.
            assigned_only: True = return only attributes with explicitly assigned values
        Returns:
            (`name1, name2, name3`).
        Note:
            Attribute 0 is ``me_inst`` (the ME instance number) and is not
            returned.
        """
        return tuple(
                a.name for a in self.attrs
                    if a.number > 0 and access in a.access and
                        (not assigned_only or self._attr_values[a.number] is not None))

    def attr_numbers(self, access: str = '', assigned_only: BoolDatum = False) -> tuple:
        """Return a list of all attribute numbers,
        optionally restricted to those with a specified access level.

        Args:
            access: Desired access level, or ``None`` to return all attributes.
            assigned_only: True = return only attributes with explicitly assigned values
        Returns:
            Tuple in the form of (number1, number2, ..).
        Note:
            Attribute 0 is ``me_inst`` (the ME instance number) and is not
            returned.
        """
        return tuple(a.number for a in self.attrs
            if a.number > 0 and access in a.access and
               (not assigned_only or self._attr_values[a.number] is not None))

    def attr_mask(self, access: str = '', assigned_only: BoolDatum = False) -> int:
        """Return a mask for all attributes,
        optionally restricted to those with a specified access level.

        Args:
            access: Desired access level, or ``None`` to return all attributes.
            assigned_only: True = return only attributes with explicitly assigned values
        Returns:
            attribute bitmask
        """
        attr_numbers = self.attr_numbers(access, assigned_only)
        mask = 0
        for an in attr_numbers:
            mask |= self.attr(an).mask
        return mask

    def to_string(self, assigned_only: bool = False, attr_mask: int = 0):
        s = super().__str__()
        for a in self.attrs:
            val = self._attr_values[a.number]
            if assigned_only and val is None:
                continue
            if a.number > 0 and (a.mask & attr_mask) == 0:
                continue
            if val is None:
                val = a.default_value()
            valfmt = a._data_type._print_format
            s += "\n\t" + str(a) + "=" + valfmt.format(val)
        return s

    def __str__(self) -> str:
        return self.to_string(True, 0xffff)
