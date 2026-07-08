from flask import Flask, request, render_template, flash
import os

from config import Config

# Detector
from detector.file_detector import detect_file_type

# Parser Factory
from parsers.parser_factory import ParserFactory

app = Flask(__name__)
app.config.from_object(Config)

# Create upload folder automatically
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


@app.route("/")
def index():
    """
    Display upload page.
    """
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    # -------------------------
    # Check if file exists
    # -------------------------

    if "report_file" not in request.files:
        flash("No file selected.")
        return render_template("index.html")

    uploaded_file = request.files["report_file"]

    if uploaded_file.filename == "":
        flash("Please select a report.")
        return render_template("index.html")

    # -------------------------
    # Read file bytes
    # -------------------------

    file_bytes = uploaded_file.read()

    try:

        # -------------------------
        # Detect report type
        # -------------------------

        report_type = detect_file_type(
            uploaded_file.filename,
            file_bytes
        )

        # -------------------------
        # Get parser
        # -------------------------

        parser = ParserFactory.get_parser(report_type)

        # -------------------------
        # Parse report
        # -------------------------

        report = parser.parse(file_bytes)

        # -------------------------
        # Render HTML report
        # -------------------------

        return render_template(
            "report.html",
            report=report,
            report_type=report_type.upper()
        )

    except Exception as e:

        flash(str(e))

        return render_template("index.html")


@app.errorhandler(413)
def file_too_large(e):
    flash("Maximum upload size is 20 MB.")
    return render_template("index.html"), 413


@app.errorhandler(404)
def page_not_found(e):
    return "<h2>404 - Page Not Found</h2>", 404


@app.errorhandler(500)
def internal_error(e):
    return "<h2>Internal Server Error</h2>", 500


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )