import shutil
from pathlib import Path

import logging

class ImageManager:
    def __init__(self, base_dir: str):
        """
        Initialize the ImageManager with a base directory.
        :param base_dir: The base directory where images and captions will be stored.
        """
        self.base_dir = Path(base_dir)
        logging.info("ImageManager initialized with base directory: %s", self.base_dir)
        self.setup_folders()
    
    def setup_folders(self) -> None:
        """
        Create the base directory if it doesn't exist.
        """
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logging.info("Base directory created: %s", self.base_dir)

    def add_image(self, image_path: str) -> Path:
        """
        Add an image to the managed folder structure.
        :param image_path: The path to the image to be added.
        :return: The path to the added image's directory in the managed folder.
        """
        image_path = Path(image_path)
        logging.info("Attempting to add image: %s", image_path)
        if not image_path.exists():
            logging.error("Image %s does not exist.", image_path)
            raise FileNotFoundError(f"Image {image_path} does not exist.")

        # Create a unique folder name based on the image name (without extension)
        folder_name = image_path.stem
        destination_folder = self.base_dir / folder_name
        destination_folder.mkdir(parents=True, exist_ok=True)
        logging.info("Created destination folder: %s", destination_folder)

        # Copy the image to the new folder
        destination_image_path = destination_folder / image_path.name
        shutil.copy(image_path, destination_image_path)
        logging.info("Copied image to: %s", destination_image_path)

        # Return the path to the folder containing the image and caption
        logging.info("Image added successfully to: %s", destination_folder)
        return destination_folder

    def add_images_from_folder(self, folder: str, extensions: list[str] = ['.jpg', '.jpeg', '.png']) -> list[Path]:
        """
        Load all images from a specified folder and add them to the managed folder.
        :param folder: The folder to load images from (must be provided).
        :param extensions: List of file extensions to consider as images (default: ['.jpg', '.jpeg', '.png']).
        :return: List of added image paths.
        """
        folder = Path(folder)
        logging.info("Loading images from folder: %s", folder)
        logging.info("Using file extensions: %s", extensions)

        added_images: list[Path] = []
        for file in folder.iterdir():
            logging.info("Processing file: %s", file)
            if any(file.name.endswith(ext) for ext in extensions):
                added_image_folder = self.add_image(file)
                added_images.append(added_image_folder)
                logging.debug("Added image: %s", file)

        logging.info("Added %d images", len(added_images))
        return added_images

    def get_all_images(self, extensions: list[str] = ['.jpg', '.jpeg', '.png']) -> list[Path]:
        """
        Get a list of all image files in the managed directory.
        :return: List of paths to all image files.
        """
        image_files: list[Path] = []
        for folder in self.base_dir.iterdir():
            if folder.is_dir():
                for ext in extensions:
                    img_file = folder / f"{folder.name}{ext}"
                    if img_file.exists():
                        image_files.append(img_file)
                        break  # Assuming only one matching image per folder
        logging.info("Retrieved matching image files: %s", image_files)
        return image_files