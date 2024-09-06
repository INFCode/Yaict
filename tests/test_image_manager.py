import pytest
from pathlib import Path
import shutil
import logging
from yaict.image_manager import ImageManager

@pytest.fixture(scope="function")
def test_dir():
    path = Path('./test_yaict_data')
    yield path
    shutil.rmtree(path)

@pytest.fixture
def image_manager(test_dir):
    return ImageManager(base_dir=test_dir)

@pytest.fixture
def test_image_path():
    return Path('./tests/imgs/banana.jpg')

@pytest.fixture
def test_image_folder():
    return Path('./tests/imgs/img_folder')

@pytest.fixture
def test_image_inside_folder():
    return Path('./tests/imgs/img_folder/pineapple.jpg')

def are_images_identical(image_path1: Path, image_path2: Path) -> bool:
    if not image_path1.exists() or not image_path2.exists():
        logging.error("One or both images do not exist: %s, %s", image_path1, image_path2)
        raise FileNotFoundError("One or both images do not exist.")

    with open(image_path1, 'rb') as file1, open(image_path2, 'rb') as file2:
        return file1.read() == file2.read()

def test_setup_folders(image_manager, test_dir):
    image_manager.setup_folders()
    assert test_dir.exists()

def test_add_image(image_manager, test_image_path):
    image_id = image_manager.add_image(test_image_path)
    image_path = image_manager.get_image_path_by_id(image_id)
    assert are_images_identical(test_image_path, image_path)

def test_add_images_from_folder(image_manager, test_image_folder, test_image_inside_folder):
    added_images = image_manager.add_images_from_folder(test_image_folder)
    cnt = 0
    for added_image_id in added_images:
        image_path = image_manager.get_image_path_by_id(added_image_id)
        cnt += are_images_identical(test_image_inside_folder, image_path)
    assert cnt == 1

def test_get_all_images(image_manager, test_image_path):
    image_manager.add_image(test_image_path)
    all_images = image_manager.get_all_images()
    assert len(all_images) == 1
    image_path = image_manager.get_image_path_by_id(all_images[0])
    assert are_images_identical(test_image_path, image_path)
