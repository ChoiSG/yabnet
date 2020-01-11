#!/bin/sh

sudo apt update -y 
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update -y 
sudo apt install python3.7
