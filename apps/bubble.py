import dash_bootstrap_components as dbc
import dash_html_components as html
from app import app
import pickle
from pathlib import Path

cwd = Path.cwd()

with open(cwd.joinpath("assets/graph1.pkl"), "rb") as f:
    sg = pickle.load(f)

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}
layout = html.Div([
            dbc.Spinner(sg,
                    color="primary", type="border", fullscreen=True,
                    spinner_style={"width": "20rem", "height": "20rem"})
])