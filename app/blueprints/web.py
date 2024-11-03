from flask import Blueprint, request

bp = Blueprint("web", __name__)

@bp.route("/")
def index():
    return "<h1>Hello, World!</h1>"
@bp.route("/about/")
def myAboutRoute():
    return "<h1>About Page</h1>"