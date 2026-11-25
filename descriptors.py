from dataclasses import dataclass
from enum import StrEnum


class FieldType(StrEnum):
    BYTE = 'B'
    CHAR = 'C'
    DOUBLE = 'D'
    FLOAT = 'F'
    INTEGER = 'I'
    LONG = 'J'
    REFERENCE_CLASS = 'L'
    SHORT = 'S'
    BOOLEAN = 'Z'
    REFERENCE_ARRAY = '['
    VOID = 'V'

@dataclass
class Field:
    field_type: FieldType
    name: str | None = None

@dataclass
class MethodDescriptor:
    parameters: list[Field]
    return_type: Field

    @staticmethod
    def parse_character(s: str):
        t = FieldType(s[0])
        index = 0
        name = None
        if t == FieldType.REFERENCE_CLASS:
            index = 1
            raw_name = s[index:]
            semicolon_index = raw_name.find(';')
            assert semicolon_index != -1
            name = raw_name[:semicolon_index]
            print(name)
            index += len(name)
        
        return index + 1, Field(t, name)

    @classmethod
    def parse(cls, s: str):
        assert s[0] == '('
        return_type = None
        parameters = []
        index = 1
        while index < len(s):
            if s[index] == ')':
                index += 1
                l, last_t = cls.parse_character(s[index:])
                index += l
                return_type = last_t

                break
            l, t = cls.parse_character(s[index:])
            parameters.append(t)

            index += l

        assert return_type
        return cls(parameters, return_type)
