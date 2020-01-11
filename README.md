# Yabnet
Yet Another Botnet, PoC created for educational purposes only.

## Disclaimer
Yabnet is a proof of concept tool which is only created for educational purposes in classroom and cybersecurity related competitions. This tool is not created, nor is good enough for any real world usage. I do not condone use of this tool anything other than educational purposes. Using any of the files of yabnet in/against a system that you do not own is illegal, and you will get caught.

## Under Construction
**Yabnet is currently under construction.**

## Installation 

**Yabnet requires python3.7++
Due to laziness, yabnet currently requires to be installed in the /opt directory.**

```
cd /opt
git clone https://github.com/choisg/yabnet.git
cd /opt/yabnet
chmod +x install.sh
./install.sh
```

## Operation 

###Server setup
```
<Change MASTERNAME and MASTERPASSWORD in /server/server.py>
<Default is admin:password>

python3 ./server/server.py
```

###Agent setup

There are two options to setup agents. One is to create a static executable through freezing. Another way is to just simply create a `.py` file.

**1. Freezing - Executable**
```
python3 /opt/yabnet/agent/generator.py -i <server_ipaddress> -p <server_port> -f 
Example) python3 /opt/yabnet/agent/generator.py -i localhost -p 5000 -f 
```

**2. Plain python file**
```
python3 /opt/yabnet/agent/generator.py -i <server_ipaddress> -p <server_port>
Example) python3 /opt/yabnet/agent/generator.py -i localhost -p 5000
```

**Transfer the agent file** 

Transfer either `/opt/yabnet/agent/dist/agent_deploy_staticx` or `/opt/yabnet/agent/agent_deploy.py` to the target machine and run it

###Master setup

After server and the agent is setup, launch the master console.
Default credential for master is `admin:password`
```
python3 ./master/master.py
console# login -r localhost -u <user> -p <password>
console# list
``` 

`< All master console commands have help flag>`
`Example) push -h`

## Demo
<insert youtubelink here>