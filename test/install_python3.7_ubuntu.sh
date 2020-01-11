#!/bin/sh

sudo apt update -y 
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update -y 
sudo apt install -y python3.7
