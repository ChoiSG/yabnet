from flask_sqlalchemy import SQLAlchemy
from datetime import datetime  

db = SQLAlchemy()

class Bot(db.Model):
    #__tablename__ = 'bots'
    id = db.Column('bot_id', db.Integer, primary_key=True)
    ip = db.Column(db.String(128))
    os = db.Column(db.String(128))
    # cmds is a "list" of "Command" Model. The cmds and the bot_id from Command Model 
    # shows the one-to-many foreign key relationship between two tables. 
    cmds = db.relationship('Command', backref='bot', lazy=True)

    #TODO: Implement 'bot_unique_key' for authentication? 
    #unique_key = db.Column(db.String(128), default=<random_hash_created>)

    def __init__(self, ip, os):
        self.ip = ip 
        self.os = os
        self.cmds = []

    def get_id(self):
        return self.id

    def get_ip(self):
        return self.ip

    def get_os(self):
        return self.os

    def get_info(self):
        info = 'Bot[' + str(self.id) + '] IP: ' + self.ip + ' OS: ' + self.os
        return info

    def get_commands(self):
        result = '' 
        i = 0 
        for command in self.cmds:
            tmp = '[' + str(i) +'] ' + command.cmd + '\n'
            result += tmp 
            i+=1 

        return result 

    def jsonbot(self):
        # TODO: Create a function which returns a jsonify version of the bot information 
        pass 

class Command(db.Model):
    id = db.Column('cmd_id', db.Integer, primary_key=True)
    cmd = db.Column(db.String(128))
    bot_id = db.Column(db.Integer, db.ForeignKey('bot.bot_id'))
    bot_ip = db.Column(db.String(128))
    timestamp = db.Column(db.String(50)) 
    latest = db.Column(db.Boolean, default=False)
    result = db.Column(db.String(500))

    def __init__(self, cmd, bot_id, bot_ip):
        self.cmd = cmd 
        self.bot_id = bot_id 
        self.bot_ip = bot_ip 
        self.timestamp = str(datetime.now())
        self.latest = False
        self.result = ''

    def set_latest_true(self):
        self.latest = True

    def set_latest_false(self):
        self.latest = False 

    def set_result(self, result):
        self.result = result 

    def get_info(self):
        info = '[Command Info] [' + self.timestamp + '] Bot_id: ' + str(self.bot_id) + ' Command Issued: ' + self.cmd
        #result = self.result 

        return info 
        #return '\n'.join([info, result])
