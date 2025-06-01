import os
import json
from flask import Flask, request, redirect, make_response, render_template_string
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# MinIO configuration
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

LOGIN_FORM = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login Session</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(to right, #8e44ad, #3498db);
                color: #fff;
                text-align: center;
                padding-top: 50px;
            }
            .container {
                background: white;
                color: #333;
                border-radius: 10px;
                padding: 40px;
                max-width: 400px;
                margin: auto;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            input[type="text"], input[type="submit"] {
                padding: 10px;
                margin: 10px 0;
                width: 80%;
                border-radius: 5px;
                border: 1px solid #ccc;
            }
            input[type="submit"] {
                background-color: #8e44ad;
                color: white;
                border: none;
                cursor: pointer;
            }
            input[type="submit"]:hover {
                background-color: #732d91;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Login</h2>
            <form method="POST">
                <input type="text" name="username" placeholder="Enter your name" required><br>
                <input type="submit" value="Login">
            </form>
        </div>
    </body>
    </html>
'''

@app.route('/')
def index():
    session_id = request.cookies.get("session_id")
    if session_id:
        try:
            response = s3.get_object(Bucket=bucket, Key=session_id)
            session_data = json.loads(response['Body'].read())
            username = session_data.get('username', 'Guest')
            return f"<h2>👋 Welcome back, <strong>{username}</strong>!</h2><a href='/logout'>Logout</a>"
        except:
            return "<p>Session not found or expired. <a href='/login'>Login again</a></p>"
    else:
        return "<p>Welcome! Please <a href='/login'>login</a> to continue.</p>"

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        session_id = os.urandom(16).hex()
        session_data = {"username": username}
        s3.put_object(Bucket=bucket, Key=session_id, Body=json.dumps(session_data))
        resp = make_response(redirect('/'))
        resp.set_cookie("session_id", session_id)
        return resp
    return render_template_string(LOGIN_FORM)

@app.route('/logout')
def logout():
    resp = make_response("<p>You've been logged out. <a href='/login'>Login again</a></p>")
    resp.set_cookie("session_id", "", expires=0)
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

