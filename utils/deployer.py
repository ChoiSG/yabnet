import sys 
import paramiko
import threading
import argparse
import socket
import winrm
from winrm.protocol import Protocol
from scp import SCPClient
from colorama import Fore,Style

"""
    Name: deployer.py 
    Description: Worse version of Fabric, Worse version of detcord. TBH I should just use Fabric or detcord. But I guess now I kind of know 
    how to use paramiko, hey I learned something, right? Gotta reinvent all the wheels! 
"""

def print_green(string):
    print(Fore.GREEN + string + Style.RESET_ALL)

def print_blue(strings):
    try:
        print(Fore.BLUE + strings + Style.RESET_ALL)
    except Exception as e:
        print(Fore.BLUE + strings.encode('ascii',errors='ignore').decode('ascii') + Style.RESET_ALL)

def print_red(string):
    try:
        print(Fore.BLUE + string + Style.RESET_ALL)
    except Exception as e:
        print(Fore.BLUE + string.encode('ascii',errors='ignore').decode('ascii') + Style.RESET_ALL)


def generateTarget(common, cloud_common, teams, targets, cloud_targets):
    """
    Description: Returns a list of target ipv4 addresses based on team number and hosts

    Param:
        - [str]      common: Common octet of the competition  
        - [list/str] teams: List of teams in string 
        - [list/str] hosts: Last octet of the target machines 
    """

    total = []

    for team in teams:
        for target in targets:
            final = common + '.' + team + '.' + target 
            total.append(final)

        for cloud_target in cloud_targets:
            final = cloud_common + '.' + team + '.' + cloud_target
            total.append(final)

    return total 

def windows(ip, user, pwd, command):
    """
    p = Protocol(
        endpoint="http://"+ip+":5985/wsman",
        transport='ntlm',
        username=user,
        password=pwd,
        server_cert_validation='ignore'
    )
    
    shell_id = p.open_shell()
    command_id = p.run_command(shell_id, command)
    stdout, stderr, status_code = p.get_command_output(shell_id, command_id)
    p.cleanup_command(shell_id, command_id)
    p.close_shell(shell_id)
    print(stderr)
    """

    print_green("[IP] - " + str(ip) + " [Command] - " + command)

    try:
        # The key was ntlm transport. 
        session = winrm.Session(ip, auth=(user,pwd), transport='ntlm')
        result = session.run_ps(command)
        print(result.std_out.decode("utf-8"))
        #print(result.std_err.decode("utf-8"))
    
    except Exception as e:
        print_red("[-] Error: " + str(e))


# This needs to be changed manually. Implementation will come soon(tm)
def yabnetWindows():
    ps_script = """ [[REDACTED]]
    """

    return ps_script

def exec(ssh, command, sudo, winrm):
    if winrm:
        # implementation for another day 
        pass 
    
    # Using ssh 
    else:
        try:
            if sudo: 
                print_green("\n[IP] - " + ssh.get_transport().getpeername()[0] + " [Command] - " + command)
                stdin, stdout, stderr = ssh.exec_command("sudo -S -p '' -- sh -c \"" + command + "\"", get_pty=True)
                stdin.write(PASSWORD + "\n")
                stdin.flush()
                return stdin, stdout, stderr 

            else:
                print_green("\n[IP] - " + ssh.get_transport().getpeername()[0] + " [Command] - " + command)
                stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
                return stdin, stdout, stderr 

        except Exception as e:
            print_red(str(e))
            return '','','' 

# Actually drop the payload, change the file permission, and execute it 
def drop(ssh, localFile, remoteLocation):    
    scp = SCPClient(ssh.get_transport())

    # Drop list of files 
    if (isinstance(localFile, list) and isinstance(remoteLocation,list)):
        localFileList = localFile
        remoteLocList = remoteLocation
        for lfile, rloc in zip(localFileList, remoteLocList):
            try:
                scp.put(lfile, rloc)
            except Exception as e:
                print("[-] ", str(e))
            
            print_green("[+] [IP] - " + ssh.get_transport().getpeername()[0] + " | Successfully dropped: " + lfile + " | Dest: " + rloc)

    # Drop single file 
    else:
        try:
            scp.put(localFile, remoteLocation)
        except Exception as e:
            print("[-] " , str(e))

        print_green("[+] [IP] - " + ssh.get_transport().getpeername()[0] + " | Successfully dropped: " + localFile + " | Dest: " + remoteLocation)
    

def sshConnect(ip, user, pwd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(ip, username=user, password=pwd, timeout=4)
    except paramiko.AuthenticationException:
        print("[-] Authentication failed.")
        return "[-]"
    except (paramiko.ssh_exception.NoValidConnectionsError, socket.timeout) as e :
        print("[-] No valid connection, socket timed out", str(e))
        return "[-]"
    except  paramiko.ssh_exception.SSHException as e:
        print("[-] Check ip, user, pwd. (-u, -p, -i). Exception: ",str(e))
        return "[-]"
    
    print_green("[+] Login successful [" + ip + "] [" + user + ":" + pwd + "]")

    return ssh 

def parseHostFile(filename, user, pwd):
    """
    return list of paramiko ssh clients 
    """

    fd = open(filename, 'r')
    sshList = []
    for host in fd:
        host = host.strip()
        ssh = sshConnect(host, user, pwd)
        if ssh != "[-]":
            sshList.append(ssh)
    
    fd.close()
    #print("[DEBUG] SSHList debug = ", sshList)
    return sshList


def parseStdout(stdout):
    result = ""
    for line in stdout:
        result += line
    return result 

    
# Parsing arguments 
def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u','--user', type=str, dest='u', help='Default competition username for login')
    parser.add_argument('-p','--password',type=str, dest='p', help='Default competition password for login')
    parser.add_argument('-i','--ipaddr', type=str, dest='i', help='IP Address to deploye to')
    parser.add_argument('-f','--file', type=str,  dest='f', help='Location of the file to be dropped')
    parser.add_argument('-d','--destination', type=str, dest='d', help='Remote destination location to drop the file')
    parser.add_argument('-c','--command', type=str, dest='c', help='Command to be executed')
    parser.add_argument('-iL','--ipfile',type=str, dest='iL', help='File name which contains list of ip addresses')
    parser.add_argument('-g','--generate', action="store_true", dest='g', help='Generate a list of ip addresses for competition')
    parser.add_argument('-s','--sudo', action="store_true", dest='s', help='Run commands with sudo, if the user is sudoer')
    #parser.add_argument('--ssh')
    parser.add_argument('-w', '--winrm', action="store_true", default=False, dest='w', help='Uses winrm module to connect to remote Windows machines')

    if len(sys.argv) < 2:
        parser.print_help()
        exit(1)

    try:
        arguments = parser.parse_args()
    except Exception as e:
        print("[-] Error occurred: ", str(e))
        exit()

    return arguments 

def main():

    # Parse all the arguments 
    args = parse()

    # Set all argument variables - What is this abomination  
    user = args.u
    pwd = args.p
    ip = args.i 
    localFile = args.f
    if localFile != None:
        localFile = localFile.split(",")    
    remoteLocation = args.d
    if remoteLocation != None:
        remoteLocation = remoteLocation.split(",")
    command = args.c
    hostFile = args.iL
    generate = args.g
    winrm = args.w
    sudo = args.s 

    global PASSWORD
    PASSWORD = pwd 


    # ============= Main logic Starts =============

    # For multiple, hosts file 
    if args.iL != None:
        # Multiple Windows WinRM 
        if winrm:
            for host in open(hostFile).readlines():
                host = host.strip()
                windows(host, user, pwd, command)
        
        # Multiple Linux SSH 
        else:
            sshList = parseHostFile(hostFile, user, pwd)

            # TODO: Multiprocessing with pools will come later
            if args.c != None:
                for ssh in sshList:
                    stdin, stdout, stderr = exec(ssh, command, sudo, winrm)
                    print_blue(parseStdout(stdout).decode("utf-8"))
            
            if args.f != None and args.d != None:
                for ssh in sshList:
                    drop(ssh, localFile, remoteLocation)


    # For single ssh connection  
    else:
        # Single Windows WinRM 
        if winrm:
            windows(ip,user,pwd,command)

        # Single Linux SSH 
        else:
            ssh = sshConnect(ip, user, pwd)

            # If that single ssh connection failed, exit the program. 
            if ssh == "[-]":
                exit(1) 

            if args.c != None:
                stdin, stdout, stderr = exec(ssh, command, sudo, winrm)

                print_blue(parseStdout(stdout))

            if args.f != None and args.d != None:
                drop(ssh, localFile, remoteLocation)
    
    """
    # SSH Login Sanity check 
    for target in targets:
        thread = threading.Thread(target=sshAttempt, args=(target,USER,PASSWORD))

    print("\n[+] Preparing to actually drop payload ...\n")
    time.sleep(5)

    # Actually drop payloads 
    for target in targets:
        thread = threading.Thread(target=drop, args=(target,USER,PASSWORD,REMOTE_LOCATION))

    print("\n\n\n[+] Agents all dropped. Have fun.\n\n\n")
    """


if __name__ == '__main__':
    main()