# yabnet
Yet Another Botnet, PoC created for educational purposes only.

## Installation 

`git clone https://github.com/choisg/yabnet.git`

`pip3 install -r requirements.txt`

## Operation 

Currently, yabnet is under construction. That means yabnet is meant to work on localhost environment.

**Server setup**
`python3 /server/server.py`

**Agent setup**
`< Change the URL in the agent.py >`

`python3 agent.py` 


**Master setup**
After server and the agent is setup, launch the master console 
`python3 /master/master.py`

`console# login -r localhost -u user -p pass`

`console# list` 

`< All master console commands have help flag. 
broadcast  commands  exit  list  login  push  quit
ex) push -h `

