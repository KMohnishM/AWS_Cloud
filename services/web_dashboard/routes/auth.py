from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from datetime import datetime, timedelta

from models.user import User, UserSession, db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if not user or not user.check_password(password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))
            
        # If user exists and is inactive
        if not user.is_active:
            flash('This account has been deactivated. Please contact an administrator.')
            return redirect(url_for('auth.login'))
            
        # Update last login time
        user.last_login = datetime.utcnow()
        
        # Create session record
        session = UserSession(
            session_id=request.cookies.get('session'),
            user_id=user.user_id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            expires_at=datetime.utcnow() + timedelta(days=30) if remember else None
        )
        
        # Commit changes to database
        db.session.add(session)
        db.session.commit()
        
        # Log in user
        login_user(user, remember=remember)
        
        # Redirect to the page the user was trying to access
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
            
        return redirect(next_page)
        
    return render_template('auth/login.html')
    
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already exists.')
            return redirect(url_for('auth.register'))
            
        # Create new user - default role is 'technician' for security
        # Admins can later upgrade role if needed
        new_user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='technician'  # Default lowest privilege role
        )
        new_user.set_password(password)
        
        # Add and commit to database
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    # Find and invalidate the current session
    session = UserSession.query.filter_by(
        session_id=request.cookies.get('session'),
        user_id=current_user.user_id
    ).first()
    
    if session:
        db.session.delete(session)
        db.session.commit()
    
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))

@auth.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')

@auth.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # Update profile information
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.email = request.form.get('email')
        
        # Only update password if provided
        if request.form.get('password'):
            current_user.set_password(request.form.get('password'))
            
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('auth.profile'))
        
    return render_template('auth/edit_profile.html')

# Admin routes for user management
@auth.route('/admin/users')
@login_required
def admin_users():
    if not current_user.has_permission('manage_users'):
        flash('You do not have permission to access this page.')
        return redirect(url_for('index'))
        
    users = User.query.all()
    return render_template('auth/admin_users.html', users=users)

@auth.route('/admin/users/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    if not current_user.has_permission('manage_users'):
        flash('You do not have permission to access this page.')
        return redirect(url_for('index'))
        
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.role = request.form.get('role')
        user.department = request.form.get('department')
        user.is_active = True if request.form.get('is_active') else False
        
        # Only update password if provided
        if request.form.get('password'):
            user.set_password(request.form.get('password'))
            
        db.session.commit()
        flash(f'User {user.username} has been updated.')
        return redirect(url_for('auth.admin_users'))
        
    return render_template('auth/admin_edit_user.html', user=user)

@auth.route('/admin/users/create', methods=['GET', 'POST'])
@login_required
def admin_create_user():
    if not current_user.has_permission('manage_users'):
        flash('You do not have permission to access this page.')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        role = request.form.get('role')
        department = request.form.get('department')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('auth.admin_create_user'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already exists.')
            return redirect(url_for('auth.admin_create_user'))
            
        # Create new user
        new_user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            department=department,
            is_active=True
        )
        new_user.set_password(password)
        
        # Add and commit to database
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'User {username} has been created.')
        return redirect(url_for('auth.admin_users'))
        
    return render_template('auth/admin_create_user.html')