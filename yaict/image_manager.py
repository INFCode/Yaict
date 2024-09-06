import shutil
from pathlib import Path
import logging
from typing import List
import uuid

from PIL import Image

class ImageManager:
    def __init__(self, base_dir: str):
        """
        Initialize the ImageManager with a base directory.
        :param base_dir: The base directory where images and captions will be stored.
        """
        self.base_dir = Path(base_dir)
        self.image_map = {}
        self.thumbnail_dir = self.base_dir / 'thumbnails'
        
        if not self.base_dir.exists():
            self.setup_folders()
        else:
            self.load_existing_images()
    
    def setup_folders(self) -> None:
        """
        Create the base directory and thumbnail directory if they don't exist.
        """
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)
        logging.info("Base directory and thumbnail directory created: %s, %s", self.base_dir, self.thumbnail_dir)

    def load_existing_images(self) -> None:
        """
        Scan the base directory and generate a dict mapping image id to its full path.
        """
        for folder in self.base_dir.iterdir():
            if folder.is_dir():
                for file in folder.iterdir():
                    if file.is_file():
                        image_id = str(uuid.uuid4())
                        self.image_map[image_id] = file
        logging.info("Loaded existing images: %s", self.image_map)

    def add_image(self, image_path: str) -> str:
        """
        Add an image to the managed folder structure.
        :param image_path: The path to the image to be added.
        :return: The unique id of the added image.
        """
        image_path = Path(image_path)
        logging.info("Attempting to add image: %s", image_path)
        if not image_path.exists():
            logging.error("Image %s does not exist.", image_path)
            raise FileNotFoundError(f"Image {image_path} does not exist.")

        # Create a unique id for the image
        image_id = str(uuid.uuid4())
        destination_folder = self.base_dir / image_path.stem
        destination_folder.mkdir(parents=True, exist_ok=True)
        logging.info("Created destination folder: %s", destination_folder)

        # Create a unique path for the image in the new folder
        destination_image_path = destination_folder / f"{image_id}.jpg"  # Assuming jpg for simplicity
        shutil.copy(image_path, destination_image_path)
        logging.info("Copied image to: %s", destination_image_path)

        # Create a real thumbnail
        thumbnail_size = (128, 128)  # Define the size for the thumbnail
        with Image.open(image_path) as img:
            img.thumbnail(thumbnail_size)
            thumbnail_path = self.thumbnail_dir / f"{image_id}.jpg"  # Assuming jpg for simplicity
            img.save(thumbnail_path)
            logging.info("Created thumbnail at: %s", thumbnail_path)

        # Store the mapping of image id to its path
        self.image_map[image_id] = destination_image_path
        logging.info("Image added successfully with id: %s", image_id)
        return image_id

    def add_images_from_folder(self, folder: str, extensions: list[str] = ['.jpg', '.jpeg', '.png']) -> list[str]:
        """
        Load all images from a specified folder and add them to the managed folder.
        :param folder: The folder to load images from (must be provided).
        :param extensions: List of file extensions to consider as images (default: ['.jpg', '.jpeg', '.png']).
        :return: List of added image ids.
        """
        folder = Path(folder)
        logging.info("Loading images from folder: %s", folder)
        logging.info("Using file extensions: %s", extensions)

        added_image_ids: list[str] = []
        for file in folder.iterdir():
            logging.info("Processing file: %s", file)
            if any(file.name.endswith(ext) for ext in extensions):
                image_id = self.add_image(file)
                added_image_ids.append(image_id)
                logging.debug("Added image with id: %s", image_id)

        logging.info("Added %d images", len(added_image_ids))
        return added_image_ids

    def get_all_images(self) -> List[str]:
        """
        Get a dictionary of all image ids and their corresponding paths in the managed directory.
        :return: Dictionary mapping image ids to their paths.
        """
        logging.info("Retrieved all images: %s", self.image_map)
        return list(self.image_map.keys())
    
    def get_image_path_by_id(self, image_id: str) -> Path:
        """
        Get the path of an image by its id.
        :param image_id: The id of the image to retrieve.
        :return: The path of the image.
        """
        image_path = self.image_map.get(image_id)
        if image_path:
            return image_path
        else:
            logging.error("Image with id %s not found.", image_id)
            raise ValueError(f"Image with id {image_id} not found.")
    
    def get_thumbnail_path_by_id(self, image_id: str) -> Path:
        """
        Get the path of a thumbnail by its id.
        :param image_id: The id of the thumbnail to retrieve.
        :return: The path of the thumbnail.
        """
        thumbnail_path = self.thumbnail_dir / f"{image_id}.jpg"
        return thumbnail_path