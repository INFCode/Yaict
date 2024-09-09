import pytest
import uuid
from pathlib import Path
import shutil
import logging
from yaict.dataset_manager import DatasetManager

@pytest.fixture(scope="function")
def test_dir():
    path = Path('./test_yaict_data')
    yield path
    shutil.rmtree(path)

@pytest.fixture
def dataset_manager(test_dir):
    return DatasetManager(base_dir=test_dir)

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

def test_setup_folders(dataset_manager, test_dir):
    dataset_manager.setup_folders()
    assert test_dir.exists()

def test_setup_existing_folders(dataset_manager, test_image_path, test_dir):
    # copy test_image_folder to build an existing folder
    test_dir.mkdir()
    (test_dir / 'images').mkdir()
    (test_dir / 'thumbnails').mkdir()
    shutil.copy(test_image_path, test_dir / 'images' / f'{uuid.uuid4()}.jpg')
    dataset_manager.setup_folders()
    assert test_dir.exists()

def test_add_image(dataset_manager, test_image_path):
    image_id = dataset_manager.add_image(test_image_path)
    image_path = dataset_manager.get_image_path(image_id)
    assert are_images_identical(test_image_path, image_path)

def test_add_images_from_folder(dataset_manager, test_image_folder, test_image_inside_folder):
    added_images = dataset_manager.add_images_from_folder(test_image_folder)
    cnt = 0
    for added_image_id in added_images:
        image_path = dataset_manager.get_image_path(added_image_id)
        cnt += are_images_identical(test_image_inside_folder, image_path)
    assert cnt == 1

def test_get_all_images(dataset_manager, test_image_path):
    dataset_manager.add_image(test_image_path)
    all_images = dataset_manager.get_all_images()
    assert len(all_images) == 1
    image_path = dataset_manager.get_image_path(all_images[0])
    assert are_images_identical(test_image_path, image_path)

    dataset_manager.add_images_from_folder(test_image_folder)
    all_images = dataset_manager.get_all_images()
    assert len(all_images) == 3 # 1 from add_image and 2 from add_images_from_folder

def test_set_caption(dataset_manager, test_image_path):
    image_id = dataset_manager.add_image(test_image_path)
    caption = "This is a test caption."
    dataset_manager.set_caption(image_id, caption)
    caption_path = dataset_manager.get_caption_path(image_id)
    assert caption_path is not None
    assert caption_path.exists()
    with open(caption_path, 'r') as file:
        assert file.read() == caption

    image_path = dataset_manager.get_image_path(image_id)
    assert image_path.exists()
    assert image_path.parent == caption_path.parent

def test_copy_caption_file(dataset_manager, test_image_path, tmp_path):
    image_id = dataset_manager.add_image(test_image_path)
    source_caption_path = tmp_path / "source_caption.txt"
    caption_text = "This is a copied caption."
    source_caption_path.write_text(caption_text)
    dataset_manager.copy_caption_file(image_id, source_caption_path)
    caption_path = dataset_manager.get_caption_path(image_id)
    assert caption_path is not None
    assert caption_path.exists()
    with open(caption_path, 'r') as file:
        assert file.read() == caption_text
    
    image_path = dataset_manager.get_image_path(image_id)
    assert image_path.exists()
    assert image_path.parent == caption_path.parent

def test_get_thumbnail_path_by_id(dataset_manager, test_image_path):
    image_id = dataset_manager.add_image(test_image_path)
    thumbnail_path = dataset_manager.get_thumbnail_path_by_id(image_id)
    assert thumbnail_path.exists()

def test_get_info_by_id(dataset_manager, test_image_path):
    image_id = dataset_manager.add_image(test_image_path)
    image_info = dataset_manager.get_info_by_id(image_id)
    assert image_info is not None
    assert image_info.image_id == image_id

def test_get_image_path(dataset_manager, test_image_path):
    image_id = dataset_manager.add_image(test_image_path)
    image_path = dataset_manager.get_image_path(image_id)
    assert image_path.exists()
    assert are_images_identical(test_image_path, image_path)

def test_get_caption_path(dataset_manager, test_image_path):
    image_id = dataset_manager.add_image(test_image_path, match_caption=True)
    caption_path = dataset_manager.get_caption_path(image_id)
    if caption_path:
        assert caption_path.exists()

def test_get_relative_thumbnail_path(dataset_manager, test_image_path):
    image_id = dataset_manager.add_image(test_image_path)
    thumbnail_path = dataset_manager.get_relative_thumbnail_path(image_id)
    assert thumbnail_path.exists()

def test_get_containing_folder(dataset_manager, test_image_path):
    image_id = dataset_manager.add_image(test_image_path)
    containing_folder = dataset_manager.get_containing_folder(image_id)
    assert containing_folder.exists()
