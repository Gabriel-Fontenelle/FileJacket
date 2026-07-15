import pytest

from filejacket.exception import (
    __all__,
    FileJacketException,
    CacheContentNotSeekableError,
    EmptyHashContentError,
    EmptyContentError,
    ImproperlyConfiguredFile,
    ImproperlyConfiguredPipeline,
    MultipleFileExistError,
    NoInternalContentError,
    OperationNotAllowed,
    PipelineError,
    RenderError,
    ReservedFilenameError,
    SerializerError,
    StopPipeline,
    ValidationError
)


@pytest.mark.parametrize(
    "exception_class",
    [
        CacheContentNotSeekableError,
        EmptyContentError,
        EmptyHashContentError,
        ImproperlyConfiguredFile,
        NoInternalContentError,
        MultipleFileExistError,
        ImproperlyConfiguredPipeline,
        OperationNotAllowed,
        PipelineError,
        RenderError,
        ReservedFilenameError,
        SerializerError,
        StopPipeline,
        ValidationError
    ]
)
def test_instance_of_exception(exception_class: Exception):
    assert isinstance(exception_class(), Exception)
    assert isinstance(exception_class(), FileJacketException)


def test_file_exception_all_import():
    assert __all__ == [
        "CacheContentNotSeekableError",
        "EmptyContentError",
        "EmptyHashContentError",
        "ExtractorError",
        "ImproperlyConfiguredFile",
        "ImproperlyConfiguredPipeline",
        "MultipleFileExistError",
        "NoInternalContentError",
        "OperationNotAllowed",
        "PipelineError",
        "RenderError",
        "ReservedFilenameError",
        "SerializerError",
        "StopPipeline",
        "ValidationError",
    ]
