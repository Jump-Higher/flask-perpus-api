from itsdangerous import URLSafeTimedSerializer
from app import secret_key, os, mail, response_handler,app
from flask_mail import Message
from app.models import select_users_role

@app.after_request
def add_header(response):
    response.headers['ngrok-skip-browse-warning'] = ''
    return response

def gender():
    gender = ['female','male','prefer not say']
    return gender
# Check update 
def check_update(json_body, data, array):
    check_update = all(json_body[field] == getattr(data, field) for field in array)
    return check_update

# CRUL 
def super_auth():
    authorized_roles = str({select_users_role('SUPER_ADMIN_ROLE')})
    return authorized_roles

def public_auth():
    authorized_roles = str({select_users_role('SUPER_ADMIN_ROLE'), 
                            select_users_role('USER_ROLE'),
                            select_users_role('ADMIN_ROLE')})
    return authorized_roles


def admin_auth():
    authorized_roles = str({select_users_role('SUPER_ADMIN_ROLE'), 
                            select_users_role('ADMIN_ROLE')})
    return authorized_roles

def user_auth():
    authorized_roles = str({select_users_role('USER_ROLE')})
    return authorized_roles

def generate_token(email):
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(email)

def send_email(email,subjectBody,htmlBody):
    send = Message(
                 subject = subjectBody,
                 sender = os.getenv('MAIL_USERNAME'),
                 recipients = [email], 
                 html=htmlBody
            )
    return mail.send(send)

def reset_password_body(url,user):
    html_body = f'''
    <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="background-color: #f0f0f0; padding: 20px; border-radius: 5px;">
                <h1 style="color: #007BFF;">Reset Your Password</h1>
                <p>Hello {user},</p>
                <p>A password reset for your account was requested.</p>
                <p>Please click the button below to change your password.</p>
                <p style="text-align: left;">
                    <a href="{url}" style="display: inline-block; background-color: #007BFF; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        Reset Password
                    </a>
                </p>
                <p>Note that this link is valid for 1 hour. After the time limit has expired, you will have to resubmit the request for a password reset.</p>
                <p>If you didn't request a password reset, please ignore this email.</p>
            </div>
        </body>
    </html>
    '''
    return html_body


def activation_body(url, user):
    html_body = f'''
    <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="background-color: #f0f0f0; padding: 20px; border-radius: 5px;">
                <h1 style="color: #007BFF;">Activate Your Account</h1>
                <p>Hello {user},</p>
                <p>Thank you for signing up with us!</p>
                <p>Please click the button below to activate your account.</p>
                <p style="text-align: left;">
                    <a href="{url}" style="display: inline-block; background-color: #007BFF; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        Activate Account
                    </a>
                </p>
                <p>Note that this activation link is valid for 1 hour. After the time limit has expired, you might need to request a new activation link.</p>
                <p>If you didn't sign up for an account, please ignore this email.</p>
            </div>
        </body>
    </html>
    '''
    return html_body
