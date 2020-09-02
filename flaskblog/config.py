import os

class Config:
	SECRET_KEY = '3f5867adcbf93af092a40d57178024ac'
	SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
	MAIL_SERVER = "smtp.gmail.com"
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USERNAME = "imurdad498@gmail.com"
	MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')