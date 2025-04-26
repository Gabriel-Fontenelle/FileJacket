import pytest

from filejacket.pipelines.base import BaseComparer
from filejacket.pipelines.comparer import (
    DataCompare,
    SizeCompare,
    HashCompare,
    LousyNameCompare,
    NameCompare,
    MimeTypeCompare,
    BinaryCompare,
    TypeCompare
)


@pytest.mark.parametrize(
    "package_class",
    [
        BaseComparer,
        DataCompare,
        SizeCompare,
        HashCompare,
        LousyNameCompare,
        NameCompare,
        MimeTypeCompare,
        BinaryCompare,
        TypeCompare
    ]
)
def test_class_for_comparing_has_required_attribute(package_class):
    assert hasattr(package_class, 'is_the_same')
    assert hasattr(package_class, 'process')


def test_base_class_for_comparing_raise_not_implemented_error_in_some_attributes(file_jpg, file_svg):
    with pytest.raises(NotImplementedError):
        BaseComparer.is_the_same(file_1=file_jpg, file_2=file_svg)


@pytest.mark.parametrize(
    "package_class",
    [
        DataCompare,
        SizeCompare,
        HashCompare,
        LousyNameCompare,
        NameCompare,
        MimeTypeCompare,
        BinaryCompare,
        TypeCompare
    ]
)
def test_method_is_the_same_with_equal_file_should_return_true(package_class, file_jpg):
    assert package_class.is_the_same(file_1=file_jpg, file_2=file_jpg)


@pytest.mark.parametrize(
    "package_class",
    [

        DataCompare,
        SizeCompare,
        HashCompare,
        LousyNameCompare,
        NameCompare,
        MimeTypeCompare,
        BinaryCompare,
        TypeCompare
    ]
)
def test_method_is_the_same_with_unequal_file_should_return_false(package_class, file_gif, file_txt):
    assert package_class.is_the_same(file_1=file_gif, file_2=file_txt) is False


@pytest.mark.parametrize(
    "package_class",
    [
        DataCompare,
        SizeCompare,
        HashCompare,
        LousyNameCompare,
        NameCompare,
        MimeTypeCompare,
        BinaryCompare,
        TypeCompare
    ]
)
def test_method_process_with_equal_files_should_return_true(package_class, file_jpg):
    assert package_class.process(object_to_process=file_jpg, objects_to_compare=[file_jpg])

    
@pytest.mark.parametrize(
    "package_class",
    [
        DataCompare,
        SizeCompare,
        HashCompare,
        LousyNameCompare,
        NameCompare,
        MimeTypeCompare,
        BinaryCompare,
        TypeCompare
    ]
)
def test_method_is_the_same_with_unequal_files_should_return_false(package_class, file_jpg, file_txt):
    assert package_class.process(object_to_process=file_jpg, objects_to_compare=[file_txt]) is False
