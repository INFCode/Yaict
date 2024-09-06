from dash import html
from dash import dcc

def generate_image_display(image_id: str) -> html.Div:
    """
    Generate Dash components to display a thumbnail with a checkbox.
    :param image_id: The id of the image.
    :return: A Dash HTML component for the image display with a checkbox.
    """
    image_url = f'http://localhost:8050/thumbnails/{image_id}'  # Updated to use the local Flask server URL

    # Create an HTML figure with the image and a checkbox
    image_component = html.Div(
        [
            html.Img(src=image_url, style={'width': '150px', 'height': '150px'}),
            dcc.Checklist(
                options=[{'label': '', 'value': image_id}],  # Label is empty for a cleaner look
                id=f'checkbox-{image_id}',
                style={'position': 'absolute', 'bottom': '10px', 'right': '10px'}
            )
        ],
        style={'display': 'inline-block', 'margin': '10px', 'position': 'relative'}
    )
    return image_component