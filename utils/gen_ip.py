import re 
import sys 
import time
import json

class Box:
    name = ""
    ip = ""
    teamNum = ""
    os = ""
    version = "" 

    def __init__(self, name, ip, teamNum, os):
        self.name = name 
        self.ip = ip
        self.teamNum = teamNum
        self.os = os 

    def jsonBox(self):
        return {
            'name': self.name,
            'ip': self.ip,
            'teamNum': self.teamNum,
            'os': self.os 
        } 


def build(internalorcloud, teams, boxDict, os):

    boxList = []

    for team in teams:
        for win in boxDict:
            ip = internalorcloud.replace('x', team)
            ip = ip.replace('y', win['ip'])
            box = Box(win['name'], ip, team, os)
            boxList.append(box)

    return boxList

def parseBoxesJson(filename):
    teams = []
    internal_win = []
    internal_lin = []
    cloud_win = []
    cloud_lin = []
    misc = [] 

    with open(filename) as fd:
        data = json.load(fd)
        teams = data['teams']
        internal_win = data['internal_win']
        internal_lin = data['internal_lin']
        cloud_win = data['cloud_win']
        cloud_lin = data['cloud_lin']

    fd.close()
    
    return teams, internal_win, internal_lin, cloud_win, cloud_lin, misc 

def writeHostFile(totalBoxList, teams, os):
    
    for team in teams:
        ip = ""

        for box in totalBoxList:
            if box.teamNum == team and box.os == os:
                ip += box.ip
                ip += "\n"
        
        filename = "team" + team + "_" + os + ".txt"
        with open(filename, 'w') as fd:
            fd.write(ip)
        fd.close 
        


def main():
    if len(sys.argv) < 2:
        print("USAGE: {} <boxes.json>".format(sys.argv[0]))
        quit(1)

    internal = "10.x.1.y"
    cloud = "10.x.2.y"

    # Build box templates
    teams, internal_win, internal_lin, cloud_win, cloud_lin, misc = parseBoxesJson(sys.argv[1])

    # Actually build boxes with names, ip, teamNum, os 
    internalWinBox = build(internal,teams,internal_win,"windows")
    internalLinBox = build(internal,teams,internal_lin,"linux")
    cloudWinBox = build(cloud,teams,cloud_win,"windows")
    cloudLinBox = build(cloud,teams,cloud_lin,"linux")

    # Gain a list(dictionary) with all of the boxes for the competition 
    totalBoxList = internalWinBox + internalLinBox + cloudWinBox + cloudLinBox

    for box in totalBoxList:
        print(box.jsonBox())

    print("\n\n")
    print("This will create hostfile for each team's windows and linux")
    print("~20 .txt files will be created.")
    print("CTRL+C to exit.\n\n")

    time.sleep(10)
    writeHostFile(totalBoxList, teams, "windows")
    writeHostFile(totalBoxList, teams, "linux")

    print("DONE! All host files per team + per OS have been created.")
    print("===========================================")

if __name__ == '__main__':
    main()
