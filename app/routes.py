from flask import render_template, url_for
from app import App
from datetime import datetime

@App.route('/')
@App.route('/index')
def index():
    return render_template("index.html")

@App.route('/history')
def log_history():
    return render_template("weather_logs.html")
