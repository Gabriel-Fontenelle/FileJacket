import json
import pytest

from filejacket import File, FileJsonSerializer, PipelineSequential, PipelineEngine
from ..data.packets import DATA_DIR as PACKET_DATA_DIR
from ..data.images import DATA_DIR as IMAGE_DATA_DIR
from ..data.videos import DATA_DIR as VIDEO_DATA_DIR
from ..data.serializations import DATA_DIR as SERIALIZATION_DATA_DIR


@pytest.mark.parametrize(
    "filename",
    [
        "images.rar",
        "images.cbz",
        "images.tar",
        "images.zip",
        "3763816_76417.psd",
    ]
)
def test_file_json_serialization_for_packet_files_should_return_json(filename: str):
    File.serializer = FileJsonSerializer
    file_object = File(path=f"{PACKET_DATA_DIR}/{filename}", pipelines_override_kwargs=[
        ({"full_loop_check": True}, 'hasher_pipeline')
    ])

    file_object.id = "1"
    file_object._thumbnail.static_defaults.height = 562
    file_object._thumbnail.static_defaults.width = 375
    file_object._option.pipeline_raises_exception = False
    file_object._content.__class__._block_size = 102400
    file_object._content._block_size = 102400

    with open(
        f"{SERIALIZATION_DATA_DIR}/test_file_json_serialization_for_packet_files_should_return_json__{filename}.txt",
        mode="r"
    ) as fp:
        expected_serialization = fp.read()

    # Due to the order of keys in serialization being non-deterministic we need to convert
    # again to dict to compare the results.
    assert json.loads(file_object.serialize()) == json.loads(expected_serialization)
    assert not list(file_object.pipelines_errors)


@pytest.mark.parametrize(
    "filename",
    [
        "images.rar",
        "images.cbz",
        "images.tar",
        "images.zip",
        "3763816_76417.psd"
    ]
)
def test_file_json_serialization_with_internal_content_for_packet_files_should_return_json(filename: str):
    File.serializer = FileJsonSerializer
    file_object = File(path=f"{PACKET_DATA_DIR}/{filename}", pipelines_override_kwargs=[
        ({"full_loop_check": True}, 'hasher_pipeline')
    ])

    file_object.id = "1"
    file_object._thumbnail.static_defaults.height = 562
    file_object._thumbnail.static_defaults.width = 375
    file_object._option.pipeline_raises_exception = False
    file_object._content.__class__._block_size = 102400
    file_object._content._block_size = 102400

    # Generate the list of internal files
    file_object.files()

    with open(
        f"{SERIALIZATION_DATA_DIR}/test_file_json_serialization_with_internal_"
        f"content_for_packet_files_should_return_json__{filename}.txt",
    ) as fp:
        expected_serialization = fp.read()

    # Due to the order of keys in serialization being non-deterministic we need to convert
    # again to dict to compare the results.
    assert json.loads(file_object.serialize()) == json.loads(expected_serialization)
    assert not list(file_object.pipelines_errors)


@pytest.mark.parametrize(
    "filename",
    [
        "images.rar",
        "images.cbz",
        "images.tar",
        "images.zip",
        "3763816_76417.psd",
    ]
)
def test_file_json_serialization_with_internal_content_and_additional_extractors_for_packet_files_should_return_json(
    filename: str
):
    File.serializer = FileJsonSerializer
    file_object = File(path=f"{PACKET_DATA_DIR}/{filename}", pipelines_override_kwargs=[
        ({"full_loop_check": True}, 'hasher_pipeline')
    ])

    file_object.id = "1"
    file_object._thumbnail.static_defaults.height = 562
    file_object._thumbnail.static_defaults.width = 375
    file_object._option.pipeline_raises_exception = False
    file_object._content.__class__._block_size = 102400
    file_object._content._block_size = 102400

    file_object._content_files.unpack_data_pipeline: PipelineEngine = PipelineSequential(
        "filejacket.pipelines.packager.PSDLayersFromPackageExtractor",
        "filejacket.pipelines.packager.SevenZipCompressedFilesFromPackageExtractor",
        "filejacket.pipelines.packager.RarCompressedFilesFromPackageExtractor",
        "filejacket.pipelines.packager.TarCompressedFilesFromPackageExtractor",
        "filejacket.pipelines.packager.ZipCompressedFilesFromPackageExtractor",
    )

    # Generate the list of internal files
    file_object.files()

    with open(
        f"{SERIALIZATION_DATA_DIR}/test_file_json_serialization_with_internal_content_and_additional_extractors_"
        f"for_packet_files_should_return_json__{filename}.txt"
    ) as fp:
        expected_serialization = fp.read()

    # Due to the order of keys in serialization being non-deterministic we need to convert
    # again to dict to compare the results.
    assert json.loads(file_object.serialize()) == json.loads(expected_serialization)
    assert not list(file_object.pipelines_errors)


@pytest.mark.parametrize(
    "filename",
    [
        "images.rar",
        "images.cbz",
        "images.tar",
        "images.zip",
        "3763816_76417.psd",
    ]
)
def test_file_json_serialization_with_thumbnail_for_packet_files_should_return_json(filename: str):
    File.serializer = FileJsonSerializer
    file_object = File(path=f"{PACKET_DATA_DIR}/{filename}", pipelines_override_kwargs=[
        ({"full_loop_check": True}, 'hasher_pipeline')
    ])

    file_object.id = "1"
    file_object._thumbnail.static_defaults.height = 562
    file_object._thumbnail.static_defaults.width = 375
    file_object._option.pipeline_raises_exception = False
    file_object._content.__class__._block_size = 102400
    file_object._content._block_size = 102400

    # Generate the thumbnail for the file
    file_object.thumbnail

    with open(
        f"{SERIALIZATION_DATA_DIR}/test_file_json_serialization_with_thumbnail_for_packet_files_should_return_json"
        f"__{filename}.txt"
    ) as fp:
        expected_serialization = fp.read()

    # Due to the order of keys in serialization being non-deterministic we need to convert
    # again to dict to compare the results.
    assert json.loads(file_object.serialize()) == json.loads(expected_serialization)
    assert not list(file_object.pipelines_errors)


@pytest.mark.parametrize(
    "filename",
    [
        "aurora-1197753_1280_by_Noel_Bauza_at_pixabay.jpg",
        "snow-man-10450_by_winterflower_at_pixabay.gif",
        "snow-man-10450_by_winterflower_at_pixabay.png",
        "watermelon-8368960_by_ebengg_at_pixabay.svg",
    ]
)
def test_file_json_serialization_with_thumbnail_with_type_image_should_return_json(filename: str):
    File.serializer = FileJsonSerializer
    file_object = File(path=f"{IMAGE_DATA_DIR}/{filename}", pipelines_override_kwargs=[
        ({"full_loop_check": True}, 'hasher_pipeline')
    ])

    file_object.id = "1"
    file_object._thumbnail.static_defaults.height = 562
    file_object._thumbnail.static_defaults.width = 375
    file_object._option.pipeline_raises_exception = False
    file_object._content.__class__._block_size = 102400
    file_object._content._block_size = 102400

    # Generate the thumbnail for the file
    file_object.thumbnail

    with open(
        f"{SERIALIZATION_DATA_DIR}/test_file_json_serialization_with_thumbnail_with_type_image_should_return_json"
        f"__{filename}.txt"
    ) as fp:
        expected_serialization = fp.read()

    # Due to the order of keys in serialization being non-deterministic we need to convert
    # again to dict to compare the results.
    assert json.loads(file_object.serialize()) == json.loads(expected_serialization)
    assert not list(file_object.pipelines_errors)


@pytest.mark.parametrize(
    "filename",
    [
        "183136-870151786_small_by_setfwithanf_At_pixabay.mp4",
    ]
)
def test_file_json_serialization_with_thumbnail_with_type_video_should_return_json(filename: str):
    File.serializer = FileJsonSerializer
    file_object = File(path=f"{VIDEO_DATA_DIR}/{filename}", pipelines_override_kwargs=[
        ({"full_loop_check": True}, 'hasher_pipeline')
    ])

    file_object.id = "1"
    file_object._thumbnail.static_defaults.height = 562
    file_object._thumbnail.static_defaults.width = 375
    file_object._option.pipeline_raises_exception = False
    file_object._content.__class__._block_size = 102400
    file_object._content._block_size = 102400

    # Generate the thumbnail for the file
    file_object.thumbnail

    with open(
        f"{SERIALIZATION_DATA_DIR}/test_file_json_serialization_with_thumbnail_with_type_video_should_return_json"
        f"__{filename}.txt",
    ) as fp:
        expected_serialization = fp.read()

    # Due to the order of keys in serialization being non-deterministic we need to convert
    # again to dict to compare the results.
    assert json.loads(file_object.serialize()) == json.loads(expected_serialization)
    assert not list(file_object.pipelines_errors)

