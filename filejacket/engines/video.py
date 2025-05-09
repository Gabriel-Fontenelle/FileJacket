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

if TYPE_CHECKING:
    from io import BytesIO

    from .pipelines.extractor.package import PackageExtractor

__all__ = [
    "VideoEngine",
]


class VideoEngine:
    """
    Class that standardized methods of different video manipulators.
    """

    video: Any = None
    """
    Attribute where the current video converted from buffer is stored.
    """
    metadata: dict[str, Any]
    metadata = None
    """
    Attribute where the current video metadata is stored.
    """

    def __init__(self, buffer: BytesIO | PackageExtractor.ContentBuffer) -> None:
        """
        Method to instantiate the current class using a buffer for the image content as a source
        for manipulation by the class to be used.
        """
        self.source_buffer = buffer

        self.prepare_video()

    def get_duration(self) -> int:
        """
        Method to return the duration in seconds of the video.
        This method should be overwritten in child class.
        """
        raise NotImplementedError(
            "The method get_duration should be override in child class."
        )

    def get_frame_rate(self) -> float:
        """
        Method to return the framerate of the video.
        This method should be overwritten in child class.
        """
        raise NotImplementedError(
            "The method get_frame_rate should be override in child class."
        )

    def get_frame_amount(self) -> int:
        """
        Method to return the total amount of frame available in the video.
        """
        return int(self.get_duration() * self.get_frame_rate())

    def get_frame_as_bytes(self, index: int, encode_format: str = "jpeg") -> Any:
        """
        Method to return content of the frame at index as bytes.
        This method should be overwritten in child class.
        """
        raise NotImplementedError(
            "The method get_frame_as_bytes should be override in child class."
        )

    def get_frame_image(self, index: int) -> Any:
        """
        Method to return the array representing the frame at index.
        This method should be overwritten in child class.
        """
        raise NotImplementedError(
            "The method get_frame_image should be override in child class."
        )

    def get_size(self) -> tuple[int, int]:
        """
        Method to return the width and height of the video.
        This method should be overwritten in child class.
        """
        raise NotImplementedError(
            "The method get_size should be override in child class."
        )

    def prepare_video(self) -> None:
        """
        Method to prepare the video using the stored buffer as the source.
        This method should use `self.source_buffer` and `self.video` to set the current video object.
        This method should be overwritten in child class.
        """
        raise NotImplementedError(
            "The method prepare_video should be override in child class."
        )

    def show(self) -> None:
        """
        Method to display the video for debugging purposes.
        This method should be overwritten in child class.
        """
        raise NotImplementedError("The method show should be override in child class.")
