import os
import csv
import requests
import collections
from maya import cmds

class ProjectManager:

    # Fetches and reads the assets csv file.
    assets_csv_url = 'https://docs.google.com/spreadsheets/d/1-a2K2BXe1uCPinImkMx5qVsuJcKoylxrWBqQxNl2yA0/pub?gid=797696484&single=true&output=csv'
    req_assets_csv = requests.get(assets_csv_url, verify='C:/apps/python/2.7.8/Lib/site-packages/certifi/cacert.pem')
    assets_text = req_assets_csv.iter_lines()

    shots_csv_url= 'https://docs.google.com/spreadsheets/d/1-a2K2BXe1uCPinImkMx5qVsuJcKoylxrWBqQxNl2yA0/pub?gid=1343957549&single=true&output=csv'
    req_shots_csv = requests.get(shots_csv_url, verify='C:/apps/python/2.7.8/Lib/site-packages/certifi/cacert.pem')
    shots_text = req_shots_csv.iter_lines()

    # Path to project folder.
    projectFolder = 'C:/apps/autodesk/2017/Maya2017/plug-ins/camd/scripts/teamProduction/'
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

    def getAssignedAssets(self):
        readAssets = csv.reader(self.assets_text, delimiter=',')
        self.assignedAssets = collections.namedtuple('Assets', ['Name', 'Type', 'Assigned_To', 'Status', 'Task', 'Bid', 'BidPercent'])
        assetList = []
        for row in readAssets:
            for field in row:
                if field == self.user:
                    self.asset = self.assignedAssets(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                    assetList.append(self.asset)


        return assetList


    def getAssignedShots(self):
        pass
        '''readShots = csv.reader(self.shots_text, delimiter=',')
        self.assignedShots = collections.namedtuple('Shots', ['Shot', 'Status', 'Assigned_To', 'Bid', 'BidPercent'])
        shotList = []
        for row in readShots:
            for field in row:
                if field == self.user:
                    self.shot = self.assignedShots(row[0], row[1], row[2], row[5], row[6])
                    assignedShots.append(row[0])

        return assignedShots
        '''
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
