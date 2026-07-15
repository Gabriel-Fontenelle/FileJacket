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

from base64 import b64decode
from datetime import datetime, time
from importlib import import_module
from typing import Any, Type, TYPE_CHECKING

from ..exception import SerializerError
from ..file.content import FileContent, FilePacket
from ..file.hasher import FileHashes
from ..file.thumbnail import FileThumbnail
from ..adapters.pipeline import PipelineOrderedDependency
from ..engines.pipeline import PipelineEngine
from ..engines.transmuter import TransmuterEngine

if TYPE_CHECKING:
    from ..file import BaseFile
    from ..file.content import BufferBytes, BufferStr


__all__: list[str] = [
    # Transmuters
    "TransmuterClass",
    "TransmuterObjectClass",
    "TransmuterPipeline",
    "TransmuterDatetime",
    "TransmuterAttribute",
    "TransmuterValue",
    "TransmuterThumbnail",
    "TransmuterHashes",
    "TransmuterContentFiles",
    "TransmuterContent",
    "TransmuterContentBase64",
]


class TransmuterClass(TransmuterEngine):
    """
    Transmuter class to handle non instantiated class.
    """

    def from_data(self, value: Type) -> str:
        """
        Method to convert `value` to string for use in dict.
        """
        return f"{value.__module__}.{value.__name__}"

    def to_data(self, value: str, reference: BaseFile) -> Type:
        """
        Method to reverse the conversion at `from_data`.
        """
        module_name, class_name = value.rsplit(".", maxsplit=1)
        module = import_module(module_name)
        return getattr(module, class_name)


class TransmuterObjectClass(TransmuterEngine):
    """
    Transmuter class to handle instantiated class.
    """

    def from_data(self, value: object) -> str:
        """
        Method to convert `value` to string for serialization.
        """
        return f"{value.__class__.__module__}.{value.__class__.__name__}"

    def to_data(self, value: str, reference: BaseFile) -> Any:
        """
        Method to reverse the conversion at `from_data`.
        """
        module_name, class_name = value.rsplit(".", maxsplit=1)
        module = import_module(module_name)
        return getattr(module, class_name)()


class TransmuterPipeline(TransmuterEngine):
    """
    Transmuter class to handle Pipeline objects.
    """

    def from_data(self, value: PipelineEngine) -> dict[str, str | list[str]]:
        """
        Method to convert `value` to dict for serialization.
        """
        transmuter_class = TransmuterClass()
        transmuter_class.serializer = self.serializer

        return {
            "pipeline": transmuter_class.from_data(value.__class__),
            "processor": transmuter_class.from_data(value.processor),
            "processors_candidate": value.processors_candidate,
        }

    def to_data(self, value: dict[str, Any], reference: BaseFile) -> PipelineEngine:
        """
        Method to reverse the conversion at `from_data`.
        """
        transmuter_class = TransmuterClass()
        transmuter_class.serializer = self.serializer

        pipeline = transmuter_class.to_data(value["pipeline"], reference=reference)(
            *value["processors_candidate"]
        )
        pipeline.processor = transmuter_class.to_data(
            value["processor"], reference=reference
        )

        return pipeline


class TransmuterDatetime(TransmuterEngine):
    """
    Transmuter class to handle datetime or time objects.
    """

    def from_data(self, value: datetime | time) -> str:
        """
        Method to convert `value` to string for serialization.
        """
        instance_type = "d" if isinstance(value, datetime) else "t"

        return f"{instance_type}:{value.isoformat()}"

    def to_data(self, value: str, reference: BaseFile) -> datetime | time:
        """
        Method to reverse the conversion at `from_data`.
        """
        instance_type, data = value.split(":", maxsplit=1)

        data_type = datetime if instance_type == "d" else time
        return data_type.fromisoformat(data)


class TransmuterAttribute(TransmuterEngine):
    """
    Transmuter class to handle attribute that are objects from classes.
    """

    def from_data(self, value: Any) -> dict[str, Any]:
        """
        Method to convert `value` to dict for serialization.
        """
        values = value.__serialize__

        if "related_file_object" in values:
            values["related_file_object"] = values["related_file_object"].id

        transmuter_object_class = TransmuterObjectClass()
        transmuter_object_class.serializer = self.serializer

        return {
            "__source__": transmuter_object_class.from_data(value),
            "values": values,
        }

    def to_data(self, value: dict[str, Any], reference: BaseFile) -> object:
        """
        Method to reverse the conversion at `from_data`.
        """
        transmuter_object_class = TransmuterClass()
        transmuter_object_class.serializer = self.serializer

        attribute_object = transmuter_object_class.to_data(
            value["__source__"], reference=reference
        )

        values = value["values"]

        if "related_file_object" in values:
            values["related_file_object"] = reference

        return attribute_object(**values)


class TransmuterValue(TransmuterEngine):
    """
    Transmuter class to handle attributes that don`t need to be converted.
    """

    def from_data(self, value: Any) -> Any:
        """
        Method to return the same `value` for serialization.
        """
        return value

    def to_data(self, value: Any, reference: BaseFile) -> Any:
        """
        Method to reverse the conversion at `from_data`.
        """
        return value


class TransmuterThumbnail(TransmuterEngine):
    """
    Transmuter class to handle the FileThumbnail object.
    """

    def from_data(self, value: FileThumbnail) -> dict[str, Any]:
        """
        Method to convert `value` to dict for serialization.
        """
        from ..adapters.serializer import FileWithContentDictionarySerializer

        thumbnail = value.__serialize__

        # Convert _static_file and _animated_file to Base64
        # static_file = thumbnail["_static_file"].content_as_base64 if thumbnail["_static_file"] else None
        # animated_file = thumbnail["_animated_file"].content_as_base64 if thumbnail["_animated_file"] else None
        # TODO: Simplify usage of serializer instead of whole file to save only the content as base64.
        static_file = (
            FileWithContentDictionarySerializer.serialize(thumbnail["_static_file"])
            if thumbnail["_static_file"] is not None
            and thumbnail["_static_file"] is not False
            else None
        )
        animated_file = (
            FileWithContentDictionarySerializer.serialize(thumbnail["_animated_file"])
            if thumbnail["_animated_file"] is not None
            and thumbnail["_animated_file"] is not False
            else None
        )

        transmuter_class = TransmuterClass()
        transmuter_class.serializer = self.serializer

        transmuter_pipeline = TransmuterPipeline()
        transmuter_pipeline.serializer = self.serializer

        return {
            "static_defaults": transmuter_class.from_data(thumbnail["static_defaults"]),
            "animated_defaults": transmuter_class.from_data(
                thumbnail["animated_defaults"]
            ),
            "static_file": static_file,
            "animated_file": animated_file,
            "image_engine": transmuter_class.from_data(thumbnail["image_engine"]),
            "video_engine": transmuter_class.from_data(thumbnail["video_engine"]),
            "render_static_pipeline": transmuter_pipeline.from_data(
                thumbnail["render_static_pipeline"]
            ),
            "render_animated_pipeline": transmuter_pipeline.from_data(
                thumbnail["render_animated_pipeline"]
            ),
        }

    def to_data(self, value: dict[str, Any], reference: BaseFile) -> FileThumbnail:
        """
        Method to reverse the conversion at `from_data`.
        """
        from ..adapters.serializer import FileWithContentDictionarySerializer

        file_thumbnail = FileThumbnail()
        file_thumbnail.related_file_object = reference

        transmuter_class = TransmuterClass()
        transmuter_class.serializer = self.serializer

        transmuter_pipeline = TransmuterPipeline()
        transmuter_pipeline.serializer = self.serializer

        file_thumbnail.static_defaults = transmuter_class.to_data(
            value["static_defaults"], reference=reference
        )
        file_thumbnail.animated_defaults = transmuter_class.to_data(
            value["animated_defaults"], reference=reference
        )
        file_thumbnail.image_engine = transmuter_class.to_data(
            value["image_engine"], reference=reference
        )
        file_thumbnail.video_engine = transmuter_class.to_data(
            value["video_engine"], reference=reference
        )
        file_thumbnail.render_static_pipeline = transmuter_pipeline.to_data(
            value["render_static_pipeline"], reference=reference
        )
        file_thumbnail.render_animated_pipeline = transmuter_pipeline.to_data(
            value["render_animated_pipeline"], reference=reference
        )

        if value["static_file"]:
            file_thumbnail._static_file = (
                FileWithContentDictionarySerializer.deserialize(value["static_file"])
            )
            # file_thumbnail._static_file = thumbnail["_static_file"].content_as_base64 if thumbnail["_static_file"] else None

        if value["animated_file"]:
            file_thumbnail._animated_file = (
                FileWithContentDictionarySerializer.deserialize(value["animated_file"])
            )
            # file_thumbnail._animated_file = thumbnail["_animated_file"].content_as_base64 if thumbnail["_animated_file"] else None

        return file_thumbnail


class TransmuterHashes(TransmuterEngine):
    """
    Transmuter class to handle the FileHash object.
    """

    def from_data(self, value: FileHashes) -> dict[str, Any]:
        """
        Method to convert `value` to dict for serialization.
        """
        hashes = value.__serialize__

        transmuter_class = TransmuterClass()
        transmuter_class.serializer = self.serializer

        cache = {}
        for hash_name, hash_tuple in hashes["_cache"].items():
            cache_file = hash_tuple[1]

            if not cache_file.meta.loaded:
                serialized = {
                    "path": cache_file.sanitize_path,
                    "class": transmuter_class.from_data(cache_file.__class__),
                }
            else:
                serialized = {
                    "path": cache_file.sanitize_path,
                    "class": transmuter_class.from_data(cache_file.__class__),
                    "content": self.serializer._content.from_data(cache_file._content)
                    if cache_file._content
                    else None,
                }

            cache[hash_name] = (
                hash_tuple[0],
                serialized,
                transmuter_class.from_data(hash_tuple[2]),
            )

        # We don`t need `_loaded` neither `related_file_object` as they can be inferred from _cache and file object.
        return cache

    def to_data(self, value: dict[str, Any], reference: BaseFile) -> FileHashes:
        """
        Method to reverse the conversion at `from_data`.
        """
        file_hashes = FileHashes()
        file_hashes.related_file_object = reference

        transmuter_class = TransmuterClass()
        transmuter_class.serializer = self.serializer

        for hash_name, hash_tuple in value.items():
            cache_file_class = transmuter_class.to_data(
                hash_tuple[1]["class"], reference=reference
            )
            if "content" in hash_tuple[1]:
                hash_file: BaseFile = cache_file_class(path=hash_tuple[1]["path"])
                hash_file._content = (
                    self.serializer._content.to_data(hash_tuple[1]["content"], reference=hash_file)
                    if hash_tuple[1]["content"]
                    else None
                )

                # Set up metadata checksum as boolean to indicate whether the source
                # of the hash is a CHECKSUM.hasher_name file (contains multiple files) or not.
                hash_file.meta.checksum = False

                # Set up metadata loaded as boolean to indicate whether the source
                # of the hash was loaded from a file or not.
                hash_file.meta.loaded = True
            else:
                # Add hash to file
                hash_file: BaseFile = cache_file_class(
                    path=hash_tuple[1]["path"],
                    extract_data_pipeline=PipelineOrderedDependency(
                        "filejacket.pipelines.extractor.FilenameAndExtensionFromPathExtractor",
                        "filejacket.pipelines.extractor.MimeTypeFromFilenameExtractor",
                    ),
                    file_system_handler=reference.storage,
                )
                # Set up metadata checksum as boolean to indicate whether the source
                # of the hash is a CHECKSUM.hasher_name file (contains multiple files) or not.
                hash_file.meta.checksum = False

                # Set up metadata loaded as boolean to indicate whether the source
                # of the hash was loaded from a file or not.
                hash_file.meta.loaded = False

                # Generate content for file
                content: str = "# Generated by Handler\r\n"
                content += f"{hash_tuple[0]} {reference.complete_filename}\r\n"
                hash_file.content = content

            file_hashes[hash_name] = (
                hash_tuple[0],
                hash_file,
                transmuter_class.to_data(hash_tuple[2], reference=reference),
            )

        return file_hashes


class TransmuterContentFiles(TransmuterEngine):
    """
    Transmuter class to handle the FilePacket object.
    """

    def from_data(self, value: FilePacket) -> dict[str, str | dict | list]:
        """
        Method to convert `value` to dict for serialization.
        The history attribute of FilePacket will not be serialized.
        """
        # Case should cache convert to base64
        content_files = value.__serialize__

        transmuter_pipeline = TransmuterPipeline()
        transmuter_pipeline.serializer = self.serializer

        transmuter_content = TransmuterContent()
        transmuter_content.serializer = self.serializer

        return {
            "internal_files": {
                key: (self.serializer.serialize(value[0]), value[1], value[2])
                for key, value in content_files["_internal_files"].items()
            },
            "unpack_data_pipeline": transmuter_pipeline.from_data(
                content_files["unpack_data_pipeline"]
            ),
            "length": content_files["length"]
        }

    def to_data(self, value: dict[str, Any], reference: BaseFile) -> FilePacket:
        """
        Method to reverse the conversion at `from_data`.
        """

        transmuter_pipeline = TransmuterPipeline()
        transmuter_pipeline.serializer = self.serializer

        return FilePacket(
            _internal_files={
                key: [self.serializer.deserialize(value[0]), value[1], value[2]]
                for key, value in value["internal_files"].items()
            },
            unpack_data_pipeline=transmuter_pipeline.to_data(
                value["unpack_data_pipeline"], reference=reference
            ),
            length=value["length"]
        )


class TransmuterContentFilesReadonly(TransmuterEngine):
    """
    Transmuter class to handle the FilePacket object when is not needed to convert to data.
    """

    def from_data(self, value: FilePacket) -> dict[str, str | dict | list]:
        """
        Method to convert `value` to dict for serialization.
        The history attribute of FilePacket will not be serialized.
        """
        # Case should cache convert to base64
        content_files = value.__serialize__

        transmuter_pipeline = TransmuterPipeline()
        transmuter_pipeline.serializer = self.serializer

        return {
            "length": content_files["length"],
            "unpack_data_pipeline": transmuter_pipeline.from_data(
                content_files["unpack_data_pipeline"]
            ),
            "internal_files": {
                key: (
                    {
                        "crc32": value[0].hashes["crc32"][0] if "crc32" in value[0].hashes else None,
                        "length": value[1],
                        "type": value[2],
                    }
                )
                for key, value in content_files["_internal_files"].items()
            },
        }

    def to_data(self, value: dict[str, Any], reference: BaseFile) -> FilePacket:
        """
        Method to reverse the conversion at `from_data` returning the default clear FilePacket.
        """

        return FilePacket()


class TransmuterContent(TransmuterEngine):
    """
    Transmuter class to handle the FileContent object.
    """

    def from_data(self, value: FileContent) -> dict[str, str] | None:
        """
        Method to convert `value`source to dict for serialization.
        """
        dict_to_return = value.__serialize__

        if value.should_load_to_memory and not value.inner:
            raise SerializerError(
                "Content for file should be serialized as it should be load to memory and may not be available later.\nPlease, use a serializer that saves the content."
            )

        del dict_to_return["_cached_content"]
        del dict_to_return["related_file_object"]

        transmuter_class_object = TransmuterObjectClass()
        transmuter_class_object.serializer = self.serializer

        transmuter_class = TransmuterClass()
        transmuter_class.serializer = self.serializer

        if value.inner:
            # Buffer = filename:class:mode:
            buffer_name = getattr(dict_to_return["buffer"], "filename", "")
            buffer_mode = getattr(dict_to_return["buffer"], "mode", "")
            buffer_reference = getattr(dict_to_return["buffer"], "reference", "")

            if not buffer_name or not buffer_mode or not buffer_reference:
                raise SerializerError(
                    "Internal file should be a implementation of `ContentBuffer` that implements `filename`, `mode` and `reference`."
                )

            dict_to_return[
                "buffer"
            ] = f"internal:{buffer_name}:{buffer_mode}:{transmuter_class.from_data(buffer_reference)}"

        else:
            # If no buffer available, it should return None.
            buffer_name = getattr(dict_to_return["buffer"], "name", "")
            buffer_mode = getattr(dict_to_return["buffer"], "mode", "")

            if not buffer_name and not buffer_mode:
                return None

            # Convert buffer to a structure that can be used to instantiate a new buffer later.
            dict_to_return[
                "buffer"
            ] = f"{getattr(dict_to_return['buffer'], 'name', '')}:{getattr(dict_to_return['buffer'], 'mode', '')}"

        dict_to_return[
            "buffer_helper"
        ] = f"{transmuter_class_object.from_data(dict_to_return['buffer_helper'])}:{dict_to_return['buffer_helper'].encoding}"
        dict_to_return[
            "cache_helper"
        ] = f"{transmuter_class.from_data(dict_to_return['cache_helper'])}"

        return dict_to_return

    def to_data(
        self, value: dict[str, Any] | None, reference: BaseFile
    ) -> FileContent | None:
        """
        Method to reverse the conversion at `from_data`.
        """
        # Dont initialize the FileContent if the buffer was empty, meaning it as None at `from_data`.
        if value is None:
            return None

        buffer = value.pop("buffer").rsplit(":", 1)

        transmuter_class_object = TransmuterObjectClass()
        transmuter_class_object.serializer = self.serializer

        transmuter_class = TransmuterClass()
        transmuter_class.serializer = self.serializer

        if buffer[0] == "internal":
            buffer = buffer[1].split(":")
            buffer[0]  # buffer_filename
            buffer[1]  # buffer_mode
            buffer[2]  # buffer_reference

            buffer_class = transmuter_class.to_data(buffer[2], reference=reference)
            buffered = buffer_class.content_buffer(
                file_object=reference, internal_file_name=buffer[0], mode=buffer[1]
            )

        else:
            buffered = reference.storage.open_file(path=buffer[0], mode=buffer[1])

        buffer_helper = value.pop("buffer_helper").rsplit(":", 1)

        buffer_helper_object: BufferBytes | BufferStr = transmuter_class_object.to_data(
            buffer_helper[0], reference=reference
        )
        buffer_helper_object.encoding = buffer_helper[1]

        cache_helper: str = value.pop("cache_helper")
        cache_helper_class = transmuter_class.to_data(cache_helper, reference=reference)

        value.pop("cached")

        return FileContent(
            raw_value=None,
            buffer=buffered,
            related_file_object=reference,
            buffer_helper=buffer_helper_object,
            cache_helper=cache_helper_class,
            **value,
        )


class TransmuterContentBase64(TransmuterEngine):
    """
    Transmuter class to handle the FileContent object as its base64 representation.
    """

    def from_data(self, value: FileContent) -> dict[str, str]:
        """
        Method to convert `value` to string for serialization.
        """
        dict_to_return = value.__serialize__

        del dict_to_return["_cached_content"]
        del dict_to_return["related_file_object"]

        dict_to_return["content_base64"] = value.content_as_base64

        # Convert buffer to a structure that can be used to instantiate a new buffer later.
        dict_to_return[
            "buffer"
        ] = f"{getattr(dict_to_return['buffer'], 'name', '')}:{getattr(dict_to_return['buffer'], 'mode', '')}"

        transmuter_class_object = TransmuterObjectClass()
        transmuter_class_object.serializer = self.serializer

        transmuter_class = TransmuterClass()
        transmuter_class.serializer = self.serializer

        dict_to_return[
            "buffer_helper"
        ] = f"{transmuter_class_object.from_data(dict_to_return['buffer_helper'])}:{dict_to_return['buffer_helper'].encoding}"
        dict_to_return[
            "cache_helper"
        ] = f"{transmuter_class.from_data(dict_to_return['cache_helper'])}"

        return dict_to_return

    def to_data(self, value: dict[str, Any], reference: BaseFile) -> FileContent:
        """
        Method to reverse the conversion at `from_data`.
        """
        buffer = value.pop("buffer").rsplit(":", 1)
        buffer_helper = value.pop("buffer_helper").rsplit(":", 1)

        content: bytes = b64decode(value.pop("content_base64"))

        transmuter_class_object = TransmuterObjectClass()
        transmuter_class_object.serializer = self.serializer

        buffer_object: BufferBytes | BufferStr = transmuter_class_object.to_data(
            buffer_helper[0], reference=reference
        )
        buffer_object.encoding = buffer_helper[1]

        transmuter_class = TransmuterClass()
        transmuter_class.serializer = self.serializer

        cache_helper = value.pop("cache_helper")
        cache_helper_class = transmuter_class.to_data(cache_helper, reference=reference)

        # set content
        cache_content = cache_helper_class(buffer_helper=buffer_object)
        cache_content.content = content

        value.pop("cached")

        buffer_data = {}

        # Fix for when buffer comes from a content file not saved (Thumbnails or internal files).
        if any(buffer):
            buffer_data["buffer"] = reference.storage.open_file(path=buffer[0], mode=buffer[1])
        else:
            buffer_data["raw_value"] = content

        return FileContent(
            related_file_object=reference,
            buffer_helper=buffer_object,
            _cached_content=cache_content,
            cache_helper=cache_helper_class,
            **value,
            **buffer_data
        )
