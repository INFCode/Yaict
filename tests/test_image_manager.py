import pytest
from pathlib import Path
import shutil
import logging
from yaict.image_manager import ImageManager

@pytest.fixture(scope="module")
def test_dir():
    path = Path('./test_yaict_data')
    path.mkdir(parents=True, exist_ok=True)
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

def test_setup_folders(image_manager, test_dir):
    image_manager.setup_folders()
    assert test_dir.exists()

def test_add_image(image_manager, test_image_path):
    added_image_folder = image_manager.add_image(test_image_path)
    assert (added_image_folder / test_image_path.name).exists()

def test_add_images_from_folder(image_manager, test_image_folder):
    added_images = image_manager.add_images_from_folder(test_image_folder)
    for added_image_folder in added_images:
        assert added_image_folder.exists()
        assert (added_image_folder / added_image_folder.name).exists()

def test_get_all_images(image_manager, test_image_path):
    image_manager.add_image(test_image_path)
    all_images = image_manager.get_all_images()
    assert len(all_images) > 0
    assert all_images[0].exists()
