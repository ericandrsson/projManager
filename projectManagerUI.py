from projManager import projectManager
from PySide2 import QtWidgets, QtUiTools
import os
from maya import cmds
import maya.mel as mel
import pymel.core as pm
import maya.OpenMaya as om
import time


class ProjectManagerUI(QtWidgets.QDialog):
    def __init__(self):
        super(ProjectManagerUI, self).__init__()
        reload (projectManager)
        self.projectManager = projectManager.ProjectManager()
        self.projectCheck()
        self.buildUI()
        self.getAssetsShots()
        self.populateMyTasks()
        self.populateAssetsShotsTab()

    def buildUI(self):
        # Creates layout
        loader = QtUiTools.QUiLoader()

        self.ui = loader.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'UI', 'projectManagerUI.ui'))

        # Get UI Elements
        self.my_tasks_list = self.ui.findChild(QtWidgets.QListWidget, 'my_tasks_listWidget')
        self.assets_list = self.ui.findChild(QtWidgets.QListWidget, 'assets_listWidget')
        self.shots_list = self.ui.findChild(QtWidgets.QListWidget, 'shots_listWidget')
        self.new_file_btn = self.ui.findChild(QtWidgets.QPushButton, 'new_file')
        self.cancel_btn = self.ui.findChild(QtWidgets.QPushButton, 'cancel')
        self.open_file_btn = self.ui.findChild(QtWidgets.QPushButton, 'open_file')
        self.bid_time_bar = self.ui.findChild(QtWidgets.QProgressBar, 'bidtimeBar')

        # Set default states
        self.new_file_btn.setEnabled(False)
        self.open_file_btn.setEnabled(False)

        # Create connections
        self.new_file_btn.clicked.connect(self.newMayaProj)
        self.my_tasks_list.clicked.connect(self.getTaskInfo)
        self.assets_list.clicked.connect(self.getTaskInfo)
        self.shots_list.clicked.connect(self.getTaskInfo)
        self.open_file_btn.clicked.connect(self.open_file)
        self.cancel_btn.clicked.connect(self.cancel)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.ui)
        self.setLayout(mainLayout)

    def projectCheck(self):
        # Checks if project exists, if not creates nessecary folders.
        if not os.path.exists(self.projectManager.projectFolder):
            raise NameError('Project folder does not exists. Please contact your supervisor.')
            quit()
        else:
            project_folder = self.projectManager.projectFolder
            defaultDirs = ['io/incoming', 'io/outgoing', 'assets', 'shots','production/docs', 'production/review/assets', 'production/review/shots', 'maps/textures', 'maps/HDRI', 'tools/scripts/nuke', 'tools/scripts/publish']

            for directory in defaultDirs:
                if not os.path.exists(os.path.join(project_folder, directory)):
                    os.makedirs(os.path.join(project_folder, directory))

    def getAssetsShots(self):
        self.assets = self.projectManager.getAssets()
        self.shots = self.projectManager.getShots()

        # If no folder for asset exists.
        asset_subFolders = ['art', 'model', 'rig', 'surface']
        asset_task_subFolders = ['work', 'review', 'publish']
        asset_task_software_subFolders = ['maya', 'houdini', 'nuke']

        for asset in self.assets:
            assetDir = os.path.join(self.projectManager.projectFolder, 'assets', asset['Type'], asset['Name'])
            if asset['Type'] == 'prepro':
                for asset_task_subFolder in asset_task_subFolders:
                    if not os.path.exists(os.path.join(assetDir, 'art', asset_task_subFolder, 'photoshop')):
                        os.makedirs(os.path.join(assetDir, 'art', asset_task_subFolder, 'photoshop'))
            else:
                for asset_subFolder in asset_subFolders:
                    for asset_task_subFolder in asset_task_subFolders:
                        for asset_task_software_subFolder in asset_task_software_subFolders:
                            if asset_subFolder != 'art':
                                if not os.path.exists(os.path.join(assetDir, asset_subFolder, asset_task_subFolder, asset_task_software_subFolder)):
                                    os.makedirs(os.path.join(assetDir, asset_subFolder, asset_task_subFolder, asset_task_software_subFolder))
                            else:
                                if not os.path.exists(os.path.join(assetDir, asset_subFolder, asset_task_subFolder, 'photoshop')):
                                    os.makedirs(os.path.join(assetDir, asset_subFolder, asset_task_subFolder, 'photoshop'))


            # Checks for latest version and adds to dictiory
            self.asset_maya_path = os.path.join(self.projectManager.projectFolder, 'assets', asset['Type'], asset['Name'], asset['Task'], 'work', 'maya')
            if os.path.isfile(os.path.join(str(self.asset_maya_path),'scenes', str(asset['Name']) + '_' + str(asset['Task']) + '_v001.ma')):
                asset_maya_versionList = []
                # Searches for matching file and adds it to list. Sorts it and grabs the last file in the list (latest version)
                for f in os.listdir(os.path.join(self.asset_maya_path, 'scenes')):
                    if f.startswith(str(asset['Name'] + '_' + asset['Task'])) and f.endswith('.ma'):
                        asset_maya_versionList.append(f)

                asset_maya_versionList.sort()
                asset_mayaFile_path = asset_maya_versionList[-1]
                asset['Maya_Path'] = self.asset_maya_path
                asset['Maya_File_Path'] = os.path.join(self.asset_maya_path, 'scenes', asset_mayaFile_path)
                asset['Version'] = asset_mayaFile_path[-6:-3]
            else:
                asset['Version'] = ''
                asset['Maya_File_Path'] = self.asset_maya_path
        shot_subFolders = ['prepro', 'layout', 'anim', 'light', 'FX', 'comp']
        shot_task_subFolders = ['publish', 'review', 'work']
        shot_task_software_subFolders = ['maya', 'nuke', 'houdini']

        for shot in self.shots:
            shotDir = os.path.join(self.projectManager.projectFolder, 'shots', shot['Shot_Code'])
            for shot_subFolder in shot_subFolders:
                for shot_task_subFolder in shot_task_subFolders:
                    for shot_task_software_subFolder in shot_task_software_subFolders:
                        if not os.path.exists(os.path.join(shotDir, shot_subFolder, shot_task_subFolder, shot_task_software_subFolder)):
                            os.makedirs(os.path.join(shotDir, shot_subFolder, shot_task_subFolder, shot_task_software_subFolder))
            # Checks for latest version and adds to dictiory
            self.shot_maya_path = os.path.join(self.projectManager.projectFolder, 'shots', shot['Shot_Code'], shot['Step'], 'work', 'maya')
            if os.path.isfile(os.path.join(str(self.shot_maya_path), 'scenes' , str(shot['Shot_Code']) + '_' + str(shot['Step']) + '_v001.ma')):

                shot_maya_versionList = []
                # Searches for matching file and adds it to list. Sorts it and grabs the last file in the list (latest version)
                for f in os.listdir(os.path.join(self.shot_maya_path, 'scenes')):
                    if f.startswith(str(shot['Shot_Code'] + '_' + shot['Step'])) and f.endswith('.ma'):
                        shot_maya_versionList.append(f)

                shot_maya_versionList.sort()
                shot_mayaFile_path = shot_maya_versionList[-1]
                shot['Maya_Path'] = self.shot_maya_path
                shot['Maya_File_Path'] = os.path.join(self.shot_maya_path, shot_mayaFile_path)
                shot['Version'] = shot_mayaFile_path[-6:-3]
            else:
                shot['Version'] = ''
                shot['Maya_File_Path'] = self.shot_maya_path

    def populateMyTasks(self):
        try:
            # Populates my tasks with assigned assets
            for asset in self.assets:
                if asset['Assigned_To'] in str(self.projectManager.user) and asset['Assigned_To'] != "":
                    if not asset['Task'] == 'art':
                        if asset['Version']:
                            self.my_tasks_list.addItem(asset['Name'] + ' (' + asset['Task']+ ')' + ' - ' + 'v' + asset['Version'])

                        else:
                            self.my_tasks_list.addItem(asset['Name'] + ' (' + asset['Task']+ ')')

            # Populates my tasks with assigned assets
            for shot in self.shots:
                if shot['Assigned_To'] in str(self.projectManager.user) and shot['Assigned_To'] != "":
                    if not shot['Step'] == 'comp':
                        if shot['Version']:
                            self.my_tasks_list.addItem(shot['Shot_Code'] + ' (' + shot['Step']+ ')' + ' - ' + 'v' + shot['Version'])

                        else:
                            self.my_tasks_list.addItem(shot['Shot_Code'] + ' (' + shot['Step']+ ')')
        except:
            pass

    def populateAssetsShotsTab(self):
        for asset in self.assets:
            if not asset['Task'] == 'art':
                if asset['Version']:
                    self.assets_list.addItem(asset['Name'] + ' (' + asset['Task']+ ')' + ' - ' + 'v' + asset['Version'])

                else:
                    self.assets_list.addItem(asset['Name'] + ' (' + asset['Task']+ ')')


        for shot in self.shots:
            if not shot['Step'] == 'comp':
                if shot['Version']:
                    self.shots_list.addItem(shot['Shot_Code'] + ' (' + shot['Step']+ ')' + ' - ' + 'v' + shot['Version'])

                else:
                    self.shots_list.addItem(shot['Shot_Code'] + ' (' + shot['Step']+ ')')

    def getTaskInfo(self, item):
        self.open_file_btn.setEnabled(False)
        # Grabs the output from clicking.
        itemSel = item.data()
        self.itemSel = {}
        # Splits the task into name + type and assigns it.
        self.itemSelName = itemSel.split(' (')[0]

        try:
            for asset in self.assets:
                # Compares selected item name against asset names
                if asset['Name'] == self.itemSelName:
                    # In case a weird naming, checks for asset task. If match continues.
                    if asset['Task'] == (itemSel.split(' (')[1]).split(')')[0]:
                        self.itemSel = asset
                        self.itemSel['itemType'] = 'asset'

                        '''
                        # Sets percentage of asset
                        if int(asset['BidPercent']) > 100:
                            self.bid_time_bar.setValue(100)
                            self.popupMessage('Bidtime', 'Bidtime for this task is up. Please contact your supervisor.')
                        else:
                            self.bid_time_bar.setValue(int(asset['BidPercent']))
                        '''

                        # Checks if version exists, if not set new file button true.
                        if not asset['Version']:
                            self.new_file_btn.setEnabled(True)
                        else:
                            self.open_file_btn.setEnabled(True)
                            self.new_file_btn.setEnabled(False)
        except:
            pass

        try:
            for shot in self.shots:
                if shot['Shot_Code'] == self.itemSelName:
                    if shot['Step'] == (itemSel.split(' (')[1]).split(')')[0]:
                        self.itemSel = shot
                        self.itemSel['itemType'] = 'shot'
                        '''
                        if int(shot['BidPercent']) > 100:
                            self.bid_time_bar.setValue(100)
                            self.popupMessage('Bidtime', 'Bidtime for this task is up. Please contact your supervisor.')
                        else:
                            self.bid_time_bar.setValue(int(shot['BidPercent']))
                        '''

                        # Checks if version exists, if not set new file button true.
                        if not shot['Version']:
                            self.new_file_btn.setEnabled(True)
                        else:
                            self.open_file_btn.setEnabled(True)
                            self.new_file_btn.setEnabled(False)
        except:
            pass

        print self.itemSel

    def newMayaProj(self):
        cmds.file(new=True, force=True)
        mel.eval('setProject \"' + self.itemSel['Maya_File_Path'].replace('\\', '/') + '\"')
        for file_rule in cmds.workspace(query=True, fileRuleList=True):
            file_rule_dir = cmds.workspace(fileRuleEntry=file_rule)
            maya_file_rule_dir = os.path.join(self.itemSel['Maya_File_Path'], file_rule_dir)
            if not os.path.exists(maya_file_rule_dir):
                os.makedirs(maya_file_rule_dir)

        if self.itemSel['itemType'] == 'asset':
            cmds.file(rename=str(self.itemSel['Name'] + '_' + self.itemSel['Task'] +  '_v001') )
        elif self.itemSel['itemType'] == 'shot':
            cmds.file(rename=str(self.itemSel['Shot_Code'] + '_' + self.itemSel['Step'] +  '_v001') )

        cmds.file(save=True, type='mayaAscii')
        # Sets render paths
        try:
            self.popRenderPath()
        except:
            pass
        self.close()

    def open_file(self):
        try:
            if cmds.file(q=True, modified=True):
                unsavedMsg = QtWidgets.QMessageBox()
                unsavedMsg.setWindowTitle('Save your scene?')
                unsavedMsg.setText('Your scene has unsaved changes. Save before procceding?')
                unsavedMsg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
                unsavedMsg.setDefaultButton(QtWidgets.QMessageBox.Yes);
                unsavedMsgRet = unsavedMsg.exec_()

                if unsavedMsgRet == unsavedMsg.Yes:
                    cmds.SaveScene()
                    cmds.workspace(self.itemSel['Maya_Path'], o=True)
                    cmds.file(self.itemSel['Maya_File_Path'], open=True)
                    self.close()

                elif unsavedMsgRet == unsavedMsg.No:
                    cmds.file(new=True, force=True)
                    cmds.workspace(self.itemSel['Maya_Path'], o=True)
                    cmds.file(self.itemSel['Maya_File_Path'], open=True)
                    self.close()
                elif unsavedMsgRet == unsavedMsg.Cancel:
                    pass

            else:
                cmds.workspace(self.itemSel['Maya_Path'], o=True)
                cmds.file(self.itemSel['Maya_File_Path'], open=True)
                self.close()
        except:
            pass

    def cancel(self):
        self.close()

    def popupMessage(self, title, message):
        popupMessage = QtWidgets.QMessageBox()
        popupMessage.setWindowTitle(title)
        popupMessage.setText(message)
        popupMessage.setStandardButtons(QtWidgets.QMessageBox.Ok)
        popupMessage = popupMessage.exec_()

def showUI():
    ui = ProjectManagerUI()
    ui.show()
    return ui
