import logging
import dash
from dash import html
from yaict.image_display import generate_image_display
from yaict.router import image_bp
from yaict.image_manager import ImageManager
from pathlib import Path
from flask import Flask


def create_app() -> dash.Dash:
    flask_app = Flask(__name__)

    image_manager = ImageManager(base_dir=Path.cwd() / 'yaict_image_store')

    # Simulate a list of image paths
    image_paths = [
        Path('./tests/imgs/img_folder/cherry.jpg'),
        Path('./tests/imgs/img_folder/pineapple.jpg')
    ]
    
    if not image_manager.get_all_images():  # Check if there are no active images
        for img in image_paths:
            image_manager.add_image(img)

    flask_app.yaict = {}
    flask_app.yaict['image_manager'] = image_manager
    flask_app.register_blueprint(image_bp)

    # Initialize the Dash app
    app = dash.Dash(__name__, server=flask_app)

    # Define the layout of the app using the image display function
    app.layout = html.Div(children=[
        html.H1(children='Image Gallery with Checkboxes'),

        # Use the image display component to render the images and checkboxes
        html.Div([generate_image_display(image_id) for image_id in image_manager.get_all_images()])
    ])
    
    return app

# Run the app
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s'
    )

    app = create_app()
    app.run_server(debug=True)