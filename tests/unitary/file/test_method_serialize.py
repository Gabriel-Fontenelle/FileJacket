import pytest

from filejacket.file import (
    FileActions,
    FileContent,
    FileOption,
    FileHashes,
    FileMetadata,
    FileNaming,
    FilePacket,
    FileState
)


@pytest.mark.parametrize(
    "file_class, init_value, expected_attributes",
    [
        (FileActions, None, {
            "extract",
            "hash",
            "list",
            "move",
            "preview",
            "rename",
            "save",
            "thumbnail",
            "was_extracted",
            "was_hashed",
            "was_listed",
            "was_moved",
            "was_previewed",
            "was_renamed",
            "was_saved",
            "was_thumbnailed"
        }),
        (FileContent, {"raw_value": "test"}, {
            "buffer",
            "buffer_helper",
            "cache_helper",
            "related_file_object",
            "_block_size",
            "_buffer_encoding",
            "cached",
            "_cached_content"
        }),
        (FileHashes, None, {"_cache", "_loaded", "related_file_object"}),
        (FileMetadata, None, {"packed", "compressed", "lossless", "hashable", "extra_data"}),
        (FileOption, None, {
            "allow_overwrite",
            "allow_override",
            "allow_search_hashes",
            "allow_update",
            "allow_rename",
            "allow_extension_change",
            "create_backup",
            "save_hashes",
            "pipeline_raises_exception"
        }),
        (FileNaming, None, {
            "history",
            "on_conflict_rename",
            "related_file_object",
            "previous_saved_extension"
        }),
        (FilePacket, None, {"_internal_files", "unpack_data_pipeline", "history", "length"}),
        (FileState, None, {"adding", "renaming", "changing", "processing", "moving"})
        
    ]
)
def test_method_serialization_of_auxiliary_class_return_correct_attributes(file_class, init_value, expected_attributes):
    class_object = file_class(**init_value) if init_value else file_class()

    assert set(sorted(class_object.__serialize__.keys())) == expected_attributes
