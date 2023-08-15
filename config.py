import os, cloudinary

class Db_config(object):
    dialect = os.getenv('DB_DIALECT')
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD') 
    host = os.getenv('DB_HOST')
    database = os.getenv('DB_DATABASE')

    SQLALCHEMY_DATABASE_URI = dialect+'://'+username+':'+password+'@'+host+'/'+database

class Cloudinary_config(object):
    cloudinary.config(cloud_name = os.getenv('CLOUD_NAME'), api_key=os.getenv('API_KEY'), 
    api_secret=os.getenv('API_SECRET'))
    
