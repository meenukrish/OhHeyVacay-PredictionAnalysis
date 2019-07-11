from predictfare import predictMarketFare, predictallairfare , findlatlng

import os
import pandas as pd
import numpy as np
from flask import Flask, jsonify, render_template, request, redirect
from predictfare import predictMarketFare, predictallairfare , findlatlng
from fareapp import fareapp
from ontimeapp import ontimeapp

app = Flask(__name__, static_url_path='/static')
app.register_blueprint(fareapp)
app.register_blueprint(ontimeapp)


@app.route("/")
def index():
    """Return the homepage."""

    return render_template("index.html")

@app.route("/slides", methods=["GET"])
def slides():
    """Return the Slides."""
    return render_template("slides.html")

@app.route("/aboutus", methods=["GET"])
def aboutus():
    """Return the aboutus."""
    return render_template("aboutus.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 17995))
    app.run(host='0.0.0.0', port=port)