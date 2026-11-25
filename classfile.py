import struct
from dataclasses import dataclass, field
from enum import IntEnum, IntFlag

import descriptors


@dataclass
class ConstantUTF8Info:
    value: str

    @classmethod
    def from_file(cls, f):
        length = struct.unpack('>H', f.read(2))[0]
        return cls(f.read(length).decode('utf-8'))

@dataclass
class ConstantClassInfo:
    name_index: int

    @classmethod
    def from_file(cls, f):
        name_index = struct.unpack('>H', f.read(2))[0]
        return cls(name_index)

@dataclass
class ConstantMethodReference:
    class_index: int
    name_and_type_index: int

    @classmethod
    def from_file(cls, f):
        class_index, name_and_type_index = struct.unpack('>HH', f.read(4))
        return cls(class_index, name_and_type_index)

@dataclass
class ConstantNameAndType:
    name_index: int
    descriptor_index: int

    @classmethod
    def from_file(cls, f):
        name_index, descriptor_index = struct.unpack('>HH', f.read(4))
        return cls(name_index, descriptor_index)

class ConstantMethodTag(IntEnum):
    UTF8_INFO = 1
    CLASS_TYPE = 7
    METHOD_REFERENCE = 10
    NAME_AND_TYPE = 12

@dataclass
class ConstantPoolEntry:
    tag: ConstantMethodTag
    data: ConstantUTF8Info | ConstantClassInfo | ConstantMethodReference | ConstantNameAndType

    @classmethod
    def from_file(cls, f):
        tag = ConstantMethodTag(f.read(1)[0])
        match tag:
            case ConstantMethodTag.UTF8_INFO:
                data = ConstantUTF8Info.from_file(f)
            case ConstantMethodTag.METHOD_REFERENCE:
                data = ConstantMethodReference.from_file(f)
            case ConstantMethodTag.CLASS_TYPE:
                data = ConstantClassInfo.from_file(f)
            case ConstantMethodTag.NAME_AND_TYPE:
                data = ConstantNameAndType.from_file(f)
            case _:
                raise ValueError(f'unhandled tag {tag!r}')


        return cls(tag, data)

@dataclass
class ConstantPool:
    values: list[ConstantPoolEntry]

    @classmethod
    def from_file(cls, f):
        constant_pool_count = struct.unpack('>H', f.read(2))[0]
        values = []

        for _ in range(constant_pool_count - 1):
            values.append(ConstantPoolEntry.from_file(f))

        return cls(values)

    def __getitem__(self, subscript):
        if subscript == 0:
            raise KeyError('constant pool index 0 is illegal')
        return self.values[subscript-1]

@dataclass
class AttributeCode:
    max_stack: int
    max_locals: int
    code: bytes

    @classmethod
    def from_bytes(cls, b):
        max_stack, max_locals, len_code = struct.unpack('>HHI', b[0:8])
        code = b[8:8 + len_code]

        return cls(max_stack, max_locals, code)

@dataclass
class AttributeInfo:
    name_index: int
    info: bytes
    constant_pool: ConstantPool | None = field(repr=False, default=None)

    @property
    def name(self):
        if self.constant_pool is None: return None
        return self.constant_pool[self.name_index].data

    def resolve_code(self) -> AttributeCode | None:
        if self.name is None or self.name.value != 'Code':
            return None

        return AttributeCode.from_bytes(self.info)

    @classmethod
    def from_file(cls, f, constant_pool):
        name_index, attribute_length = struct.unpack('>HI', f.read(6))
        #print(f'name index {constant_pool[name_index]}')
        return cls(name_index, f.read(attribute_length), constant_pool)

class AccessFlags(IntFlag):
    PUBLIC    = 0b000001
    PRIVATE   = 0b000010
    PROTECTED = 0b000100
    STATIC    = 0b001000
    FINAL     = 0b010000
    SUPER     = 0b100000

@dataclass
class MethodInfo:
    access_flags: AccessFlags
    name_index: int
    descriptor_index: int
    attributes: list[AttributeInfo]
    constant_pool: ConstantPool | None = field(repr=False, default=None)

    @property
    def name(self):
        if self.constant_pool is None: return None
        return self.constant_pool[self.name_index].data

    @property
    def descriptor(self):
        if self.constant_pool is None: return None
        return self.constant_pool[self.descriptor_index].data

    def parse_descriptor(self):
        if self.descriptor is None: return None
        return descriptors.MethodDescriptor.parse(self.descriptor.value)

    @classmethod
    def from_file(cls, f, constant_pool: ConstantPool):
        access_flags, name_index, descriptor_index, attributes_count = struct.unpack('>HHHH', f.read(8))
        attributes = []
        for _ in range(attributes_count):
            attributes.append(AttributeInfo.from_file(f, constant_pool))
        return cls(AccessFlags(access_flags), name_index, descriptor_index, attributes, constant_pool)

@dataclass
class ClassFile:
    minor: int
    major: int
    constant_pool: ConstantPool
    access_flags: AccessFlags
    this_class_index: int
    super_class_index: int
    methods: list[MethodInfo]
    attributes: list[AttributeInfo]

    @property
    def this_class(self) -> ConstantClassInfo | None:
        if self.constant_pool is None: return None
        return self.constant_pool[self.this_class_index].data

    @property
    def super_class(self) -> ConstantClassInfo | None:
        if self.constant_pool is None: return None
        return None if self.super_class_index == 0 else self.constant_pool[self.super_class_index].data

    @classmethod
    def from_file(cls, f):
        assert f.read(4) == b'\xca\xfe\xba\xbe'
        minor, major = struct.unpack('>HH', f.read(4))
        constant_pool = ConstantPool.from_file(f)

        access_flags, this_class_index, super_class_index, interfaces_count = struct.unpack('>HHHH', f.read(8))
        assert interfaces_count == 0, 'interfaces are not implemented yet'
        fields_count = struct.unpack('>H', f.read(2))[0]
        assert fields_count == 0, 'fields are not implemented yet'

        methods_count = struct.unpack('>H', f.read(2))[0]
        methods = []
        for _ in range(methods_count):
            methods.append(MethodInfo.from_file(f, constant_pool))
        attributes_count = struct.unpack('>H', f.read(2))[0]
        attributes = []
        for _ in range(attributes_count):
            attributes.append(AttributeInfo.from_file(f, constant_pool))

        return cls(minor, major, constant_pool, AccessFlags(access_flags), this_class_index, super_class_index, methods, attributes)

