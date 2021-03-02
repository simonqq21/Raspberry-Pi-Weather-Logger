from flask import Flask

print(__name__)
App = Flask(__name__)

from app import routes
