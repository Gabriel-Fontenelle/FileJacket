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

from .adapters.image import OpenCVImage, PillowImage, WandImage
# Module with classes adapted from engines
from .adapters.mimetype import LibraryMimeTyper, APIMimeTyper
from .adapters.pipeline import PipelineContent, PipelineOrderedDependency, PipelineSequential, ProcessorContent
from .adapters.storage import WindowsFileSystem, LinuxFileSystem
from .adapters.video import MoviePyVideo
# Module with engines for adapters
from .engines.image import ImageEngine
# A Pipeline is a sequence that loop processors to be run.
from .engines.pipeline import Processor, PipelineEngine
from .engines.serializer import Serializer
from .engines.storage import StorageEngine
from .engines.video import VideoEngine
from .exception import (
    ImproperlyConfiguredFile,
    NoInternalContentError,
    OperationNotAllowed,
    ReservedFilenameError,
    ValidationError,
)
from .file import BaseFile
from .handler import System, URI
# Module with base classes for pipeline classes.
from .pipelines.base import (
    BaseComparer,
    BaseExtractor,
    BaseHasher,
    BasePackager,
    BaseRenamer,
    BaseRender,
)
# Module with pipeline classes for comparing Files.
from .pipelines.comparer import (
    BinaryCompare,
    DataCompare,
    HashCompare,
    LousyNameCompare,
    MimeTypeCompare,
    NameCompare,
    SizeCompare,
    TypeCompare,
)
# Module with pipeline classes for extracting data for files from multiple sources.
from .pipelines.extractor import (
    FileSystemDataExtractor,
    FilenameAndExtensionFromPathExtractor,
    MimeTypeFromFilenameExtractor,
    HashFileExtractor,
    FilenameFromURLExtractor,
    PathFromURLExtractor,
    FilenameFromMetadataExtractor,
    MetadataExtractor,
    AudioMetadataFromContentExtractor,
    ImageMetadataFromContentExtractor,
    MimeTypeFromContentExtractor,
    VideoMetadataFromContentExtractor,
)
# Module with pipeline classes for generating or extracting hashed data related to file.
from .pipelines.hasher import CRC32Hasher, MD5Hasher, SHA256Hasher
# Module wih pipeline classes for packagins files.
from .pipelines.packager import (
    PSDLayersFromPackageExtractor,
    SevenZipCompressedFilesFromPackageExtractor,
    RarCompressedFilesFromPackageExtractor,
    TarCompressedFilesFromPackageExtractor,
    ZipCompressedFilesFromPackageExtractor,
)
# Module with pipeline classes for renaming files.
from .pipelines.renamer import WindowsRenamer, LinuxRenamer, UniqueRenamer
# module with pipeline classes for render content representation.
from .pipelines.render import (
    BaseAnimatedRender,
    BaseStaticRender,
    DocumentFirstPageRender,
    ImageAnimatedRender,
    ImageRender,
    PSDRender,
    StaticAnimatedRender,
    VectorRender,
    VectorSWFRender,
    VideoRender,
)
# Module with classes for serializing/deserializing objects.
from .adapters.serializer import (
    PickleSerializer,
    JSONSerializer,
    FileJsonSerializer,
    FileJsonSerializerReadonly,
    FileDictionarySerializer,
    FileWithContentJsonSerializer,
)

__all__ = [
    "APIMimeTyper",
    "AudioMetadataFromContentExtractor",
    "BaseAnimatedRender",
    "BaseComparer",
    "BaseExtractor",
    "BaseFile",
    "BaseHasher",
    "BasePackager",
    "BaseRenamer",
    "BaseRender",
    "BaseStaticRender",
    "BinaryCompare",
    "CRC32Hasher",
    "ContentFile",
    "DataCompare",
    "DocumentFirstPageRender",
    "File",
    "FileDictionarySerializer",
    "FileJsonSerializer",
    "FileJsonSerializerReadonly",
    "FileSystemDataExtractor",
    "FileWithContentJsonSerializer",
    "FilenameAndExtensionFromPathExtractor",
    "FilenameFromMetadataExtractor",
    "FilenameFromURLExtractor",
    "HashCompare",
    "HashFileExtractor",
    "ImageAnimatedRender",
    "ImageEngine",
    "ImageMetadataFromContentExtractor",
    "ImageRender",
    "ImproperlyConfiguredFile",
    "JSONSerializer",
    "LibraryMimeTyper",
    "LinuxFileSystem",
    "LinuxRenamer",
    "LousyNameCompare",
    "MD5Hasher",
    "MetadataExtractor",
    "MimeTypeCompare",
    "MimeTypeFromContentExtractor",
    "MimeTypeFromFilenameExtractor",
    "MoviePyVideo",
    "NameCompare",
    "NoInternalContentError",
    "OpenCVImage",
    "OperationNotAllowed",
    "PSDRender",
    "PathFromURLExtractor",
    "PickleSerializer",
    "PillowImage",
    "PipelineContent",
    "PipelineEngine",
    "PipelineOrderedDependency",
    "PipelineSequential",
    "Processor",
    "ProcessorContent",
    "RarCompressedFilesFromPackageExtractor",
    "ReservedFilenameError",
    "SHA256Hasher",
    "Serializer",
    "SevenZipCompressedFilesFromPackageExtractor",
    "SizeCompare",
    "StaticAnimatedRender",
    "StorageEngine",
    "StreamFile",
    "System",
    "TypeCompare",
    "URI",
    "UniqueRenamer",
    "ValidationError",
    "VectorRender",
    "VectorSWFRender",
    "VideoEngine",
    "VideoMetadataFromContentExtractor",
    "VideoRender",
    "WandImage",
    "WindowsFileSystem",
    "WindowsRenamer",
    "ZipCompressedFilesFromPackageExtractor",
]


class ContentFile(BaseFile):
    """
    Class to create a file from an in memory content.
    It can load a file already saved as BaseFile allow it, but is recommended to use `File` instead
    because it will have a more complete pipeline for data extraction.
    a new one from memory using `ContentFile`.
    """

    extract_data_pipeline: PipelineEngine = PipelineOrderedDependency(
        "filejacket.pipelines.extractor.FilenameFromMetadataExtractor",
        "filejacket.pipelines.extractor.MimeTypeFromFilenameExtractor",
        "filejacket.pipelines.extractor.MimeTypeFromContentExtractor",
    )
    """
    Pipeline to extract data from multiple sources.
    """


class StreamFile(BaseFile):
    """
    Class to create a file from an HTTP stream that has a header with metadata.
    """

    extract_data_pipeline: PipelineEngine = PipelineOrderedDependency(
        "filejacket.pipelines.extractor.FilenameFromMetadataExtractor",
        "filejacket.pipelines.extractor.FilenameFromURLExtractor",
        "filejacket.pipelines.extractor.MimeTypeFromFilenameExtractor",
        "filejacket.pipelines.extractor.MimeTypeFromContentExtractor",
        "filejacket.pipelines.extractor.MetadataExtractor",
    )
    """
    Pipeline to extract data from multiple sources.
    """


class File(BaseFile):
    """
    Class to create a file from an already saved path in filesystem.
    It can create a new file as BaseFile allow it, but is recommended to create
    a new one from memory using `ContentFile`.
    """

    extract_data_pipeline: PipelineEngine = PipelineOrderedDependency(
        "filejacket.pipelines.extractor.FilenameAndExtensionFromPathExtractor",
        "filejacket.pipelines.extractor.MimeTypeFromFilenameExtractor",
        "filejacket.pipelines.extractor.FileSystemDataExtractor",
        "filejacket.pipelines.extractor.HashFileExtractor",
    )
    """
    Pipeline to extract data from multiple sources.
    """
