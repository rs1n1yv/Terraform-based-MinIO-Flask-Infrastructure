import os
from flask import Flask, request, redirect, render_template_string
import boto3
from dotenv import load_dotenv

# Load environment variables from .env if available
load_dotenv()

app = Flask(__name__)

# Initialize the S3 client for MinIO
s3 = boto3.client(
    's3',
    endpoint_url=os.getenv("MINIO_ENDPOINT"),
    aws_access_key_id=os.getenv("MINIO_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("MINIO_SECRET_KEY")
)

bucket = os.getenv("MINIO_BUCKET")

# Ensure the specified bucket exists
try:
    s3.head_bucket(Bucket=bucket)
except:
    s3.create_bucket(Bucket=bucket)

UPLOAD_FORM = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MinIO File Upload</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(to right, #2980b9, #6dd5fa);
                color: #333;
                text-align: center;
                padding-top: 50px;
            }
            .container {
                background: white;
                border-radius: 10px;
                padding: 40px;
                max-width: 500px;
                margin: auto;
                box-shadow: 0px 0px 20px rgba(0,0,0,0.2);
            }
            input[type="file"] {
                margin-bottom: 15px;
            }
            input[type="submit"] {
                background-color: #3498db;
                border: none;
                color: white;
                padding: 10px 20px;
                text-transform: uppercase;
                border-radius: 5px;
                cursor: pointer;
            }
            input[type="submit"]:hover {
                background-color: #2980b9;
            }
            p {
                font-size: 1.1em;
                margin-top: 20px;
            }
            a {
                display: inline-block;
                margin-top: 15px;
                text-decoration: none;
                color: #3498db;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Secure File Upload to MinIO</h2>
            <form method="POST" enctype="multipart/form-data">
                <input type="file" name="file" required><br>
                <input type="submit" value="Upload">
            </form>
        </div>
    </body>
    </html>
'''

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            try:
                s3.put_object(
                    Bucket=bucket,
                    Key=file.filename,
                    Body=file.read(),
                    ServerSideEncryption='AES256'  # Enable server-side encryption
                )
                return render_template_string(UPLOAD_FORM + f"<p>✅ <strong>{file.filename}</strong> uploaded successfully with encryption.</p><a href='/'>Upload another</a>")
            except Exception as e:
                return render_template_string(UPLOAD_FORM + f"<p>❌ Upload failed: {str(e)}</p><a href='/'>Try again</a>")
    return render_template_string(UPLOAD_FORM)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

