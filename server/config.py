class Config(object):
    DEBUG = False
    TESTING = False

class ProdConfig(Config):
    DEBUG = False                # Change me to false if you want!
    
    HOST = "0.0.0.0"            # Change me if you want!
    PORT = "443"                # Change me if you want! 
    MASTERNAME = "admin"        # Change me, definitely!
    MASTERPASS = "password"     # Change me, definitely!
    MASTERKEY = "ChangeMeandCredentialsAsWell"   # Change me, definitely! 

    SQLALCHEMY_TRACK_MODIFICATIONS = False 

    #SQLALCHEMY_DATABASE_URI = "sqlite:///yabnet.sqlite3"
    """
    POSTGRES = {
        'user': 'postgres',
        'pw': 'password',
        'db': 'my_database',
        'host': 'localhost',
        'port': '5432'
    }
    """
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://test:test@db/test"
    UPLOAD_FOLDER = "./uploads"

    # If this is changed, the bot's configuration needs to be changed as well 
    FIRSTCONTACTKEY = "dudeOurRedteamalreadyhaslike30C2already-Friend"

class DevConfig(Config):
    DEBUG = True
    
    HOST = "0.0.0.0"
    PORT = "4444"
    MASTERNAME = "admin"
    MASTERPASS = "password"
    MASTERKEY = "testomaster"

    SQLALCHEMY_TRACK_MODIFICATIONS = False 

    SQLALCHEMY_DATABASE_URI = "sqlite:///yabnet.sqlite3"
    UPLOAD_FOLDER = "./uploads"

    # If this is changed, the bot's configuration needs to be changed as well 
    FIRSTCONTACTKEY = "dudeOurRedteamalreadyhaslike30C2already-Friend"
