import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from app.models import UserProfile
from app.forms import LoginForm, UploadForm, SignUpForm

@login_manager.user_loader
def load_user(user_id):
    return UserProfile.query.get(int(user_id))

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')

@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    form = SignUpForm()

    if form.validate_on_submit():
        # Debugging: Log the lengths of the input data
        print(f"First Name Length: {len(form.first_name.data)}")
        print(f"Last Name Length: {len(form.last_name.data)}")
        print(f"Username Length: {len(form.username.data)}")
        print(f"Password Length: {len(form.password.data)}")

        # Create a new user and add to the database
        new_user = UserProfile(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            password=form.password.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Sign up successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = UserProfile.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html', form=form)

@app.route('/upload', methods=['POST', 'GET'])
@login_required  # Restrict access to logged-in users
def upload():
    form = UploadForm()  # Ensure the form is instantiated

    # Validate file upload on submit
    if form.validate_on_submit():
        file = form.file.data  # Get the uploaded file
        if file:
            filename = secure_filename(file.filename)  # Secure the filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Save path
            file.save(file_path)  # Save the file
            print(f"File saved to: {file_path}")  # Debugging statement
            flash('File Saved', 'success')
            return redirect(url_for('files'))  # Redirect to the files route
        else:
            print("No file uploaded.")  # Debugging statement

    return render_template('upload.html', form=form)

def get_uploaded_images():
    """Helper function to get a list of uploaded image filenames."""
    upload_folder = app.config['UPLOAD_FOLDER']
    return [f for f in os.listdir(upload_folder) if os.path.isfile(os.path.join(upload_folder, f))]

@app.route('/uploads/<filename>')
def get_image(filename):
    """Serve an uploaded image."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/files')
@login_required
def files():
    """Render a list of uploaded files."""
    images = get_uploaded_images()
    return render_template('files.html', images=images)

@app.route('/logout')
@login_required
def logout():
    """Log out the user and redirect to home."""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))
