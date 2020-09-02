import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail


def save_picture(picture_path):
   random_name = secrets.token_hex(8)
   _,file_ext = os.path.splitext(picture_path.filename)
   picture_f = random_name + file_ext
   path = os.path.join(current_app.root_path,'static/icon',picture_f)
   output_size = (150,150)
   reduced_image = Image.open(picture_path)
   reduced_image.thumbnail(output_size)

   reduced_imagefp.save(path)
   return picture_f

def send_email(user):
  token = user.get_reset_token()
  msg = Message('Password rest request', sender='noreply@demo.com',
                 recipients=[user.email])
  msg.body = f"""To reset your password, visit following link:
  {url_for('users.reset_token', token=token, _external=True)}
  """
  mail.send(msg)