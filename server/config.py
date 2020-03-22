class Config(object):
    DEBUG = False
    TESTING = False

class ProdConfig(Config):
    pass

class DevConfig(Config):
    DEBUG = True
    
    HOST = "0.0.0.0"
    PORT = "5985"
    MASTERNAME = "config"
    MASTERPASS = "password"
    MASTERKEY = "testomaster"

    SQLALCHEMY_TRACK_MODIFICATIONS = False 

    SQLALCHEMY_DATABASE_URI = "sqlite:///yabnet.sqlite3"
    UPLOAD_FOLDER = "./uploads"

    # If this is changed, the bot's configuration needs to be changed as well 
    FIRSTCONTACTKEY = "dudeOurRedteamalreadyhaslike30C2already-Friend"