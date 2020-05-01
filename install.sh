#!/bin/sh

# Installing dependencies if the current box doesn't have one.
# Based on UBUNTU
sudo add-apt-repository ppa:longsleep/golang-backports
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update -y
apt-get install -y python3-pip git golang-go docker-ce libpq-dev
sudo curl -L "https://github.com/docker/compose/releases/download/1.25.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
sudo pip3 install --upgrade pip
pip3 install -r requirements.txt
