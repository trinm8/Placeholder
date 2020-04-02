from flask import render_template, current_app
from ..emails import send_email

def send_password_reset_email(user, email):
    token = user.get_reset_password_token()
    send_email('[PlaceHolder] Reset Your Password',
               sender=current_app.config['ADMINS'][0],
               recipients=[email],
               text_body=render_template('auth/email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('auth/email/reset_password.html',
                                         user=user, token=token))