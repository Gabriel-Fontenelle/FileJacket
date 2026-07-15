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

from typing import Any, TYPE_CHECKING

from ...engines.serializer import Serializer
from ..transmuter import (
    TransmuterDatetime,
    TransmuterClass,
    TransmuterObjectClass,
    TransmuterPipeline,
    TransmuterAttribute,
    TransmuterContentFiles,
    TransmuterThumbnail,
    TransmuterHashes,
    TransmuterContent,
    TransmuterValue,
    TransmuterContentBase64,
    TransmuterContentFilesReadonly
)


if TYPE_CHECKING:
    from ...file import BaseFile


__all__: list[str] = [
    "FileDictionarySerializer",
    "FileWithContentDictionarySerializer",
    "FileDictionarySerializerReadonly"
]


class FileDictionarySerializer(Serializer):
    """
    Class that allow handling of Serialization/Deserialization from BaseFile instance to and from a Python dictionary.
    This class was created with specificity in mind and would need to be overridden if the object to be serialized is
    having a custom class based on BaseFile.
    The content attribute will not be serialized.
    """

    transmuter: set[str]
    """
    Attribute used by __set_name__ to indicate the transmuters in use by the serializer.
    """

    # Datetime serializer/deserializer
    create_date = TransmuterDatetime()
    update_date = TransmuterDatetime()

    # Class serializer/deserializer
    storage = TransmuterClass()
    serializer = TransmuterClass()
    uri_handler = TransmuterClass()
    mime_type_handler = TransmuterObjectClass()

    # Pipelines serializer/deserializer
    extract_data_pipeline = TransmuterPipeline()
    compare_pipeline = TransmuterPipeline()
    hasher_pipeline = TransmuterPipeline()
    rename_pipeline = TransmuterPipeline()
    compare_pipeline = TransmuterPipeline()

    # File Control classes serializer/deserializer
    _option = TransmuterAttribute()
    _actions = TransmuterAttribute()
    _naming = TransmuterAttribute()
    _state = TransmuterAttribute()
    meta = TransmuterAttribute()
    _content_files = TransmuterContentFiles()
    _thumbnail = TransmuterThumbnail()
    hashes = TransmuterHashes()
    _content = TransmuterContent()

    # Raw attribute serializer/deserilizer
    id = TransmuterValue()
    filename = TransmuterValue()
    extension = TransmuterValue()
    _path = TransmuterValue()
    _save_to = TransmuterValue()
    relative_path = TransmuterValue()
    length = TransmuterValue()
    mime_type = TransmuterValue()
    type = TransmuterValue()
    _pipelines_override_keyword_arguments = TransmuterValue()
    __version__ = TransmuterValue()

    @classmethod
    def serialize(cls, source: BaseFile) -> dict[str, str | int | bool]:
        """
        Method to serialize the input `source`
        """

        return {
            "__source__": TransmuterClass().from_data(source.__class__),
            **{
                attribute: getattr(cls, attribute).from_data(
                    value=getattr(source, attribute)
                )
                for attribute in cls.transmuters
                if hasattr(source, attribute) and getattr(source, attribute) is not None
            },
        }

    @classmethod
    def deserialize(cls, source: dict[str, Any]) -> BaseFile:
        """
        Method to deserialize the input `source`
        """
        data = source.copy()

        class_instance = TransmuterClass().to_data(data["__source__"], reference=None)
        # Create empty file
        file_object = class_instance.__new__(class_instance)

        # Process storage before anything else
        file_object.storage = cls.storage.to_data(
            data["storage"], reference=file_object
        )

        keys = data.keys()
        # Fill content of file with deserialized objects
        kwargs = {
            attribute: getattr(cls, attribute).to_data(
                value=data[attribute], reference=file_object
            )
            for attribute in cls.transmuters
            if attribute in keys
        }

        file_object.__init__(**kwargs)

        return file_object


class FileWithContentDictionarySerializer(FileDictionarySerializer):
    """
    Class that allow handling of Serialization/Deserialization from BaseFile instance to and from a Python dictionary.
    This class was created with specificity in mind and would need to be overridden if the object to be serialized has
    a custom class based on BaseFile.
    The content attribute will be serialized.
    """

    _content = TransmuterContentBase64()


class FileDictionarySerializerReadonly(FileDictionarySerializer):
    """

    """
    _content_files = TransmuterContentFilesReadonly()
