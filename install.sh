#!/bin/sh

# Install required packages - Pandoc is required for staticx 
apt-get install -y python3-pip
sudo pip3 install --upgrade pip
apt-get install -y pandoc
pip3 install -r requirements.txt
