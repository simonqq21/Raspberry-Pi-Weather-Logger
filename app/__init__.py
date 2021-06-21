from flask import Flask

# "App" is the Flask application instance
# app is the application directory
print(__name__) # app
App = Flask(__name__)

from app import routes
