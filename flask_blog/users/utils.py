import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flask_blog import mail

# this is for the update account
# grabs the file extension and the picture
# creates a place to save the picture
# saves the picture as a resized thumbnail and returns the filename
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex+file_ext
    picture_path = os.path.join(current_app.root_path, 'static/headshots', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

# helper function to create email
def send_reset_email(user):
    # grab the token
    token = user.get_reset_token()
    # specificy to, from, and subject of message
    msg = Message('Password Reset Request', sender='ytang07@gmail.com', recipients=[user.email])
    
    # craft the message body
    msg.body = f''' To reset your password, visit the following link
{url_for('users.reset_password', token=token, _external=True)}
If you did not make this request, please ignore this email
'''