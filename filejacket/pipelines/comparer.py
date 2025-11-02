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

from .base import BaseComparer
from ..exception import StopPipeline

if TYPE_CHECKING:
    from ..file import BaseFile


__all__ = [
    "BinaryCompare",
    "DataCompare",
    "HashCompare",
    "LousyNameCompare",
    "MimeTypeCompare",
    "NameCompare",
    "SizeCompare",
    "TypeCompare",
]


class DataCompare(BaseComparer):
    """
    Class that define comparing of data between two Files for use in Comparer Pipeline.
    """

    @classmethod
    def is_the_same(cls, file_1: BaseFile, file_2: BaseFile) -> bool | None:
        """
        Method used to check if two files are the same.
        This method check byte by byte.
        This method assumes that data has the same size and both has the same value
        to is_binary, thus use it after SizeCompare and BinaryCompare.

        Because the content buffers can have difference in sizes, we should make use
        of an additional buffer to save parts of content to compare. Using the lower size of buffer
        between the two files.

        This method stops the pipeline if the result value is either False or True.
        """

        def compare_buffer():
            """
            Internal function to compare two buffer's data.
            This function will compare the buffer extracting from it the content of same size, usually
            the lowest buffer size between those buffers.
            """
            # Compare same size buffer
            if buffer_1[:buffer_size] != buffer_2[:buffer_size]:
                raise StopIteration()

            # Normalize buffer returning modified buffer (after comparing above)
            return buffer_1[buffer_size:], buffer_2[buffer_size:]

        try:
            # Check if there is a content so we don't compare empty content. It is checked by property content of
            # BaseFile when calling .content
            content_1 = file_1.content_as_iterator
            content_2 = file_2.content_as_iterator

            # Comparing data between binary and string should return False, they are not the same anyway.
            if file_1.is_binary != file_2.is_binary:
                raise StopPipeline(f"Stopper called at {cls.__name__}", False)

            # Check if the iterator being compared is the same, to avoid consuming unequal parts of the same iterator.
            if id(content_1) == id(content_2):
                raise StopPipeline(f"Stopper called at {cls.__name__}", True)

            # Set-up initial data for additional buffer
            value_1: str | bytes | None
            value_2: str | bytes | None
            buffer_1: str | bytes | None
            buffer_2: str | bytes | None

            if file_1.is_binary:
                value_1 = buffer_1 = b""
                value_2 = buffer_2 = b""
            else:
                value_1 = buffer_1 = ""
                value_2 = buffer_2 = ""

            # Normalize buffer size to be the minimum denominator between buffers
            buffer_size = min(file_1._content._block_size, file_2._content._block_size)

        except ValueError:
            return None

        try:
            # Loop through content adding to new buffer to allow comparison between normalized sizes.
            # We should avoid raising StopIteration so we define a default value to return instead.
            while (value_1 := next(content_1, None)) is not None or (value_2 := next(content_2, None)) is not None:
                if value_1 is not None:
                    # Add data to buffer
                    buffer_1 += value_1

                if value_2 is not None:
                    # Add data to buffer
                    buffer_2 += value_2

                if len(buffer_1) >= buffer_size and len(buffer_2) >= buffer_size:
                    # Normalize buffer (after comparing above)
                    # compare_buffer will raise StopIterator case the comparison is False.
                    buffer_1, buffer_2 = compare_buffer()

            # If there is still buffer to verify, check buffer data
            while max(len(buffer_1), len(buffer_2)) >= buffer_size:
                # Normalize buffer (after comparing above)
                # compare_buffer will raise StopIterator case the comparison is False.
                buffer_1, buffer_2 = compare_buffer()

            raise StopPipeline(f"Stopper called at {cls.__name__}", True)

        except StopIteration:
            # Case StopIteration as raised the comparison is false.
            raise StopPipeline(f"Stopper called at {cls.__name__}", False)


class SizeCompare(BaseComparer):
    """
    Class that define comparing of size of content between two Files for use in Comparer Pipeline.
    """

    @classmethod
    def is_the_same(cls, file_1: BaseFile, file_2: BaseFile) -> bool | None:
        """
        Method used to check if two files are the same.
        This method check if the sizes are the same.

        This method stops the pipeline if the result value is False.
        """
        if not len(file_1) or not len(file_2):
            return None

        result = len(file_1) == len(file_2)

        if not result:
            raise StopPipeline(f"Stopper called at {cls.__name__}", result)

        return result


class HashCompare(BaseComparer):
    """
    Class that define comparing of hash between two Files for use in Comparer Pipeline.
    """

    @classmethod
    def is_the_same(cls, file_1: BaseFile, file_2: BaseFile) -> bool | None:
        """
        Method used to check if two files are the same.
        This method check if hashes are the same.

        This method stops the pipeline if the result value is either False or True.
        """
        if not file_1.hashes or not file_2.hashes:
            return None

        intersection = list(filter(
            lambda hash_name: file_1.hashes[hash_name]
                              and file_2.hashes[hash_name],
            set(file_1.hashes.keys()).intersection(set(file_2.hashes.keys()))
        ))

        if not intersection:
            return None

        for hash_name in intersection:
            if file_1.hashes[hash_name] != file_2.hashes[hash_name]:
                raise StopPipeline(f"Stopper called at {cls.__name__}", False)

        raise StopPipeline(f"Stopper called at {cls.__name__}", True)


class LousyNameCompare(BaseComparer):
    """
    Class that define comparing of filename between two Files for use in Comparer Pipeline.
    """

    @classmethod
    def is_the_same(cls, file_1: BaseFile, file_2: BaseFile) -> bool | None:
        """
        Method used to check if two files are the same.
        This method check if the names are lousily the same.

        This method stops the pipeline if the result value is False.
        """
        if not file_1.filename or not file_2.filename:
            return None

        # Compare filenames and extension, but we assume that being the same mime_type it can have different
        # extension if those are valid and registered
        # to mime type.
        extension = True
        if file_1.extension and file_2.extension:
            extension = file_1.mime_type_handler.get_mimetype(
                file_1.extension
            ) == file_2.mime_type_handler.get_mimetype(file_2.extension)

        result = file_1.complete_filename == file_2.complete_filename and extension

        if not result:
            raise StopPipeline(f"Stopper called at {cls.__name__}", result)

        return result


class NameCompare(BaseComparer):
    """
    Class that define comparing of filename between two Files for use in Comparer Pipeline.
    """

    @classmethod
    def is_the_same(cls, file_1: BaseFile, file_2: BaseFile) -> bool | None:
        """
        Method used to check if two files are the same.
        This method check if the complete filename are the same.

        This method stops the pipeline if the result value is False.
        """
        if not file_1.filename or not file_2.filename:
            return None

        result = file_1.complete_filename == file_2.complete_filename

        if not result:
            raise StopPipeline(f"Stopper called at {cls.__name__}", result)

        return result


class MimeTypeCompare(BaseComparer):
    """
    Class that define comparing of mimetype between two Files for use in Comparer Pipeline.
    """

    @classmethod
    def is_the_same(cls, file_1: BaseFile, file_2: BaseFile) -> bool | None:
        """
        Method used to check if two files are the same.
        This method check if the mimetypes are the same.

        This method stops the pipeline if the result value is False.
        """
        if file_1.mime_type is None or file_2.mime_type is None:
            return None

        result = file_1.mime_type == file_2.mime_type

        if not result:
            raise StopPipeline(f"Stopper called at {cls.__name__}", result)

        return result


class BinaryCompare(BaseComparer):
    """
    Class that define comparing of binary attribute between two Files for use in Comparer Pipeline.
    """

    @classmethod
    def is_the_same(cls, file_1: BaseFile, file_2: BaseFile) -> bool | None:
        """
        Method used to check if two files are the same.
        This method check if the attribute binary are the same.

        This method stops the pipeline if the result value is False.
        """
        file_1_is_binary = file_1.is_binary
        file_2_is_binary = file_2.is_binary

        if file_1_is_binary is None or file_2_is_binary is None:
            return None

        result = file_1_is_binary == file_2_is_binary

        if not result:
            raise StopPipeline(f"Stopper called at {cls.__name__}", result)

        return result


class TypeCompare(BaseComparer):
    """
    Class that define comparing of type between two Files for use in Comparer Pipeline.
    """

    @classmethod
    def is_the_same(cls, file_1: BaseFile, file_2: BaseFile) -> bool | None:
        """
        Method used to check if two files are the same.
        This method check if the attribute binary are the same.

        This method stops the pipeline if the result value is False.
        """
        if file_1.type is None or file_2.type is None:
            return None

        return file_1.type == file_2.type
        result = file_1.type == file_2.type

        if not result:
            raise StopPipeline(f"Stopper called at {cls.__name__}", result)

        return result

