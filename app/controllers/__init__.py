from itsdangerous import URLSafeTimedSerializer
from app import secret_key, os, mail
from flask_mail import Message
 
def generate_reset_token(email):
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

