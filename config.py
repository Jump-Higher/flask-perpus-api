import os, cloudinary

class Db_config(object):
    dialect = os.getenv('DB_DIALECT','postgresql')
    username = os.getenv('DB_USERNAME','bhhtclox')
    password = os.getenv('DB_PASSWORD','8d0hfkG_ivlr_LDupiRCTcVogNnh3Buk') 
    host = os.getenv('DB_HOST','satao.db.elephantsql.com')
    database = os.getenv('DB_DATABASE','bhhtclox')

    SQLALCHEMY_DATABASE_URI = f'{dialect}://{username}:{password}@{host}/{database}?sslmode=require'
class Cloudinary_config(object):
    cloudinary.config(cloud_name = os.getenv('CLOUD_NAME'), api_key=os.getenv('API_KEY'), 
    api_secret=os.getenv('API_SECRET'))
    
class Mail_config(object):
        MAIL_SERVER = os.getenv('MAIL_SERVER')
        MAIL_PORT = os.getenv('MAIL_PORT')
        MAIL_USE_TLS = False
        MAIL_USE_SSL = True
        MAIL_USERNAME = os.getenv('MAIL_USERNAME')
        MAIL_PASSWORD =  os.getenv('MAIL_PASSWORD')