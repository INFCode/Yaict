import shutil
from pathlib import Path
import logging
from typing import List, Optional
import uuid

from PIL import Image

class ImageInfo:
    def __init__(self, image_id: str, group_name: str, image_extension: str, thumbnail_extension: str, caption_extension: Optional[str] = None):
        self.image_id = image_id
        self.image_extension = image_extension
        self.thumbnail_extension = thumbnail_extension
        self.caption_extension = caption_extension
        self.group_name = group_name
    
    def get_image_path(self, image_dir: Path) -> Path:
        return image_dir / self.group_name / f"{self.image_id}{self.image_extension}"
    
    def get_caption_path(self, image_dir: Path) -> Path:
        if self.caption_extension:
            return image_dir / self.group_name / f"{self.image_id}{self.caption_extension}"
        else:
            return None
    
    def get_relative_thumbnail_path(self, thumbnail_dir: Path) -> Path:
        return thumbnail_dir / f"{self.image_id}{self.thumbnail_extension}"
    
    def get_containing_folder(self, image_dir: Path) -> Path:
        return image_dir / self.group_name
    
    def get_group_name(self) -> str:
        return self.group_name

def has_extension(file: Path, extensions: List[str]) -> bool:
    return file.suffix.lower() in (ext.lower() for ext in extensions)

def find_file_with_extensions(folder: Path, name: str, extensions: List[str]) -> Path:
    for ext in extensions:
        file_path = folder / f"{name}{ext}"
        if file_path.exists():
            return file_path
    return None

class DatasetManager:
    def __init__(self, base_dir: str):
        """
        Initialize the ImageManager with a base directory.
        :param base_dir: The base directory where images and captions will be stored.
        """
        self.base_dir = Path(base_dir)
        self.image_dir = self.base_dir / 'images'
        self.thumbnail_dir = self.base_dir / 'thumbnails'
        self.id_to_info = {}

        if not self.base_dir.exists():
            self.setup_folders()
        else:
            self.load_existing_images(self.image_dir)

    def setup_folders(self) -> None:
        """
        Create the base directory, image directory, and thumbnail directory if they don't exist.
        """
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.image_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)
        logging.info("Base directory, image directory, and thumbnail directory created: %s, %s, %s", 
                     self.base_dir, self.image_dir, self.thumbnail_dir)

    def load_existing_images(self, image_dir: Path) -> None:
        for folder in image_dir.iterdir():
            if folder.is_dir():
                for file in folder.iterdir():
                    if file.is_file() and has_extension(file, ['.jpg', '.jpeg', '.png']):
                        image_id = file.stem
                        # check if there is a caption file
                        caption_file = find_file_with_extensions(folder, image_id, ['.txt', '.caption'])
                        caption_ext = caption_file.suffix if caption_file else None
                        self.id_to_info[image_id] = ImageInfo(image_id, folder.name, file.suffix, '.jpg', caption_ext)
        logging.info("Loaded existing images: %s", self.id_to_info)

    def add_images_from_folder(self, folder: str, extensions: list[str] = ['.jpg', '.jpeg', '.png'], include_captions: bool = False) -> list[str]:
        """
        Load all images from a specified folder and add them to the managed folder.
        :param folder: The folder to load images from (must be provided).
        :param extensions: List of file extensions to consider as images (default: ['.jpg', '.jpeg', '.png']).
        :param include_captions: Whether to include caption files (default: False).
        :return: List of added image ids.
        """
        folder = Path(folder)
        logging.info("Loading images from folder: %s", folder)
        logging.info("Using file extensions: %s", extensions)

        added_image_ids: List[str] = []
        for file in folder.iterdir():
            logging.info("Processing file: %s", file)
            if has_extension(file, extensions):
                image_id = self.add_image(file, include_captions)
                added_image_ids.append(image_id)
                logging.debug("Added image with id: %s", image_id)

        logging.info("Added %d images", len(added_image_ids))
        return added_image_ids

    def new_image_id(self) -> str:
        """
        Generate a new unique image id.
        :return: A new unique image id.
        """
        return str(uuid.uuid4())

    def add_image(self, image_path: Path, match_caption: bool = False) -> str:
        """
        Add an image to the managed folder structure along with its caption.
        :param image_path: The path to the image to be added.
        :param match_caption: Whether to match the caption file with the image file.
        :return: The unique id of the added image.
        """
        logging.info("Attempting to add image: %s", image_path)
        if not image_path.exists():
            logging.error("Image %s does not exist.", image_path)
            raise FileNotFoundError(f"Image {image_path} does not exist.")

        # break down the image path into the folder and the file name
        source_image_folder = image_path.parent
        source_image_file_name = image_path.stem
        source_image_extension = image_path.suffix

        # Create a unique id for the image
        image_id = self.new_image_id()
        destination_folder = self.image_dir / source_image_file_name
        destination_folder.mkdir(parents=True, exist_ok=True)
        logging.info("Created destination folder: %s", destination_folder)

        # Create a unique path for the image in the new folder using the original file extension
        destination_image_path = destination_folder / f"{image_id}{source_image_extension}"
        shutil.copy(image_path, destination_image_path)
        logging.info("Copied image to: %s", destination_image_path)

        # Handle caption file
        caption_ext = None
        if match_caption:
            caption_file_path = find_file_with_extensions(source_image_folder, source_image_file_name, ['.txt', '.caption'])
            if caption_file_path:
                logging.info("Caption file found: %s", caption_file_path)
                caption_ext = caption_file_path.suffix
                shutil.copy(caption_file_path, destination_folder / f"{image_id}{caption_ext}")
            else:
                logging.info("No caption file found for image: %s", source_image_file_name)

        # Create a thumbnail
        thumbnail_size = (128, 128)
        with Image.open(destination_image_path) as img:
            img.thumbnail(thumbnail_size)
            thumbnail_path = self.thumbnail_dir / f"{image_id}.jpg"
            img.save(thumbnail_path)
            logging.info("Created thumbnail at: %s", thumbnail_path)

        # Store the mapping of image id to its path
        self.id_to_info[image_id] = ImageInfo(image_id, source_image_file_name, source_image_extension, '.jpg', caption_ext)
        logging.info("Image added successfully with id: %s", image_id)
        return image_id

    def set_caption(self, image_id: str, caption: str) -> None:
        """
        Set the caption for an image.
        :param image_id: The id of the image to set the caption for.
        :param caption: The caption to set for the image.
        """
        image_info = self.get_info_by_id(image_id)
        if not image_info:
            logging.error("Image %s not found.", image_id)
            raise ValueError(f"Image {image_id} not found.")

        caption_file_path = self.image_dir / image_info.get_group_name() / f"{image_id}.txt"
        with open(caption_file_path, 'w') as file:
            file.write(caption)
        image_info.caption_extension = '.txt'
        logging.info("Caption set for image %s: %s", image_id, caption)

    def copy_caption_file(self, image_id: str, source_file_path: Path) -> None:
        """
        Copy the caption file from a source file to the image folder.
        :param image_id: The id of the image to copy the caption file for.
        :param source_file_path: The path to the source file to copy the caption file from.
        """
        if not source_file_path.exists():
            logging.error("Source file %s does not exist.", source_file_path)
            raise FileNotFoundError(f"Source file {source_file_path} does not exist.")

        image_info = self.get_info_by_id(image_id)
        if not image_info:
            logging.error("Image %s not found.", image_id)
            raise ValueError(f"Image {image_id} not found.")

        caption_file_path = self.image_dir / image_info.get_group_name() / f"{image_id}.txt"
        shutil.copy(source_file_path, caption_file_path)
        image_info.caption_extension = source_file_path.suffix
        logging.info("Copied caption file to: %s", caption_file_path)

    def get_all_images(self) -> List[str]:
        logging.info("Retrieved all images: %s", self.id_to_info)
        return list(self.id_to_info.keys())

    def get_thumbnail_path_by_id(self, image_id: str) -> Optional[Path]:
        thumbnail_path = self.thumbnail_dir / f"{image_id}.jpg"
        if thumbnail_path.exists():
            return thumbnail_path
        else:
            return None
    
    def get_info_by_id(self, image_id: str) -> Optional[ImageInfo]:
        return self.id_to_info.get(image_id, None)
    
    def get_image_path(self, image_id: str) -> Optional[Path]:
        image_info = self.get_info_by_id(image_id)
        if image_info:
            return image_info.get_image_path(self.image_dir)
        return None

    def get_caption_path(self, image_id: str) -> Optional[Path]:
        image_info = self.get_info_by_id(image_id)
        if image_info:
            return image_info.get_caption_path(self.image_dir)
        return None

    def get_relative_thumbnail_path(self, image_id: str) -> Optional[Path]:
        image_info = self.get_info_by_id(image_id)
        if image_info:
            return image_info.get_relative_thumbnail_path(self.thumbnail_dir)
        return None

    def get_containing_folder(self, image_id: str) -> Optional[Path]:
        image_info = self.get_info_by_id(image_id)
        if image_info:
            return image_info.get_containing_folder(self.image_dir)
        return None