from __future__ import annotations

import json
import os
from importlib import import_module

import pytest

from typing import TYPE_CHECKING

from ..data import DATA_DIR
from ..data.serializations import DATA_DIR as SERIALIZATION_DATA_DIR
from filejacket import (
    BaseFile,
    File,
    PipelineContent,
)
from filejacket.file import (
    FileContent,
    FileHashes,
    FileNaming,
    FilePacket,
    FileThumbnail,
    FileActions,
    FileMetadata,
    FileState,
    FileOption,
)

if TYPE_CHECKING:
    from filejacket import PipelineEngine, Serializer


@pytest.fixture
def pipeline() -> PipelineEngine:
    return PipelineContent(
         ("filejacket.pipelines.hasher.XXHASH128Hasher", {"full_check": True, "full_loop_check": True}),
         ("filejacket.pipelines.hasher.MD5Hasher", {"full_check": True, "full_loop_check": True}),
         ("filejacket.pipelines.hasher.SHA256Hasher", {"full_check": True, "full_loop_check": True}),
    )


@pytest.mark.parametrize(
    "file_class",
    [
        File,
    ]
)
def test_file_deserialize_json_version_1(
    file_class: type[BaseFile],
    pipeline: PipelineEngine
):
    version = "v1"
    for filename in filter(
        lambda x:
        not os.path.isdir(f"{SERIALIZATION_DATA_DIR}/{x}") and x[:3] == f"{version}_" and x.rsplit('.', 1)[-1] == "json",
        os.listdir(SERIALIZATION_DATA_DIR)
    ):
        parts = filename.split("__")
        resources = parts[3].split("_and_")
        serializer = parts[1]
        folder = parts[4]
        file = parts[5].rsplit(".", 1)[0]

        with open(f"{SERIALIZATION_DATA_DIR}/{filename}", mode='r') as fp:
            content = fp.read()
            content = content.replace('..', f"{DATA_DIR}/{folder}")

        dict_content = json.loads(content)

        serializer_class = getattr(import_module("filejacket"), serializer)

        file_class.serializer = serializer_class
        file_class.hasher_pipeline = pipeline
        file_object = file_class.deserialize(source=content)

        assert isinstance(file_object, BaseFile)

        assert file_object._content is not None
        assert file_object._actions is not None
        assert file_object._state is not None
        assert file_object.meta is not None
        assert file_object._content_files is not None
        assert file_object.hashes is not None
        assert file_object._naming is not None
        assert file_object._thumbnail is not None
        assert file_object._option is not None

        assert isinstance(file_object._content, FileContent)
        assert isinstance(file_object._actions, FileActions)
        assert isinstance(file_object._state, FileState)
        assert isinstance(file_object.meta, FileMetadata)
        assert isinstance(file_object._content_files, FilePacket)
        assert isinstance(file_object.hashes, FileHashes)
        assert isinstance(file_object._naming, FileNaming)
        assert isinstance(file_object._thumbnail, FileThumbnail)
        assert isinstance(file_object._option, FileOption)

        assert file_object.filename
        assert file_object.extension
        assert file_object.length

        if "thumbnail" in resources:
            if dict_content["_thumbnail"]["static_file"]:
                assert file_object._thumbnail._static_file

        if "meta" in resources:
            assert file_object.meta.extra_data

        if "internal_content" in resources:
            assert file_object._content_files is not None
            if dict_content["_content_files"]["internal_files"] and "Readonly" not in serializer:
                assert file_object._content_files.length
                assert file_object._content_files._internal_files

        if "hash" in resources:
            assert bool(file_object.hashes)
