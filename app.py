import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.utils import secure_filename
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import io

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Require SECRET_KEY in production
secret_key = os.getenv('SECRET_KEY')
if not secret_key:
    # Only use default in development
    if os.getenv('FLASK_ENV') == 'development':
        secret_key = 'dev-secret-key-change-in-production'
        print('WARNING: Using default secret key. Set SECRET_KEY environment variable in production!')
    else:
        raise ValueError('SECRET_KEY environment variable must be set in production')

app.secret_key = secret_key

# Configuration
AUTH_USERNAME = os.getenv('AUTH_USERNAME', 'admin')
AUTH_PASSWORD = os.getenv('AUTH_PASSWORD', 'changeme')
SPACES_REGION = os.getenv('SPACES_REGION', 'nyc3')
SPACES_ENDPOINT = os.getenv('SPACES_ENDPOINT', 'https://nyc3.digitaloceanspaces.com')
SPACES_KEY = os.getenv('SPACES_KEY')
SPACES_SECRET = os.getenv('SPACES_SECRET')
SPACES_BUCKET = os.getenv('SPACES_BUCKET')

# Initialize S3 client for Digital Ocean Spaces
s3_client = boto3.client(
    's3',
    region_name=SPACES_REGION,
    endpoint_url=SPACES_ENDPOINT,
    aws_access_key_id=SPACES_KEY,
    aws_secret_access_key=SPACES_SECRET
)


def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == AUTH_USERNAME and password == AUTH_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    """Main page showing list of uploaded files"""
    files = []
    
    try:
        # List objects in the bucket
        response = s3_client.list_objects_v2(Bucket=SPACES_BUCKET)
        
        if 'Contents' in response:
            for obj in response['Contents']:
                files.append({
                    'name': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'last_modified_str': obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
                })
            
            # Sort by last modified datetime object, newest first
            files.sort(key=lambda x: x['last_modified'], reverse=True)
    
    except ClientError as e:
        flash(f'Error listing files: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unable to connect to storage. Please check your configuration: {str(e)}', 'error')
    
    return render_template('index.html', files=files)


@app.route('/upload', methods=['POST'])
@login_required
def upload():
    """Handle file upload"""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    # Validate PDF file
    if not file.filename.lower().endswith('.pdf'):
        flash('Only PDF files are allowed', 'error')
        return redirect(url_for('index'))
    
    try:
        filename = secure_filename(file.filename)
        
        # Upload to Digital Ocean Spaces
        s3_client.upload_fileobj(
            file,
            SPACES_BUCKET,
            filename,
            ExtraArgs={'ACL': 'private', 'ContentType': 'application/pdf'}
        )
        
        flash(f'File "{filename}" uploaded successfully!', 'success')
    
    except ClientError as e:
        flash(f'Error uploading file: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unable to upload file. Please check your configuration: {str(e)}', 'error')
    
    return redirect(url_for('index'))


@app.route('/download/<filename>')
@login_required
def download(filename):
    """Handle file download"""
    try:
        # Sanitize filename to prevent path traversal attacks
        safe_filename = secure_filename(filename)
        
        # Get file from Digital Ocean Spaces
        file_obj = s3_client.get_object(Bucket=SPACES_BUCKET, Key=safe_filename)
        file_data = file_obj['Body'].read()
        
        # Create a BytesIO object
        file_stream = io.BytesIO(file_data)
        
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=safe_filename,
            mimetype='application/pdf'
        )
    
    except ClientError as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Unable to download file. Please check your configuration: {str(e)}', 'error')
        return redirect(url_for('index'))


if __name__ == '__main__':
    # Use debug mode from environment variable, default to False for safety
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
