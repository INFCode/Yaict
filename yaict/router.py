from flask import Blueprint, current_app, send_file
from yaict.image_manager import ImageManager

# Create a Blueprint instance
image_bp = Blueprint('image_bp', __name__)

@image_bp.route('/images/<image_id>')
def serve_image(image_id):
    try:
        image_path = current_app.yaict['image_manager'].get_image_path_by_id(image_id)
        return send_file(image_path)
    except ValueError:
        return "Image not found", 404

@image_bp.route('/thumbnails/<image_id>')
def serve_thumbnail(image_id):
    thumbnail_path = current_app.yaict['image_manager'].get_thumbnail_path_by_id(image_id)
    if thumbnail_path.exists():
        return send_file(thumbnail_path)
    else:
        return "Thumbnail not found", 404