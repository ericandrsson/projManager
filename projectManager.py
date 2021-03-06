import os
import csv
import requests
import getpass
import logging
from maya import cmds


class ProjectManager:
    # Path to project folder.
    projectName = 'team_4'
    #projectFolder = '/Users/EricAndersson/Desktop/teamProduction/'
    projectFolder = os.path.join('\\\productions\\boad\\Projects\\BAD17023\\team_production_II\\', projectName)

    #nukePath = '/Applications/Nuke10.5v2/Nuke10.5v2*Non-commercial.app/Nuke10.5v2*Non-commercial'
    nukePath = 'C:\\apps\\nuke\\10.5v1\\Nuke10.5.exe'
    nukeBashScript = os.path.join(projectFolder, 'tools', 'scripts','nuke','nukeBash.nk')

    #Path to userAppDir folders.
    userAppDir = cmds.internalVar(userAppDir=True)
    userDirectory = os.path.join(userAppDir, 'projectManager')


    def __init__(self):
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        self.user = getpass.getuser()

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
            print row
            shotList.append(self.shot)
        return shotList

    def getFrameRange(self, shot):
        # Fetches and reads the frameRange csv file.
        frameRange_csv_url = 'https://docs.google.com/spreadsheets/d/1-a2K2BXe1uCPinImkMx5qVsuJcKoylxrWBqQxNl2yA0/pub?gid=1408211990&single=true&output=csv'
        try:
            req_frameRange_csv = requests.get(frameRange_csv_url, stream=True)
        except:
            req_frameRange_csv = requests.get(frameRange_csv_url, verify='C:/apps/python/2.7.8/Lib/site-packages/certifi/cacert.pem')

        frameRange_text = req_frameRange_csv.iter_lines()
        self.readFrameRange = csv.reader(frameRange_text, delimiter=',')
        # ------------------------------------------------
        next(self.readFrameRange, None)
        shotBreakDownList = []
        for row in self.readFrameRange:
            shotBreakDown = {'Shot_Code': row[0], 'FrameRange': row[1]}
            shotBreakDownList.append(shotBreakDown)
        return shotBreakDownList
