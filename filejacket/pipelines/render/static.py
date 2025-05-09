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

from io import BytesIO, StringIO
from typing import Any, TYPE_CHECKING, Type

from .. import Pipeline
from ..base import BaseRender
from ...exception import RenderError

if TYPE_CHECKING:
    from ...file import BaseFile
    from ...file.thumbnail import ThumbnailDefaults
    from ...engines.image import ImageEngine
    from ...engines.video import VideoEngine


__all__ = [
    "DocumentFirstPageRender",
    "ImageRender",
    "PSDRender",
    "BaseStaticRender",
    "VideoRender",
]


class BaseStaticRender(BaseRender):
    """
    Render class with focus to processing information from file's content to create a static representation of it.
    """

    @classmethod
    def create_file(
        cls, object_to_process: BaseFile, content: str | bytes | BytesIO | StringIO
    ) -> BaseFile:
        """
        Method to create a file structured for the static image on same class as object_to_process.
        """
        defaults: Type[ThumbnailDefaults] = object_to_process._thumbnail.static_defaults

        # Create file object for image, change filename from parent to use
        # the new format as base for extension.
        static_file: BaseFile = object_to_process.__class__(
            path=f"{object_to_process.sanitize_path}.{defaults.format_extension}",
            extract_data_pipeline=Pipeline(
                "filejacket.pipelines.extractor.FilenameAndExtensionFromPathExtractor",
                "filejacket.pipelines.extractor.MimeTypeFromFilenameExtractor",
            ),
            file_system_handler=object_to_process.storage,
        )

        # Set content from buffer.
        if isinstance(content, (BytesIO, StringIO)):
            static_file.content_as_buffer = content
        else:
            static_file.content = content

        # Set metadata for file object of thumbnail.
        static_file.meta.thumbnail = True

        return static_file


class DocumentFirstPageRender(BaseStaticRender):
    """
    Render class for processing information from file's content focusing in rendering the representation of the first
    page of document.
    """

    extensions: set[str] = {"pdf", "epub", "fb2", "xps", "oxps"}
    """
    Attribute to store allowed extensions for use in `validator`.
    """

    @classmethod
    def render(cls, file_object: BaseFile, **kwargs: Any) -> None:
        """
        Method to render the image representation of the file_object.
        This method will only use the first page of the documents.
        """
        image_engine: Type[ImageEngine] = kwargs.pop("image_engine")

        defaults: Type[ThumbnailDefaults] = file_object._thumbnail.static_defaults

        buffer_content = file_object.content_as_buffer

        if not buffer_content:
            raise RenderError(
                "There is no content in buffer format available to render."
            )

        buffer: BytesIO = BytesIO()

        # Local import to avoid longer time to load FileJacket library.
        import fitz

        # We use fitz from PyMuPDF to open the document.
        # Because BufferedReader (default return for file_system.open) is not accept
        # we need to consume to get its bytes as bytes are accepted as stream.
        doc: fitz.mupdf.FzDocument = fitz.open(
            stream=buffer_content.read(),
            filetype=file_object.extension,
            # width and height are only used for content that requires rendering of vectors as `epub`.
            width=defaults.width * 5,
            height=defaults.height * 5,
        )
        for page in doc:
            bitmap = page.get_pixmap(dpi=defaults.format_dpi)
            # Save the image in buffer with Pillow.
            bitmap.pil_save(fp=buffer, format=defaults.format)
            buffer.seek(0)
            break

        # Resize image using the image_engine and default values.
        image: ImageEngine = image_engine(buffer=buffer)

        # Trim white space originated from epub.
        image.trim(color=defaults.color_to_trim)

        # Resize
        image.resize(defaults.width, defaults.height, keep_ratio=defaults.keep_ratio)

        # Set static file for current file_object.
        file_object._thumbnail._static_file = cls.create_file(
            file_object, content=image.get_buffer(encode_format=defaults.format)
        )


class ImageRender(BaseStaticRender):
    """
    Render class for processing information from file's content focusing in rendering the whole image.
    """

    extensions: set[str] = {"jpeg", "jpg", "png", "gif", "bmp", "tiff", "tif", "webp"}
    """
    Attribute to store allowed extensions for use in `validator`.
    """

    @classmethod
    def render(cls, file_object: BaseFile, **kwargs: Any) -> None:
        """
        Method to render the image representation of the file_object.
        """
        image_engine: Type[ImageEngine] = kwargs.pop("image_engine")

        defaults: Type[ThumbnailDefaults] = file_object._thumbnail.static_defaults

        buffer_content = file_object.content_as_buffer

        if not buffer_content:
            raise RenderError(
                "There is no content in buffer format available to render."
            )

        # Resize image using the image_engine and default values.
        image: ImageEngine = image_engine(buffer=buffer_content)

        image.resize(defaults.width, defaults.height, keep_ratio=defaults.keep_ratio)

        # Set static file for current file_object.
        file_object._thumbnail._static_file = cls.create_file(
            file_object, content=image.get_buffer(encode_format=defaults.format)
        )


class PSDRender(BaseStaticRender):
    """
    Render class for processing information from file's content focusing in rendering the whole PSD image.
    """

    extensions: set[str] = {"psd", "psb"}
    """
    Attribute to store allowed extensions for use in `validator`.
    """

    @classmethod
    def render(cls, file_object: BaseFile, **kwargs: Any) -> None:
        """
        Method to render the image representation of the file_object.
        """
        image_engine: Type[ImageEngine] = kwargs.pop("image_engine")

        defaults: Type[ThumbnailDefaults] = file_object._thumbnail.static_defaults

        buffer_content = file_object.content_as_buffer

        if not buffer_content:
            raise RenderError(
                "There is no content in buffer format available to render."
            )

        # Local import to avoid longer time to load FileJacket library.
        from psd_tools import PSDImage

        # Load PSD from buffer
        psd: PSDImage = PSDImage.open(fp=buffer_content)

        # Compose image from PSD visible layers and
        # convert it to RGB to remove alpha channel before saving it to buffer.
        buffer: BytesIO = BytesIO()
        psd.composite().convert(mode="RGB").save(fp=buffer, format=defaults.format)

        # Reset buffer to beginning before being loaded in image_engine.
        buffer.seek(0)

        image: ImageEngine = image_engine(buffer=buffer)

        image.resize(defaults.width, defaults.height, keep_ratio=defaults.keep_ratio)

        # Set static file for current file_object.
        file_object._thumbnail._static_file = cls.create_file(
            file_object, content=image.get_buffer(encode_format=defaults.format)
        )


class VideoRender(BaseStaticRender):
    """
    Render class for processing information from file's content focusing in rendering the few first seconds of the
    video.
    """

    extensions: set[str] = {
        "avi",
        "mkv",
        "mpg",
        "mpeg",
        "mp4",
        "flv",
        "wmv",
        "3gp",
        "m2ts",
    }
    """
    Attribute to store allowed extensions for use in `validator`.
    """

    @classmethod
    def render(cls, file_object: BaseFile, **kwargs: Any) -> None:
        """
        Method to render the image representation of the file_object.
        This method will get the frame in 20% of the video.
        """
        image_engine: Type[ImageEngine] = kwargs.pop("image_engine")
        video_engine: Type[VideoEngine] = kwargs.pop("video_engine")

        defaults: Type[ThumbnailDefaults] = file_object._thumbnail.static_defaults

        video: VideoEngine = video_engine(buffer=file_object.content_as_buffer)

        frame_to_select: int = video.get_frame_amount() * 20 // 100

        image: ImageEngine = image_engine(
            buffer=BytesIO(
                video.get_frame_as_bytes(
                    index=frame_to_select, encode_format=defaults.format
                )
            )
        )

        image.resize(defaults.width, defaults.height, keep_ratio=defaults.keep_ratio)

        # Set static file for current file_object.
        file_object._thumbnail._static_file = cls.create_file(
            file_object, content=image.get_buffer(encode_format=defaults.format)
        )
