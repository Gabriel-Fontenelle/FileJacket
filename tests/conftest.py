import pytest
import json

from filejacket import File

from .data import DATA_DIR
from .data.images import DATA_DIR as IMAGE_DATA_DIR
from .data.videos import DATA_DIR as VIDEO_DATA_DIR
from .data.packets import DATA_DIR as PACKET_DATA_DIR
from .data.texts import DATA_DIR as TEXT_DATA_DIR
from .data.serializations import DATA_DIR as SERIALIZATION_DATA_DIR


@pytest.fixture
def file_jpg() -> File:
    return File(path=f"{IMAGE_DATA_DIR}/aurora-1197753_1280_by_Noel_Bauza_at_pixabay.jpg")


@pytest.fixture
def file_png() -> File:
    return File(path="")


@pytest.fixture
def file_txt() -> File:
    return File(path=f"{TEXT_DATA_DIR}/content_for_test.txt")


@pytest.fixture
def file_psd() -> File:
    return File(path=f"{PACKET_DATA_DIR}/3763816_76417.psd")


@pytest.fixture
def file_gif() -> File:
    return File(path=f"{IMAGE_DATA_DIR}/snow-man-10450_by_winterflower_at_pixabay.gif")


@pytest.fixture
def file_svg() -> File:
    return File(path=f"{IMAGE_DATA_DIR}/watermelon-8368960_by_ebengg_at_pixabay.svg")


@pytest.fixture
def file_epub() -> File:
    return File(path=f"{PACKET_DATA_DIR}/franklin-w-dixon_hunting-for-hidden-gold_advanced.epub")


@pytest.fixture
def file_rar() -> File:
    return File(path=f"{PACKET_DATA_DIR}/images.rar")


@pytest.fixture
def file_tar() -> File:
    return File(path=f"{PACKET_DATA_DIR}/images.tar")


@pytest.fixture
def file_7zip() -> File:
    return File(path=f"{PACKET_DATA_DIR}/images.7z")


@pytest.fixture
def file_zip() -> File:
    return File(path=f"{PACKET_DATA_DIR}/images.zip")


@pytest.fixture
def file_cbz() -> File:
    return File(path=f"{PACKET_DATA_DIR}/images.cbz")


@pytest.fixture
def file_mp4() -> File:
    return File(path=f"{VIDEO_DATA_DIR}/183136-870151786_small_by_setfwithanf_At_pixabay.mp4")


@pytest.fixture
def json_serialized_v1_json_simple_readonly_packets_images_zip():
    file_path = f"{SERIALIZATION_DATA_DIR}/v1__json_simple__readonly__with_thumbnail__source__packets_images.zip.json"

    with open(file_path, mode='r') as fp:
        content = fp.read()
        content = content.replace('..', f"{PACKET_DATA_DIR}")

    return content


@pytest.fixture
def json_serialized_v1_dictionary_readonly_packets_images_zip():
    file_path = f"{SERIALIZATION_DATA_DIR}/v1__json_simple__readonly__with_thumbnail__source__packets_images.zip.json"

    with open(file_path, mode='r') as fp:
        content = fp.read()
        # Replace relative path to absolute
        content = content.replace('..', f"{PACKET_DATA_DIR}")
        content = json.loads(content)

    return content
