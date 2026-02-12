# fuzzy-robot - PDF Manager

A simple Python web application for uploading and downloading PDF files, with authentication and Digital Ocean Spaces integration.

## Features

- 🔐 **Authentication** - Secure login system to prevent abuse
- 📤 **PDF Upload** - Upload PDF files to Digital Ocean Spaces
- 📥 **PDF Download** - Download previously uploaded files
- 📋 **File Listing** - View all uploaded files with names and timestamps
- ☁️ **Cloud Storage** - Files stored securely in Digital Ocean Spaces (S3-compatible)

## Prerequisites

- Python 3.8 or higher
- Digital Ocean account with Spaces enabled
- A Digital Ocean Spaces bucket created

## Installation

1. Clone the repository:
```bash
git clone https://github.com/stevenhelms/fuzzy-robot.git
cd fuzzy-robot
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

Edit the `.env` file and update the following values:

- `SECRET_KEY`: A random secret key for Flask sessions (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
- `AUTH_USERNAME`: Username for authentication
- `AUTH_PASSWORD`: Password for authentication
- `SPACES_REGION`: Your Digital Ocean Spaces region (e.g., `nyc3`, `sfo3`, `sgp1`)
- `SPACES_ENDPOINT`: Your Spaces endpoint URL (e.g., `https://nyc3.digitaloceanspaces.com`)
- `SPACES_KEY`: Your Spaces access key
- `SPACES_SECRET`: Your Spaces secret key
- `SPACES_BUCKET`: Your Spaces bucket name

## Digital Ocean Spaces Setup

1. Log in to your Digital Ocean account
2. Navigate to **Spaces** in the left sidebar
3. Click **Create a Space**
4. Choose your region and create a unique bucket name
5. Go to **API** → **Spaces Keys** to generate access keys
6. Copy the key and secret to your `.env` file

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Log in with the credentials you set in the `.env` file

4. Upload PDF files using the upload form

5. View the list of uploaded files with timestamps

6. Download files by clicking the download link

## Deployment to Digital Ocean

### Using App Platform

1. Push your code to GitHub
2. In Digital Ocean, go to **App Platform**
3. Create a new app and connect your GitHub repository
4. Configure environment variables in the app settings
5. Deploy the app

### Using a Droplet

1. Create a Droplet with Ubuntu
2. SSH into your droplet
3. Install Python and dependencies
4. Clone your repository
5. Set up environment variables
6. Use a production server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

7. Set up Nginx as a reverse proxy
8. Configure SSL with Let's Encrypt

## Security Notes

- Change the default `SECRET_KEY` in production
- Use strong passwords for authentication
- Consider implementing more robust authentication (OAuth, JWT, etc.) for production use
- Enable HTTPS in production
- Regularly rotate your Digital Ocean Spaces keys
- Set appropriate CORS and bucket policies

## License

This project is open source and available under the MIT License.
