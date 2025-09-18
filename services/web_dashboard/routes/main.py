from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Landing page for the application"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard showing patient monitoring overview"""
    return render_template('dashboard.html')

@main.route('/monitoring')
@login_required
def monitoring():
    """Page with the embedded Grafana monitoring dashboard"""
    return render_template('monitoring.html')