import os
import csv
import requests
import collections
from maya import cmds

class ProjectManager:

    # Fetches and reads the assets csv file.
    assets_csv_url = 'https://docs.google.com/spreadsheets/d/1-a2K2BXe1uCPinImkMx5qVsuJcKoylxrWBqQxNl2yA0/pub?gid=797696484&single=true&output=csv'
    #req_assets_csv = requests.get(assets_csv_url, verify='C:/apps/python/2.7.8/Lib/site-packages/certifi/cacert.pem')
    req_assets_csv = requests.get(assets_csv_url, timeout=10)
    assets_text = req_assets_csv.iter_lines()

    shots_csv_url= 'https://docs.google.com/spreadsheets/d/1-a2K2BXe1uCPinImkMx5qVsuJcKoylxrWBqQxNl2yA0/pub?gid=1343957549&single=true&output=csv'
    #req_shots_csv = requests.get(shots_csv_url, verify='C:/apps/python/2.7.8/Lib/site-packages/certifi/cacert.pem')
    req_shots_csv = requests.get(shots_csv_url, timeout=10)
    shots_text = req_shots_csv.iter_lines()



    # Path to project folder.
    #projectFolder = 'C:/apps/autodesk/2017/Maya2017/plug-ins/camd/scripts/teamProduction/'
    projectFolder = '/Users/EricAndersson/Documents/Projects/Scripting/Python/Maya/teamProduction/'
    # Path to project assets folder.
    assetFolder = os.path.join(projectFolder, 'assets')

    # Pata to userAppDir folders.
    userAppDir = cmds.internalVar(userAppDir=True)
    userDirectory = os.path.join(userAppDir, 'projectManager')


    def __init__(self):
        self.user = 'Eric'

        def createDirectory(self):
            if not os.path.exists(directory):
                os.makedirs(directory)

        self.readAssets = csv.reader(self.assets_text, delimiter=',')
        next(self.readAssets, None)
        self.readShots = csv.reader(self.shots_text, delimiter=',')
        next(self.readShots, None)

    def getAssignedAssets(self):
        self.assignedAssets = collections.namedtuple('Assets', ['Name', 'Type', 'Assigned_To', 'Status', 'Task', 'Bid', 'BidPercent'])
        assetList = []
        for row in self.readAssets:
            for field in row:
                if field == self.user:
                    self.asset = self.assignedAssets(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                    assetList.append(self.asset)


        return assetList


    def getShots(self):
        self.assignedShots = collections.namedtuple('Shots', ['Shot', 'Step', 'Status', 'Assigned_To', 'Bid', 'BidPercent'])
        shotList = []
        for row in self.readShots:
            self.shot = self.assignedShots(row[0], row[1], row[2], row[3], row[4], row[5])
            shotList.append(self.shot)

        return shotList

    def newMayaProj(self, path, task_name, task_type):
        for f in os.listdir(path):
            if f.endswith('.ma'):
                return False
        else:
            cmds.file(new=True, force=True)
            cmds.workspace(path, o=True)
            cmds.file(rename=str(task_name + '_' + task_type +  '_v001') )
            cmds.file(save=True, type='mayaAscii')
            return True
