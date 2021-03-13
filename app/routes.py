"""
@app.route decorator creates an association between
the URL given as an argument and the function.
"""
from app import app


@app.route("/")
@app.route("/index")
def index():
    return "Index page"
