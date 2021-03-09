from dotenv import load_dotenv
from pathlib import Path
import os

base_dir= Path(__file__).resolve().parent

env_file= base_dir / '.env' # tworze scieżke
#print(env_file)

load_dotenv(env_file)


class Config:
    # ustawiam w flaskenv
    # DEBUG=True #automatyczny restart systemu
    SECRET_KEY= os.environ.get('SECRET_KEY') #wyciągam z pliku secret key
    #generowanie secret key os.urandom(16).hex()
    SQLALCHEMY_DATABASE_URI=''
    # https://flask-sqlalchemy.palletsprojects.com/en/2.x/
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    PER_PAGE=5
    JWT_EXPIRED_MINUTES=30
#
#print(Config.SECRET_KEY)
#print(Config.SQLALCHEMY_DATABASE_URI)


#klasa dla środowiska testowego

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')


class TestingConfig(Config):
    DB_FILE_PATH= base_dir / 'tests' / 'test.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_FILE_PATH}' #dane sa zapisywane w pliku
    DEBUG=True
    TESTING=True


class ProductionConfig(Config):
    DB_HOST= os.environ.get('DB_HOST')
    DB_USERNAME= os.environ.get('DB-USERNAME')
    DB_PASSWORD= os.environ.get('DB-PASSWORD')
    DB_NAME=os.environ.get('DB_NAME')
    SQLALCHEMY_DATABASE_URI=f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4'

config= {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}



