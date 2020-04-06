import re 

def generatehosts(internal, cloud, teams, internalBox, cloudBox, hostname):
    internalTarget = []
    cloudTarget = []

    hostdict = {host: list([]) for host in hostname}

    # Generating IP addresses for internal boxes... 
    for teamNum in teams:
        for internalip in internalBox:
            ip = internal.replace('x',teamNum)
            ip = ip.replace('y',internalip)
            
            internalTarget.append(ip)

    # Generating IP addresses for cloud boxes... 
    for teamNum in teams:
        for boxip in cloudBox:
            ip = cloud.replace('x', teamNum)
            ip = ip.replace('y', boxip)

            cloudTarget.append(ip)

    return internalTarget,cloudTarget,hostdict


def findHost(ip, regexString):
    check = re.compile(regexString)
    result = check.search(ip)

    if result:
        return True
    else:
        return False 


# smh on this algorithm but I had two hours to fix all my stuff 
def categorize(hostdict, internalTarget, cloudTarget):
    for ip in internalTarget:
        if findHost(ip, "\d{1,3}\.\d{1,3}\.1\.2"):
            hostdict['annebonny'].append(ip)
        elif findHost(ip, "\d{1,3}\.\d{1,3}\.1\.3"):
            hostdict['williamkidd'].append(ip)
        elif findHost(ip, "\d{1,3}\.\d{1,3}\.1\.4"):
            hostdict['calicojack'].append(ip)
        elif findHost(ip, "\d{1,3}\.\d{1,3}\.1\.5"):
            hostdict['maryread'].append(ip)
        elif findHost(ip, "\d{1,3}\.\d{1,3}\.1\.6"):
            hostdict['edwardteach'].append(ip)
        elif findHost(ip, "\d{1,3}\.\d{1,3}\.1\.7"):
            hostdict['captaincrapo'].append(ip)
        elif findHost(ip, "\d{1,3}\.\d{1,3}\.1\.8"):
            hostdict['canoot'].append(ip)
        
    for ip in cloudTarget:
        if findHost(ip, "\d{1,3}\.\d{1,3}\.2\.2"):
            hostdict['nemo'].append(ip)
        elif findHost(ip, "\d{1,3}\.\d{1,3}\.2\.3"):
            hostdict['gunner'].append(ip)
        elif findHost(ip, "\d{1,3}\.\d{1,3}\.2\.4"):
            hostdict['laurellabonaire'].append(ip)
        elif findHost(ip, "\d{1,3}\.\d{1,3}\.2\.5"):
            hostdict['lockelamora'].append(ip)
        elif findHost(ip, "\d{1,3}\.\d{1,3}\.2\.6"):
            hostdict['hook'].append(ip)

    return hostdict

def main():
    internal = "10.x.1.y"
    cloud = "10.x.2.y"

    teams = ['1','2','3','4','5','6','7','8','9','10']
    internalBox = ['2','3','4','5','6','7','8']
    cloudBox = ['2','3','4','5','6']

    hostname = ['annebonny', 'williamkidd', 'calicojack', 'maryread', 'edwardteach', 'captaincrapo', 'canoot', 'nemo', 'gunner', 'laurellabonaire','lockelamora','hook']

    internalTarget = []
    cloudTarget = []
    hostdict = {} 

    internalTarget,cloudTarget,hostdict = generatehosts(internal, cloud, teams, internalBox, cloudBox, hostname)

    hostdict = categorize(hostdict, internalTarget, cloudTarget)

    for host in hostname:
        print("========== [ " + host + " ] ==========")
        for ip in hostdict[host]:
            print(ip)
        print("\n")

    for host in hostname:
        print(host + " = ", hostdict[host])

    """
    # Use this if needed
    for ip in internalTarget:
        print(ip)
    for ip in cloudTarget:
        print(ip)
    print(internalTarget)
    print(cloudTarget)
    print(hostname)
    """

    print(internalTarget)
    print(cloudTarget)
    print(hostname)

if __name__ == '__main__':
    main()
