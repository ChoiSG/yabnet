# Yabnet
Yet Another Botnet, PoC created for educational purposes only.

## Disclaimer
Yabnet is a proof of concept tool which is only created for educational purposes in classroom and cybersecurity related competitions. This tool is not created, nor is good enough for any real world usage. I do not condone use of this tool anything other than educational purposes. Using any of the files of yabnet in/against a system that you do not own is illegal, and you will get caught.

## Under Construction
**Yabnet is currently under construction.**

## Installation 

**Due to laziness, yabnet currently requires to be installed in the /opt directory.**

```
cd /opt
git clone https://github.com/choisg/yabnet.git
cd /opt/yabnet
chmod +x install.sh
./install.sh
```

## Operation 

**Server setup**
```
<Change MASTERNAME and MASTERPASSWORD in server.py>
<Default is admin:password>

python3 /server/server.py
```
**Agent setup**

```
python3 ./agent/generator.py -i <server_ipaddress> -p <server_port>

Example) python3 ./agent/generator.py -i 192.168.204.128 -p 5000
```

`<Transfer ./agent/dist/agent_deploy_staticx to the target machine and run it>`

**Master setup**

After server and the agent is setup, launch the master console.
```
python3 /master/master.py
console# login -r localhost -u user -p pass
console# list
``` 

`< All master console commands have help flag>`
`Example) push -h`

