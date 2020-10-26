from flask.blueprints import Blueprint
from flask.templating import render_template


bp = Blueprint("/", __name__, template_folder="templates")


@bp.route("/")
@bp.route("/index.html")
def index():
    return render_template("index.html")


@bp.route("/profile")
@bp.route("/profile.html")
def profile():
    return render_template("profile.html")