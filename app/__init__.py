from flask import Flask

# app - instance of Flask class
app = Flask(__name__)

# app - package
# The bottom import is a workaround to circular imports
# routes module needs to import the app variable defined in this script,
# so putting one of the reciprocal imports at the bottom avoids the error
# that results from the mutual references between these two files
from app import routes

