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
# Common data types used by OMCI MEs and attributes
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

#
# Common OMCI protocol and helper types
#
import logging
import re
import struct
from typing import Any, Dict, Optional, Set, Tuple, Union
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

OltId = str                 # pOLT name

# Channel termination key
# XXX this type might need to be refined
PonId = str                 # channel-termination name ]

# ONU SBI Id
# XXX this type might need to be refined
OnuSbiId = Tuple[PonId, int]   # [ PonID, TC layer ONU id ]

# OnuNbiId
OnuName = str

#


#
# Helper types
#

# Internal attribute value types
AttrSingleRawValue = Union[bool, bytearray, int, str]
AttrRawValue = Union[AttrSingleRawValue, Tuple[AttrSingleRawValue, ...]]
# External attribute value types
AttrSingleValue = Union[bool, bytearray, int, str]
StructFieldValue = Dict[str, AttrSingleValue]
AttrValue = Union[AttrSingleValue, Tuple[StructFieldValue]]

NameValuePair = Tuple[str, AttrValue]
NameValueOrName = Union[NameValuePair, str]
NameValueList = Tuple[NameValueOrName, ...]

RawMessage = bytearray

EnumValue = Tuple[str, int]
EnumValues = Tuple[EnumValue, ...]

# within a given type (class), name must be a unique key
class Name:
    """Name (and description) mixin class.
    """

    def __init__(self, name: str, description: Optional[str] = None, *,
                 names: Optional[Set[str]] = None):
        assert names is None or name in names
        self._name = name
        self._description = description or ''

    def info(self) -> str:
        description = ' %r' % self._description if self._description else ''
        return '%s%s' % (self._name, description)

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        description = self._description and ', description=%r' % \
                      self._description or ''
        return '%s(name=%r%s)' % (self.__class__.__name__, self._name,
                                  description)


# within a given type (class), number be a unique key (and name via Name)
class NumberName(Name):
    """Number, name (and description) mixin class.
    """

    def __init__(self, number: int, name: str, description: Optional[str] = None, *,
                 names: Optional[Set[str]] = None):
        super().__init__(name, description=description, names=names)
        self._number = number

    @property
    def number(self):
        return self._number

    def info(self) -> str:
        description = ' %r' % self._description if self._description else ''
        return '%d (%s)%s' % (self._number, self._name, description)

    def __str__(self) -> str:
        return '%d(%s)' % (self._number, self._name)

    def __repr__(self) -> str:
        description = self._description and ', description=%r' % \
                      self._description or ''
        return '%s(number=%r, name=%r%s)' % (
            self.__class__.__name__, self._number, self._name, description)


class AutoGetter:
    """Auto-getter mixin class.

    Allows ``instance._attr`` to be accessed (only for read access) as
    ``instance.attr``.
    """

    def __getattr__(self, name: str) -> Any:
        _name = name.startswith('_') and name or '_' + name
        if _name in dir(self):
            return super().__getattribute__(_name)
        else:
            raise AttributeError('%r object has no attribute %r' % (
                self.__class__.__name__, name))


class Datum(AutoGetter):
    """Single data item class.

    Defines a single data item of a given type, with support for initial and
    fixed values, for encoding and decoding values, and for converting
    between user and raw values.
    """

    def __init__(self, size: int, default: Optional[AttrValue] = None,
                 fixed: Optional[AttrValue] = None):
        """Data item constructor.

        Args:
            size: size of data item in bytes.

            default: default value of data item (used if no value is
                specified).

            fixed: fixed value of data item (takes precedence over the
                default; any attempt to define a data item instance with a
                different value is an error).

        Note:
            Either value or fixed MUST currently be provided (it determines the type).
        """
        assert default is not None or fixed is not None
        self._size = size
        self._is_fixed = (fixed != None)
        _default = fixed and fixed or default
        # Validate the default value. Throws exception if invalid
        self._raw_default = self.raw_value(_default)

    def decode(self, buffer: bytearray, offset: int) -> Tuple[AttrValue, int]:
        """Decode data item value.

        Args:
            buffer: buffer from which to decode the value

            offset: byte offset within buffer at which to start decoding

        Returns:
            Decoded value and updated offset.

            * If there isn't sufficient data in the buffer, the default
              value is returned

            * The returned value is a user value (it's converted from the raw
              value)

            * The offset is ready to be passed to the next ``decode``
              invocation
        """
        size = self._size
        format_ = self._struct_format
        if offset + size > len(buffer):
            raise ValueError('{} attempt to decode {} bytes past the end of buffer'.format(self._name, size))
        else:
            # logger.debug('{}: decoding {} bytes from offset {}. buffer {}'.format(
            #     self.__class__.__name__, size, offset, buffer[offset:offset+size]))
            raw_value = struct.unpack_from(format_, buffer, offset)[0]
            value = self.value(raw_value)
        return value, offset + size

    def encode(self, value: AttrValue = None) -> bytearray:
        """Encode data item value.

        Args:
            value: the value to be encoded

        Returns:
            Encoded buffer.

            * If value is ``None``, the default value is encoded
            * The value is converted to a raw value before encoding
        """
        format_ = self._struct_format
        buffer = bytearray(self._size)
        raw_value = value and self.raw_value(value) or self._raw_default
        if isinstance(raw_value, list) or isinstance(raw_value, tuple):
            struct.pack_into(format_, buffer, 0, *raw_value)
        else:
            struct.pack_into(format_, buffer, 0, raw_value)
        return buffer

    def raw_value(self, value: AttrValue) -> AttrRawValue:
        """Convert data item user value to raw value.

        Args:
            value: external attribute value
        Returns:
            raw (internal) attribute value
        """
        raise Exception('Unimplemented raw_value() method')

    def value(self, raw_value: AttrRawValue) -> AttrValue:
        """Convert data item raw value to user value.

        Args:
            raw_value: raw (internal) attribute value
        Returns:
            External attribute value
        """
        raise Exception('Unimplemented value() method')

    def default_raw_value(self) -> AttrValue:
        """Returns: fixed or default value.
        """
        return self._raw_default

    def default_value(self) -> AttrValue:
        """Returns: fixed or default value.
        """
        return self.value(self._raw_default)

    @property
    def _struct_format(self) -> str:
        raise Exception('Unimplemented struct_format property')

    @property
    def _print_format(self) -> str:
        return '{}'

    def __str__(self) -> str:
        extra = '==%r' % self.default_value()
        return '%s(%d)%s' % (self.__class__.__name__, self._size, extra)

    def __repr__(self) -> str:

        out = self._is_fixed and ', fixed=' or ', default='
        out += "%r" % self.default_value()
        return '%s(size=%r%s)' % (
            self.__class__.__name__, self._size, out)


class BoolDatum(Datum):
    """Boolean data item class.
    """
    def __init__(self, size: int, default: Optional[bool] = None, fixed: Optional[bool] = None):
        """The default defaults to false.
        """
        default = default or False
        super().__init__(size, default=default, fixed=fixed)

    def raw_value(self, value: bool) -> int:
        assert type(value).__name__ == 'bool'
        return int(value)

    def value(self, raw_value: int) -> bool:
        return str(bool(raw_value))

    @property
    def _struct_format(self) -> str:
        assert self._size in {1, 2, 4, 8}
        return '!%s' % {1: 'B', 2: 'H', 4: 'I', 8: 'Q'}[self._size]

class EnumDatum(Datum):
    """Enumeration data item class.
    """
    def __init__(self, size: int, values: EnumValues,
                 default: Optional[str] = None, fixed: Optional[str] = None):
        default = default or (values[0][0] if (values and len(values[0]) > 1) else '')
        self._values = []
        self._raw_values = []
        for val in values:
            self._values.append(val[0])
            self._raw_values.append(len(val)>1 and val[1] or (len(self._values)-1))
        self._values = tuple(self._values)
        self._raw_values = tuple(self._raw_values)
        super().__init__(size, default=default, fixed=fixed)

    # XXX this throws ValueError if the value isn't found
    def raw_value(self, value: str) -> int:
        # Accepts numeric and string value
        if isinstance(value, int):
            # validate the index and return it
            _tmp = self.value(value)
            return value
        return self._raw_values[self._values.index(value)]

    # XXX this throws IndexError if the raw_value is invalid
    def value(self, raw_value: int) -> str:
        # logger.debug('{}: converting value {}'.format(self.__class__.__name__, raw_value))
        return self._values[self._raw_values.index(raw_value)]

    @property
    def _struct_format(self) -> str:
        assert self._size in {1, 2, 4, 8}
        return '!%s' % {1: 'B', 2: 'H', 4: 'I', 8: 'Q'}[self._size]

    def __str__(self) -> str:
        return '%s-%s %s' % (super().__str__(), self.default_value(), self._values)

    def __getitem__(self, key: str) -> int:
        return self.raw_value(key)


# XXX Bits is currently the same as Enum; it needs different logic
class BitsDatum(EnumDatum):
    """Bits data item class.
    """
    pass


class NumberDatum(Datum):
    """Number data item class.
    """
    def __init__(self, size: int, default: Optional[int] = None, fixed: Optional[int] = None,
                 units: Optional[str] = None):
        default = default or 0
        super().__init__(size, default=default, fixed=fixed)
        # XXX units are currently ignored
        self._units = units

    def raw_value(self, value: int) -> int:
        assert type(value).__name__ == 'int'
        # XXX add range checks
        return value

    def value(self, raw_value: int) -> int:
        return raw_value

    @property
    def _struct_format(self) -> str:
        assert self._size in {1, 2, 4, 8}
        return '!%s' % {1: 'B', 2: 'H', 4: 'I', 8: 'Q'}[self._size]


class StringDatum(Datum):
    """String data item class.
    """
    def __init__(self, size: int, default: Optional[str] = None, fixed: Optional[str] = None):
        default = default or ''
        super().__init__(size, default=default, fixed=fixed)

    def raw_value(self, value: str) -> bytes:
        assert type(value).__name__ == 'str'
        return bytes(value, 'utf-8')

    def value(self, raw_value: bytes) -> str:
        return re.sub(br'\x00*$', b'', raw_value).decode('utf-8')

    @property
    def _struct_format(self) -> str:
        return '!%ds' % self._size


class BytesDatum(Datum):
    """Bytes data item class.
    """
    def __init__(self, size: int, default: Optional[bytes] = None, fixed: Optional[bytes] = None):
        default = default or b''
        super().__init__(size, default=default, fixed=fixed)

    def raw_value(self, value) -> bytes:
        val_len = len(value)
        assert val_len <= self.size
        if val_len == self.size:
            return value
        return value + bytes(b'\x00' * (self.size - val_len))

    def value(self, raw_value: bytes) -> bytes:
        return raw_value

    @property
    def _struct_format(self) -> str:
        # not 'p' because only for 's' is the count the item size
        return '!%ds' % self._size

DatumList = Tuple[Datum, ...]

class StructField(Name, AutoGetter):
    """Structure field
       Name, Datum pair
    """
    def __init__(self, name: str, description : Optional[str] = None,
                 field_type : Datum = None):
        super().__init__(name, description)
        self._field_type = field_type

class StructDatum(Datum):
    """Structure data item class.
       Derived classes must include 'size' and 'fields' as the class variables.
       'fields' is a tuple of StructField
    """
    def __init__(self, size: int, default: Optional[AttrValue] = None, fixed: Optional[AttrValue] = None):
        self._field_names = [f._name for f in self.fields]
        if (self.__class__.__bases__)[0].__name__ != 'BitStructDatum':
            assert size == sum(f.field_type.size for f in self.fields)
        # Handle fixed and default values
        # If set, must be an array of positional values or a dictionary
        if fixed is not None:
            assert fixed.len() <= self.fields.len()
            _fixed = isinstance(fixed, dict) and fixed or {self.fields[i].name: fixed[i] for i in range(len(fixed))}

        _default = {}
        if default is not None:
            assert default.len() <= self.fields.len()
            if isinstance(default, dict):
                for dv in default.items():
                    _default[dv[0]] = dv[1]
            else:
                _default = {self.fields[i].name: default[i] for i in range(len(default))}

        # Initialize unassigned defaults
        for f in self.fields:
            if fixed is not None and f.name in _fixed:
                _default[f.name] = _fixed[f.name]
            elif f.name not in _default:
                _default[f.name] = f.field_type.default_value()

        super().__init__(size, default=_default, fixed=fixed and _fixed or None)

        self._format = ''
        for f in self.fields:
            self._format += f._field_type._struct_format
        # Keep only 1 leading '!'
        self._format = '!' + self._format.replace('!','')

    def raw_value(self, values: AttrValue) -> AttrRawValue:
        raw_values=[]
        if isinstance(values, dict):
            for val_name, val_value in values.items():
                fi = self._field_names.index(val_name)
                raw_values.append(self.fields[fi].field_type.raw_value(val_value))
        else:
            for i in range(len(values)):
                val = values[i]
                raw_values.append(self.fields[i].field_type.raw_value(values[i]))
        return raw_values

    def value(self, raw_values: AttrRawValue) -> AttrValue:
        assert len(raw_values) == len(self.fields)
        values={}
        for i in range(0, len(self.fields)):
            values[self.fields[i].name] = self.fields[i].field_type.value(raw_values[i])
        return values

    @property
    def _struct_format(self) -> str:
        return self._format

class BitField(StructField):
    """Bitfield.
    """
    def __init__(self, name: str, description : Optional[str] = None, width : int = None):
        super().__init__(name, description, field_type=NumberDatum(4))
        assert width is not None
        self._width = width
        self._offset = 0 # fill be re-assigned in BitStruct constructor

    def raw_value(self, val: int):
        val &= ((1 << self._width) - 1)
        val = val << self._offset
        return val


class BitStructDatum(StructDatum):
    """Structure data item class.
       Derived classes must include 'size' and 'fields' as the class variables.
       'fields' is a tuple of BitField
    """
    def __init__(self, size: int,
                 default: Optional[AttrValue] = None, fixed: Optional[AttrValue] = None):
        assert size in {2, 4}
        self._width = size * 8
        offset = self._width
        for f in self.fields:
            f._offset = offset - f.width
            offset = f._offset
        super().__init__(size, default=default, fixed=fixed)
        assert self._width == sum(f.width for f in self.fields)

    def raw_value(self, values: AttrValue) -> int:
        assert len(values) <= len(self.fields)
        _offset = self._width
        _raw_value = 0
        if isinstance(values, dict):
            for val_name, val_value in values.items():
                fi = self._field_names.index(val_name)
                _raw_value |= self.fields[fi].raw_value(val_value)
        else:
            for fi in range(len(values)):
                _raw_value |= self.fields[fi].raw_value(values[fi])

        return _raw_value

    def value(self, raw_value: int) -> AttrValue:
        values={}
        _offset = self._width
        for f in self.fields:
            _offset = _offset - f.width
            _val = (raw_value >> _offset) & ((1 << f.width) - 1)
            values[f.name] = _val
        return values

    @property
    def _struct_format(self) -> str:
        assert self._size in {1, 2, 4, 8}
        return '!%s' % {1: 'B', 2: 'H', 4: 'I', 8: 'Q'}[self._size]
