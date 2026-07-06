"""
Handler is a package for creating files in an object-oriented way,
allowing extendability to any file system.

Copyright (C) 2021 Gabriel Fontenelle Senno Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Should there be a need for contact the electronic mail
`filejacket <at> gabrielfontenelle.com` can be used.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from .dictionary import (
    FileDictionarySerializer,
    FileWithContentDictionarySerializer,
    FileDictionarySerializerReadonly
)

if TYPE_CHECKING:
    from file import BaseFile


__all__: list[str] = [
    # Serializers
    "FileJsonSerializer",
    "FileWithContentJsonSerializer",
    "FileJsonSerializerReadonly"
]


class SerializerJsonMixin:
    """
    Class helper to convert a serialization class to serialize/deserialize JSON.
    """

    @classmethod
    def serialize(cls, source: BaseFile) -> str:
        """
        Method to serialize the input `source` as a JSON string.
        """
        from json import dumps

        dict_to_convert = super().serialize(source=source)

        return dumps(dict_to_convert)

    @classmethod
    def deserialize(cls, source: str) -> BaseFile:
        """
        Method to deserialize the JSON string input `source`.
        """
        from json import loads

        dict_to_parse = loads(source)

        return super().deserialize(source=dict_to_parse)


class FileJsonSerializer(SerializerJsonMixin, FileDictionarySerializer):
    """
    Class that allow handling of Serialization/Deserialization from BaseFile instance to and from a JSON string.
    This class was created with specificity in mind and would need to be overridden if the object to be serialized has
    a custom class based on BaseFile.
    The content attribute will not be serialized.
    """


class FileWithContentJsonSerializer(
    SerializerJsonMixin, FileWithContentDictionarySerializer
):
    """
    Class that allow handling of Serialization/Deserialization from BaseFile instance to and from a JSON string.
    This class was created with specificity in mind and would need to be overridden if the object to be serialized has
    a custom class based on BaseFile.
    The content attribute will be serialized.
    """


class FileJsonSerializerReadonly(SerializerJsonMixin, FileDictionarySerializerReadonly):
    ...
