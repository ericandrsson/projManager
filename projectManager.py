import os
import csv
import requests
import getpass
from maya import cmds


class ProjectManager:
    # Path to project folder.
    projectName = 'teamProduction'
    projectFolder = '/Users/EricAndersson/Desktop/teamProduction/'
    #projectFolder = os.path.join('D:\\Users\\emanuel.and6428\\Project\\', projectName)

    nukePath = '/Applications/Nuke10.5v2/Nuke10.5v2*Non-commercial.app/Nuke10.5v2*Non-commercial'
    nukeBashScript = os.path.join(projectFolder, 'tools', 'scripts','nuke','nukeBash.nknc')

    #Path to userAppDir folders.
    userAppDir = cmds.internalVar(userAppDir=True)
    userDirectory = os.path.join(userAppDir, 'projectManager')


    def __init__(self):
        #self.user = getpass.getuser()
        self.user = 'Eric'

    def getAssets(self):
        # Fetches and reads the assets csv file.
        assets_csv_url = 'https://docs.google.com/spreadsheets/d/1-a2K2BXe1uCPinImkMx5qVsuJcKoylxrWBqQxNl2yA0/pub?gid=797696484&single=true&output=csv'
        try:
            req_assets_csv = requests.get(assets_csv_url, stream=True)
        except:
            req_assets_csv = requests.get(assets_csv_url, verify='C:/apps/python/2.7.8/Lib/site-packages/certifi/cacert.pem')

        assets_text = req_assets_csv.iter_lines()

        self.readAssets = csv.reader(assets_text, delimiter=',')
        next(self.readAssets, None)
        # ------------------------------------------------
        assetList = []
        for row in self.readAssets:
            self.asset = {'Name': row[0], 'Type': row[1], 'Assigned_To': row[2], 'Status': row[3], 'Task': row[4], 'Bid': row[5], 'BidPercent': row[6]}
            assetList.append(self.asset)
        return assetList


    def getShots(self):
        shots_csv_url= 'https://docs.google.com/spreadsheets/d/1-a2K2BXe1uCPinImkMx5qVsuJcKoylxrWBqQxNl2yA0/pub?gid=1343957549&single=true&output=csv'
        try:
            req_shots_csv = requests.get(shots_csv_url, stream=True)
        except:
            req_shots_csv = requests.get(shots_csv_url, verify='C:/apps/python/2.7.8/Lib/site-packages/certifi/cacert.pem')
        shots_text = req_shots_csv.iter_lines()

        self.readShots = csv.reader(shots_text, delimiter=',')
        next(self.readShots, None)
        # ------------------------------------------------
        shotList = []
        for row in self.readShots:
            self.shot = {'Shot_Code': row[0], 'Step': row[1], 'Status': row[2], 'Assigned_To': row[3], 'Bid': row[4], 'BidPercent': row[5]}
            shotList.append(self.shot)
        return shotList

    # RENDER PREP TOOLS -----------------------------------------------------------------------
    def popRenderPath(self):
        # Get version ID
        fileName = cmds.file(q=True, sn=True)[cmds.file(q=True, sn=True).rfind('/')+1:cmds.file(q=True, sn=True).rfind('.')]
        version = fileName.split("_v")[1]
        sceneName = fileName.split("_v")[0]

        #Populate Render globals
        try:
            cmds.setAttr("vraySettings.fileNamePrefix", 'v<Version>/<Layer>/'+ sceneName + '_<Layer>_v<Version>', type="string")
            cmds.setAttr("defaultRenderGlobals.renderVersion", version, type="string")
            cmds.setAttr ("vraySettings.imgOpt_exr_autoDataWindow", 1)
            cmds.setAttr ("vraySettings.imgOpt_exr_multiPart", 1)
        except:
            pass
