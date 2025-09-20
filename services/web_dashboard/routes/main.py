from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Landing page for the application (now the only dashboard)"""
    return render_template('index.html')

@main.route('/monitoring')
def monitoring():
    """Page with the embedded Grafana monitoring dashboard (public)"""
    return render_template('monitoring.html')