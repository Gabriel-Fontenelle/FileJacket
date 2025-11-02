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

from datetime import datetime
from io import BytesIO
from sys import getsizeof
from tarfile import TarFile, TarError
from typing import Any, TYPE_CHECKING, Type, IO, Iterator
from zipfile import BadZipFile, ZipFile

from rarfile import BadRarFile, RarFile, NotRarFile

from .base import BasePackager
from .hasher import CRC32Hasher
from ..utils import LazyImportClass

if TYPE_CHECKING:
    from ..file import BaseFile
    from psd_tools import PSDImage
    from py7zr import SevenZipFile, FileInfo

__all__ = [
    "PSDLayersFromPackageExtractor",
    "SevenZipCompressedFilesFromPackageExtractor",
    "RarCompressedFilesFromPackageExtractor",
    "TarCompressedFilesFromPackageExtractor",
    "ZipCompressedFilesFromPackageExtractor",
]


class MastrokaFilesFromPackageExtractor(BasePackager):
    """
    Class to extract internal files from mka, mkv files.
    """


class PDFPagesFromPackageExtractor(BasePackager):
    """
    Class to extract internal files from PDF files.
    """


class PSDLayersFromPackageExtractor(BasePackager):
    """
    Class to extract internal files from PSD files.
    """

    extensions: set[str] = {"psd", "psb"}
    """
    Attribute to store allowed extensions for use in `validator`.
    """
    compressor_class: Type[PSDImage] = LazyImportClass("PSDImage", "psd_tools")
    """
    Attribute to store the current class of compressor for use in `content_buffer` and `decompress` methods.
    """

    @classmethod
    def content_buffer(
        cls, file_object: BaseFile, internal_file_name: str, mode: str = "rb"
    ) -> BasePackager.ContentBuffer:
        """
        Method to create a buffer pointing to the uncompressed content.
        This method must work lazily, extracting the content only when the buffer is read.
        """

        class PSDContentBuffer(BasePackager.ContentBuffer):
            """
            Class to allow consumption of buffer in a lazy way.
            """

            def mount_buffer(self: BasePackager.ContentBuffer) -> None:
                """
                Method to initiate the buffer object if not exists.
                """
                compressed: IO = self.compressor.open(
                    fp=self.source_file_object.content_as_buffer
                )

                self.buffer: BytesIO = BytesIO()

                # Save PSD content for layer in buffer.
                compressed[self.filename].save(fp=self.buffer)

                # Reset buffer to allow read.
                self.buffer.seek(0)
                
            def seekable(self) -> bool:
                """
                Method to verify if buffer is seekable.
                This method override the default behavior for better performance to avoid extracting the self.filename.
                
                Because the layer must be extracted to an auxiliary buffer it will always be seekable.
                """                
                return True

        return PSDContentBuffer(
            file_object, cls.compressor_class, internal_file_name, mode, cls
        )

    @classmethod
    def decompress(cls, file_object: BaseFile, overrider: bool, **kwargs: Any) -> bool:
        """
        Method to decompress the content from a file_object.
        """
        try:
            # We need to create the directory because there is no extractor for handling PSD.
            extraction_path: str = kwargs.pop("decompress_to")

            # We don't need to reset the buffer before calling it, because it will be reset
            # if already cached. The next time property buffer is called it will reset again.
            compressed_file: PSDImage = cls.compressor_class.open(
                fp=file_object.content_as_buffer
            )

            for index, internal_file in compressed_file:
                filename = f"{index}-{internal_file.name or internal_file.layer_id}.psd"

                path: str = file_object.storage.join(extraction_path, filename)
                if not file_object.storage.exists(path) or overrider:
                    # Create directory if not exists
                    file_object.storage.create_directory(extraction_path)

                    # Save content buffer for file
                    buffer: BytesIO = BytesIO()
                    internal_file.save(fp=buffer)

                    # Reset pointer to initial point.
                    buffer.seek(0)

                    # Save buffer
                    file_object.storage.save_file(
                        path=path, content=buffer, file_mode="w", write_mode="b"
                    )

            # Remove from memory
            del compressed_file

        except (OSError, ValueError):
            return False

        return True

    @classmethod
    def extract(cls, file_object: BaseFile, overrider: bool, **kwargs: Any) -> bool:
        """
        Method to extract the information necessary from a file_object.
        """
        if not file_object.save_to:
            return False

        try:
            # We don't need to reset the buffer before calling it, because it will be reset
            # if already cached. The next time property buffer is called it will reset again.
            for filename, internal_file_object in cls.iterate_internal_files(
                file_object, overrider=overrider, **kwargs
            ):
                # Set the type for internal file.
                internal_file_object.type = "image"

                # Add internal file as File object to file.
                file_object._content_files[filename] = internal_file_object

            # Update metadata and actions.
            file_object.meta.packed = True
            file_object._actions.listed()

        except OSError:
            return False

        return True

    @classmethod
    def extract_as_generator(cls, file_object: BaseFile, overrider: bool, **kwargs: Any) -> Iterator[BaseFile]:
        """
        Method to extract the information necessary from a file_object interactable.
        """
        # We don't need to reset the buffer before calling it, because it will be reset
        # if already cached. The next time property buffer is called it will reset again.
        for filename, internal_file_object in cls.iterate_internal_files(file_object, overrider=overrider, **kwargs):
            # Set the type for internal file.
            internal_file_object.type = "image"

            # Add internal file as File object to file.
            file_object._content_files[filename] = internal_file_object

            yield internal_file_object

        # Update metadata and actions.
        file_object.meta.packed = True
        file_object._actions.listed()

    @classmethod
    def iterate_package(cls, file_object: BaseFile) -> Iterator[tuple]:
        """
        Method to iterate through the buffer to standardize the loop.
        The method should return a tuple with the following values:
            (
                filename,
                uncompressed length,
                create date,
                update date,
                checksum,
                checksum keyword,
                checksum hasher class
            )

        If no information is available for the attribute None should be returned:
            (<filename>, <uncompressed length>, None, None, None, "crc323", CRC32Hasher)
        """
        # We don't need to reset the buffer before calling it, because it will be reset
        # if already cached. The next time property buffer is called it will reset again.
        compressed_object: PSDImage = cls.compressor_class.open(
            fp=file_object.content_as_buffer
        )

        for index, internal_file in enumerate(compressed_object):
            yield (
                # Cast specifically created to fix a mypy error, as internal_file should always have a filename
                f"{index}-{internal_file.name or internal_file.layer_id}.psd",
                getsizeof(internal_file),
                None,
                None,
                None,
                None,
                None
            )

        # Remove from memory
        del compressed_object


class TarCompressedFilesFromPackageExtractor(BasePackager):
    """
    Class to extract internal files from tar.gz or tar.bz files.
    As gzip and bzip compression don`t provide a manifest, as it is not an archive format just a compression algorithm,
    the tarfile library should be used to try to extract information of files with compression .bz and .gz as its the
    most common usage of tar with those compressors.
    """

    extensions: set[str] = {"gz", "tar", "bz", "cbt"}
    """
    Attribute to store allowed extensions for use in `validator`.
    """
    compressor_class: Type[TarFile] = TarFile
    """
    Attribute to store the current class of compressor for use in `content_buffer` and `decompress` methods.
    """

    @classmethod
    def content_buffer(
        cls, file_object: BaseFile, internal_file_name: str, mode: str = "rb"
    ) -> BasePackager.ContentBuffer:
        """
        Method to create a buffer pointing to the uncompressed content.
        This method must work lazily, extracting the content only when the buffer is read.
        """

        class TarContentBuffer(BasePackager.ContentBuffer):
            """
            Class to allow consumption of buffer in a lazy way.
            """

            def mount_compressed_object(self: BasePackager.ContentBuffer) -> None:
                """
                Method to initialize the compressed file from the upstream package buffer.
                """
                # Instantiate the buffer of inner content
                self.compressed_object: TarFile = self.compressor(
                    fileobj=self.source_file_object.content_as_buffer
                )
                
            def mount_buffer(self: BasePackager.ContentBuffer) -> None:
                """
                Method to initiate the buffer object if not exists.
                """
                if not self.compressed_object:
                    self.mount_compressed_object()
                
                content = self.compressed_object.extractfile(member=self.filename)

                if content is None:
                    self.buffer = BytesIO(b"")
                else:
                    self.buffer = content

            def read(self, *args: Any, **kwargs: Any) -> bytes:
                """
                Method to read the content of the object initiating the buffer if not exists.
                """
                if not hasattr(self, "buffer"):
                    # Instantiate the buffer of inner content
                    self.mount_buffer()

                return self.buffer.read(*args, **kwargs)

            def seekable(self) -> bool:
                """
                Method to verify if buffer is seekable.
                This method override the default behavior for better performance to avoid extracting the self.filename.
                """                
                if not self.compressed_object:
                    self.mount_compressed_object()
                
                # The fileobj is the same object as the self.source_file_object.content_as_buffer 
                # used in mount_compressed_object.
                return self.compressed_object.fileobj.seekable()
            
        return TarContentBuffer(
            file_object, cls.compressor_class, internal_file_name, mode, cls
        )

    @classmethod
    def decompress(cls, file_object: BaseFile, overrider: bool, **kwargs: Any) -> bool:
        """
        Method to uncompress the content from a file_object.
        """
        try:
            # We don't need to create the directory because the extractor will create it if not exists.
            extraction_path: str = kwargs.pop("decompress_to")

            # We don't need to reset the buffer before calling it, because it will be reset
            # if already cached. The next time property buffer is called it will reset again.
            with cls.compressor_class(
                fileobj=file_object.content_as_buffer
            ) as compressed_file:  # type: ignore
                # targets as None will extract all data, overwriting existing ones.
                targets: list | None = None

                if not overrider:
                    targets = []
                    for filename in compressed_file.getnames():
                        # Avoid files beginning with `..` or `/` for security reason.
                        if filename[0] == "/" or filename[0:2] == "..":
                            continue

                        if not file_object.storage.exists(
                            file_object.storage.join(extraction_path, filename)
                        ):
                            targets.append(filename)

                    # Avoid calling the extractor if the list is empty.
                    if not targets:
                        return True

                # Concurrent extract file in external file system using a custom pathlib.Path
                # with accessor informed by storage of file_object.
                compressed_file.extractall(
                    path=file_object.storage.get_pathlib_path(extraction_path),
                    members=targets,
                )

        except BadZipFile:
            return False

        return True

    @classmethod
    def extract(cls, file_object: BaseFile, overrider: bool, **kwargs: Any) -> bool:
        """
        Method to extract the information necessary from a file_object.
        """
        if not file_object.save_to:
            return False

        try:
            # We don't need to reset the buffer before calling it, because it will be reset
            # if already cached. The next time property buffer is called it will reset again.
            for filename, internal_file_object in cls.iterate_internal_files(
                file_object, overrider=overrider, **kwargs
            ):
                # Add internal file as File object to file.
                file_object._content_files[filename] = internal_file_object

            # Update metadata and actions.
            file_object.meta.packed = True
            file_object._actions.listed()

        except TarError:
            return False

        return True

    @classmethod
    def iterate_package(cls, file_object: BaseFile) -> Iterator[tuple]:
        """

        Method to iterate through the buffer to standardize the loop.
        The method should return a tuple with the following values:
            (
                filename,
                uncompressed length,
                create date,
                update date,
                checksum,
                checksum keyword,
                checksum hasher class
            )

        If no information is available for the attribute None should be returned:
            (<filename>, <uncompressed length>, None, None, None, "crc323", CRC32Hasher)
        """
        # We don't need to reset the buffer before calling it, because it will be reset
        # if already cached. The next time property buffer is called it will reset again.
        with cls.compressor_class(file=file_object.content_as_buffer) as compressed_object:
            for internal_file in compressed_object.getmembers():
                # Skip directories
                if internal_file.isdir():
                    continue

                # Skip unexisting filename if for some reason there is one.
                if not internal_file.name:
                    continue

                create_date = datetime.fromtimestamp(
                    internal_file.mtime
                )
                yield (
                    # Cast specifically created to fix a mypy error, as internal_file should always have a filename
                    str(internal_file.name),
                    internal_file.size,
                    create_date,
                    create_date,
                    str(internal_file.chksum),
                    "crc32",
                    CRC32Hasher
                )


class ZipCompressedFilesFromPackageExtractor(BasePackager):
    """
    Class to extract internal files from zip and cbz files.
    """

    extensions: set[str] = {"zip", "cbz"}
    """
    Attribute to store allowed extensions for use in `validator`.
    """
    compressor_class: Type[ZipFile] = ZipFile
    """
    Attribute to store the current class of compressor for use in `content_buffer` and `decompress` methods.
    """

    @classmethod
    def content_buffer(cls, file_object, internal_file_name, mode="rb"):
        """
        Method to create a buffer pointing to the uncompressed content.
        This method must work lazily, extracting the content only when the buffer is read.
        """

        class ZipContentBuffer(cls.ContentBuffer):
            """
            Class to allow consumption of buffer in a lazy way.
            """

            def mount_compressed_object(self: BasePackager.ContentBuffer) -> None:
                """
                Method to initialize the compressed file from the upstream package buffer.
                """
                # Instantiate the buffer of inner content
                self.compressed_object: ZipFile = self.compressor(
                    file=self.source_file_object.content_as_buffer
                )
                
            def mount_buffer(self: BasePackager.ContentBuffer) -> None:
                """
                Method to initiate the buffer object if not exists.
                """
                if not self.compressed_object:
                    self.mount_compressed_object()

                self.buffer = self.compressed_object.open(name=self.filename)
                
            def seekable(self) -> bool:
                """
                Method to verify if buffer is seekable.
                This method override the default behavior for better performance to avoid extracting the self.filename.
                """                
                if not self.compressed_object:
                    self.mount_compressed_object()
                
                return self.compressed_object._seekable

        return ZipContentBuffer(
            file_object, cls.compressor_class, internal_file_name, mode, cls
        )

    @classmethod
    def decompress(cls, file_object: BaseFile, overrider: bool, **kwargs: Any) -> bool:
        """
        Method to uncompress the content from a file_object.
        """
        try:
            # We don't need to create the directory because the extractor will create it if not exists.
            extraction_path: str = kwargs.pop("decompress_to")

            # We don't need to reset the buffer before calling it, because it will be reset
            # if already cached. The next time property buffer is called it will reset again.
            with cls.compressor_class(
                file=file_object.content_as_buffer
            ) as compressed_file:  # type: ignore
                # targets as None will extract all data, overwriting existing ones.
                targets: list | None = None

                if not overrider:
                    targets = []
                    for filename in compressed_file.namelist():
                        # Avoid files beginning with `..` or `/` for security reason.
                        if filename[0] == "/" or filename[0:2] == "..":
                            continue

                        if not file_object.storage.exists(
                            file_object.storage.join(extraction_path, filename)
                        ):
                            targets.append(filename)

                    # Avoid calling the extractor if the list is empty.
                    if not targets:
                        return True

                # Concurrent extract file in external file system using a custom pathlib.Path
                # with accessor informed by storage of file_object.
                compressed_file.extractall(
                    path=file_object.storage.get_pathlib_path(extraction_path),
                    members=targets,
                )

        except BadZipFile:
            return False

        return True

    @classmethod
    def extract(cls, file_object: BaseFile, overrider: bool, **kwargs: Any) -> bool:
        """
        Method to extract the information necessary from a file_object.
        """
        if not file_object.save_to:
            return False

        try:
            # We don't need to reset the buffer before calling it, because it will be reset
            # if already cached. The next time property buffer is called it will reset again.
            for filename, internal_file_object in cls.iterate_internal_files(
                file_object, overrider=overrider, **kwargs
            ):
                # Add internal file as File object to file.
                file_object._content_files[filename] = internal_file_object

            # Update metadata and actions.
            file_object.meta.packed = True
            file_object._actions.listed()

        except BadZipFile:
            return False

        return True

    @classmethod
    def iterate_package(cls, file_object: BaseFile) -> Iterator[tuple]:
        """
        Method to iterate through the buffer to standardize the loop.
        The method should return a tuple with the following values:
            (
                filename,
                uncompressed length,
                create date,
                update date,
                checksum,
                checksum keyword,
                checksum hasher class
            )

        If no information is available for the attribute None should be returned:
            (<filename>, <uncompressed length>, None, None, None, "crc323", CRC32Hasher)
        """
        # We don't need to reset the buffer before calling it, because it will be reset
        # if already cached. The next time property buffer is called it will reset again.
        with cls.compressor_class(file=file_object.content_as_buffer) as compressed_object:
            for internal_file in compressed_object.infolist():
                # Skip directories and symbolic link
                if internal_file.is_dir():
                    continue

                # Skip unexisting filename if for some reason there is one.
                if not internal_file.filename:
                    continue

                # Update creation and modified date. Zip don't store the created date, only the modified one.
                # To avoid problem the created date will be considered the same as modified.
                create_date = datetime(* internal_file.date_time)

                yield (
                    # Cast specifically created to fix a mypy error, as internal_file should always have a filename
                    str(internal_file.filename),
                    internal_file.file_size,
                    create_date,
                    create_date,
                    str(internal_file.CRC),
                    "crc32",
                    CRC32Hasher
                )


class RarCompressedFilesFromPackageExtractor(BasePackager):
    """
    Class to extract internal files from rar files.
    """

    extensions: set[str] = {"rar", "cbr"}
    """
    Attribute to store allowed extensions for use in `validator`.
    """
    compressor_class: Type[RarFile] = RarFile
    """
    Attribute to store the current class of compressor for use in `content_buffer` and `decompress` methods.
    """

    @classmethod
    def content_buffer(
        cls, file_object: BaseFile, internal_file_name: str, mode: str = "rb"
    ) -> BasePackager.ContentBuffer:
        """
        Method to create a buffer pointing to the uncompressed content.
        This method must work lazily, extracting the content only when the buffer is read.
        """

        class RarContentBuffer(cls.ContentBuffer):
            """
            Class to allow consumption of buffer in a lazy way.
            """

            def mount_compressed_object(self: BasePackager.ContentBuffer) -> None:
                """
                Method to initialize the compressed file from the upstream package buffer.
                """
                # Instantiate the buffer of inner content
                self.compressed_object: RarFile = self.compressor(
                    file=self.source_file_object.content_as_buffer
                )
                
            def mount_buffer(self: BasePackager.ContentBuffer) -> None:
                """
                Method to initiate the buffer object if not exists.
                """
                if not self.compressed_object:
                    self.mount_compressed_object()
                
                self.buffer = self.compressed_object.open(name=self.filename)
                
            def seekable(self) -> bool:
                """
                Method to verify if buffer is seekable.
                This method override the default behavior for better performance to avoid extracting the self.filename.
                """                
                if not self.compressed_object:
                    self.mount_compressed_object()

                # `_rarfile` is the same as the `self.source_file_object.content_as_buffer`
                return self.compressed_object._rarfile.seekable()

        return RarContentBuffer(
            file_object, cls.compressor_class, internal_file_name, mode, cls
        )

    @classmethod
    def decompress(cls, file_object: BaseFile, overrider: bool, **kwargs: Any) -> bool:
        """
        Method to uncompressed the content from a file_object.
        """
        try:
            # We don't need to create the directory because the extractor will create it if not exists.
            extraction_path: str = kwargs.pop("decompress_to")

            # We don't need to reset the buffer before calling it, because it will be reset
            # if already cached. The next time property buffer is called it will reset again.
            with cls.compressor_class(
                file=file_object.content_as_buffer
            ) as compressed_file:
                # targets as None will extract all data, overwriting existing ones.
                targets: list[str] | None = None

                if not overrider:
                    targets = []
                    for filename in compressed_file.namelist():
                        # Avoid files beginning with `..` or `/` for security reason.
                        if filename[0] == "/" or filename[0:2] == "..":
                            continue

                        if not file_object.storage.exists(
                            file_object.storage.join(extraction_path, filename)
                        ):
                            targets.append(filename)

                    # Avoid calling the extractor if the list is empty.
                    if not targets:
                        return True

                # Concurrent extract file in external file system using a custom pathlib.Path
                # with accessor informed by storage of file_object.
                compressed_file.extractall(
                    path=file_object.storage.get_pathlib_path(extraction_path),
                    members=targets,
                )

        except (BadRarFile, NotRarFile):
            return False

        return True

    @classmethod
    def extract(cls, file_object: BaseFile, overrider: bool, **kwargs: Any) -> bool:
        """
        Method to extract the information necessary from a file_object.
        """

        if not file_object.save_to:
            return False

        try:
            # We don't need to reset the buffer before calling it, because it will be reset
            # if already cached. The next time property buffer is called it will reset again.
            for filename, internal_file_object in cls.iterate_internal_files(
                file_object, overrider=overrider, **kwargs
            ):
                # Add internal file as File object to file.
                file_object._content_files[filename] = internal_file_object

            # Update metadata and actions.
            file_object.meta.packed = True
            file_object._actions.listed()

        except (BadRarFile, NotRarFile):
            return False

        return True

    @classmethod
    def iterate_package(cls, file_object: BaseFile) -> Iterator[tuple]:
        """
        Method to iterate through the buffer to standardize the loop.
        The method should return a tuple with the following values:
            (
                filename,
                uncompressed length,
                create date,
                update date,
                checksum,
                checksum keyword,
                checksum hasher class
            )

        If no information is available for the attribute None should be returned:
            (<filename>, <uncompressed length>, None, None, None, "crc323", CRC32Hasher)
        """
        # We don't need to reset the buffer before calling it, because it will be reset
        # if already cached. The next time property buffer is called it will reset again.
        with cls.compressor_class(file=file_object.content_as_buffer) as compressed_object:
            for internal_file in compressed_object.infolist():
                # Skip directories and symbolic link
                if internal_file.is_dir() or internal_file.is_symlink():
                    continue

                # Skip unexisting filename if for some reason there is one.
                if not internal_file.filename:
                    continue

                yield (
                    # Cast specifically created to fix a mypy error, as internal_file should always have a filename
                    str(internal_file.filename),
                    internal_file.file_size,
                    internal_file.ctime,
                    internal_file.mtime,
                    str(internal_file.CRC),
                    "crc32",
                    CRC32Hasher
                )


class SevenZipCompressedFilesFromPackageExtractor(BasePackager):
    """
    Class to extract internal files from 7z files.
    """

    extensions: set[str] = {"7z", "cb7"}
    """
    Attribute to store allowed extensions for use in `validator`.
    """
    compressor_class: Type[SevenZipFile] = LazyImportClass(
        "SevenZipFile", from_module="py7zr"
    )
    """
    Attribute to store the current class of compressor for use in `content_buffer` and `decompress` methods.
    """

    @classmethod
    def content_buffer(
        cls, file_object: BaseFile, internal_file_name: str, mode: str = "rb"
    ) -> BasePackager.ContentBuffer:
        """
        Method to create a buffer pointing to the uncompressed content.
        This method must work lazily, extracting the content only when the buffer is read.
        """

        class SevenZipContentBuffer(BasePackager.ContentBuffer):
            """
            Class to allow consumption of buffer in a lazy way.
            """

            def mount_compressed_object(self: BasePackager.ContentBuffer) -> None:
                """
                Method to initialize the compressed file from the upstream package buffer.
                """
                # Instantiate the buffer of inner content
                self.compressed_object: SevenZipFile = self.compressor(
                    file=self.source_file_object.content_as_buffer
                )  # type: ignore
            
            def mount_buffer(self: BasePackager.ContentBuffer) -> None:
                """
                Method to initiate the buffer object if not exists.
                """
                if not self.compressed_object:
                    self.mount_compressed_object()

                # Case the packed file don't have content it will return None
                content = self.compressed_object.read(targets=[self.filename])

                if content is None:
                    self.buffer = BytesIO(b"")
                else:
                    self.buffer = next(iter(content.values()))
                    
            def seekable(self) -> bool:
                """
                Method to verify if buffer is seekable.
                This method override the default behavior for better performance to avoid extracting the self.filename.
                """                
                if not self.compressed_object:
                    self.mount_compressed_object()
                    
                return self.compressed_object.fp.seekable()

        return SevenZipContentBuffer(
            file_object, cls.compressor_class, internal_file_name, mode, cls
        )

    @classmethod
    def decompress(cls, file_object: BaseFile, overrider: bool, **kwargs: Any) -> bool:
        """
        Method to uncompressed the content from a file_object.
        """
        from py7zr.exceptions import Bad7zFile

        try:
            # We don't need to create the directory because the extractor will create it if not exists.
            extraction_path: str = kwargs.pop("decompress_to")

            # We don't need to reset the buffer before calling it, because it will be reset
            # if already cached. The next time property buffer is called it will reset again.
            with cls.compressor_class(
                file=file_object.content_as_buffer
            ) as compressed_file:  # type: ignore
                # targets as None will extract all data, overwriting existing ones.
                targets: list[str] | None = None

                if not overrider:
                    targets = []
                    for filename in compressed_file.getnames():
                        # Avoid files beginning with `..` or `/` for security reason.
                        if filename[0] == "/" or filename[0:2] == "..":
                            continue

                        if not file_object.storage.exists(
                            file_object.storage.join(extraction_path, filename)
                        ):
                            targets.append(filename)

                    # Avoid calling the extractor if the list is empty.
                    if not targets:
                        return True

                # Concurrent extract file in external file system using a custom pathlib.Path
                # with accessor informed by storage of file_object.
                compressed_file.extract(
                    path=file_object.storage.get_pathlib_path(extraction_path),
                    targets=targets,
                )

        except Bad7zFile:
            return False

        return True

    @classmethod
    def extract(cls, file_object: BaseFile, overrider: bool, **kwargs: Any) -> bool:
        """
        Method to extract the information necessary from a file_object.
        """
        if not file_object.save_to:
            return False

        from py7zr.exceptions import Bad7zFile

        try:
            # We don't need to reset the buffer before calling it, because it will be reset
            # if already cached. The next time property buffer is called it will reset again.
            for filename, internal_file_object in cls.iterate_internal_files(file_object, overrider=overrider, **kwargs):
                # Add internal file as File object to file.
                file_object._content_files[filename] = internal_file_object

            # Update metadata and actions.
            file_object.meta.packed = True
            file_object._actions.listed()

        except Bad7zFile:
            return False

        return True

    @classmethod
    def iterate_package(cls, file_object: BaseFile) -> Iterator[tuple]:
        """
        Method to iterate through the buffer to standardize the loop.
        The method should return a tuple with the following values:
            (
                filename,
                uncompressed length,
                create date,
                update date,
                checksum,
                checksum hasher class
            )

        If no information is available for the attribute None should be returned:
            (filename, uncompressed length, None, None, None, None)
        """

        # We don't need to reset the buffer before calling it, because it will be reset
        # if already cached. The next time property buffer is called it will reset again.
        with cls.compressor_class(file=file_object.content_as_buffer) as compressed_object:  # type: ignore
            compressed_object: FileInfo

            for internal_file in compressed_object.list():
                # Skip directories
                if internal_file.is_directory:
                    continue

                # Skip inexistent filename if for some reason there is one.
                if not internal_file.filename:
                    continue

                yield (
                    # Cast specifically created to fix a mypy error, as internal_file should always have a filename
                    str(internal_file.filename),
                    internal_file.uncompressed,
                    internal_file.creationtime,
                    internal_file.creationtime,
                    internal_file.crc32,
                    "crc32",
                    CRC32Hasher
                )
