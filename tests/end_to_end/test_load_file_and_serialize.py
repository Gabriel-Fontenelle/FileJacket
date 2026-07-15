import os

from json import loads

from filejacket import File, FileWithContentJsonSerializer, FileJsonSerializerReadonly, FileJsonSerializer

from ..data import DATA_DIR


def test_file_load_and_serialized_successfully():
    """
    Test to load the files in data in current version of BaseFile and test if serializer works.
    """
    folders = (
        "images", "packets", "texts", "videos"
    )
    hashes = ("md5", "xxh128", "py")
    resources = (
        ("thumbnail",),
        ("internal_content",),
        ("hash",),
        ("meta",),
        ("meta", "internal_content"),
        ("meta", "thumbnail"),
        ("hash", "internal_content"),
        ("hash", "thumbnail"),
        ("hash", "meta"),
        ("hash", "internal_content", "thumbnail"),
        ("hash", "internal_content", "thumbnail", "meta"),
        ("thumbnail", "internal_content",),
        ("thumbnail", "internal_content", "meta"),
        ("meta", "internal_content", "hash"),
        ("hash", "meta", "thumbnail"),
    )
    serializers = (
        FileWithContentJsonSerializer,
        FileJsonSerializerReadonly,
        FileJsonSerializer
    )

    for serializer in serializers:
        File.serializer = serializer

        for resource in resources:
            for folder in folders:
                for filename in filter(
                        lambda x: not os.path.isdir(f"{DATA_DIR}/{folder}/{x}") and x.rsplit('.', 1)[-1] not in hashes,
                        os.listdir(f"{DATA_DIR}/{folder}")
                ):
                    file_object = File(path=f"{DATA_DIR}/{folder}/{filename}", pipelines_override_kwargs=[
                        ({"full_loop_check": True}, 'hasher_pipeline')
                    ])

                    file_object.id = "1"
                    file_object._thumbnail.static_defaults.height = 562
                    file_object._thumbnail.static_defaults.width = 375
                    file_object._option.pipeline_raises_exception = False
                    file_object._content.__class__._block_size = 102400
                    file_object._content._block_size = 102400

                    if "thumbnail" in resource:
                        # Generate the thumbnail for the file
                        file_object.generate_thumbnail()

                    if "hash" in resource:
                        file_object.generate_hashes()

                    if "internal_content" in resource:
                        file_object.files()

                    if "meta" in resource:
                        file_object.meta.test_additionak_info = True
                        file_object.meta.test_additionak_info_2 = "Test"
                        file_object.meta.test_additionak_info_3 = 1
                        file_object.meta.test_additionak_info = b"True"

                    assert not list(file_object.pipelines_errors)

                    serialized = file_object.serialize()
                    dict_content = loads(serialized)

                    assert serialized
                    assert dict_content

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
