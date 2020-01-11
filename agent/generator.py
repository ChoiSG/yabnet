from string import Template
from colorama import Fore,Style
import PyInstaller.__main__
import argparse
import sys 
import subprocess

"""
Name: generator.py 
Description: Generator for creating agent python files with specific ip address and port. 
Also supports freezing the agents, making the agent python file into an executable. 


"""

def print_green(string):
    print(Fore.GREEN + string + Style.RESET_ALL)

def print_red(string):
    print(Fore.RED + string + Style.RESET_ALL)

def parse():
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

def generate(template, newfile, serverip, port):
    new = ''

    for line in open(template, 'rt'):
        if '<SERVERIP>' in line:
            new += line.replace('<SERVERIP>', serverip)
            continue
        elif '<PORT>' in line:
            new += line.replace('<PORT>', port)
            continue

        new += line 

    try:
        with open(newfile, 'w') as fd:
            fd.write(new)
        print_green("[+] Generating agent_deploy.py successful.")

    except Exception as e:
        print_red("[-] " + str(e))

def freeze():
    try: 
        print_green("[+] Freezing agent_deploy. This will take some time...")
        proc = subprocess.Popen('pyinstaller -F --clean "/opt/yabnet/agent/agent_deploy.py"', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        print(proc.stderr.read().decode('utf-8'))

        print_green("[+] Freezing agent_deploy successful.")
        print_green("[+] Executable Path: /opt/yabnet/agent/dist/agent_deploy")
    except Exception as e: 
        print_red("[-] " + str(e))
        exit()


def main():
    # HARDCODING FTW (shouldn't do this) 
    TEMPLATE = '/opt/yabnet/agent/agent.txt'
    NEWFILE = '/opt/yabnet/agent/agent_deploy.py'

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