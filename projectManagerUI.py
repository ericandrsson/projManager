from projManager import projectManager
from PySide2 import QtWidgets, QtUiTools
from maya import cmds
import os

reload (projectManager)

class ProjectManagerUI(QtWidgets.QDialog):

    def __init__(self):
        super(ProjectManagerUI, self).__init__()

        self.projectManager = projectManager.ProjectManager()
        self.buildUI()
        self.populateMyTasks()



    def buildUI(self):
        # Creates layout
        loader = QtUiTools.QUiLoader()

        self.ui = loader.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'UI', 'projectManagerUI.ui'))

        # Get UI Elements
        self.my_tasks_list = self.ui.findChild(QtWidgets.QListWidget, 'my_tasks_listWidget')
        self.my_tasks_files = self.ui.findChild(QtWidgets.QListWidget, 'my_tasks_files_listWidget')
        self.new_file_btn = self.ui.findChild(QtWidgets.QPushButton, 'new_file')
        self.cancel_btn = self.ui.findChild(QtWidgets.QPushButton, 'cancel')
        self.open_file_btn = self.ui.findChild(QtWidgets.QPushButton, 'open_file')
        self.bid_time_bar = self.ui.findChild(QtWidgets.QProgressBar, 'bidtimeBar')


        # Create connections
        self.new_file_btn.clicked.connect(self.new_maya_proj)
        self.my_tasks_list.clicked.connect(self.getTaskInfo)
        self.my_tasks_files.clicked.connect(self.get_file_version_selected)
        self.open_file_btn.clicked.connect(self.open_file)
        self.cancel_btn.clicked.connect(self.cancel)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.ui)
        self.setLayout(mainLayout)


    def populateMyTasks(self):
        self.assignedAssets = self.projectManager.getAssignedAssets()
        for asset in self.assignedAssets:
            self.my_tasks_list.addItem(str(asset.Name) + ' (' + str(asset.Task)+ ')')

        # If no folder for asset exists.
        prop_subFolders = ['art', 'model', 'rig', 'surface']
        prop_task_subFolders = ['publish', 'review', 'work']
        prop_task_software_subFolders = ['maya', 'nuke', 'zbrush']

        for asset in self.assignedAssets:
            assetDir = os.path.join(self.projectManager.assetFolder, asset.Type, asset.Name)
            if not os.path.exists(assetDir):
                for prop_subFolder in prop_subFolders:
                    for prop_task_subFolder in prop_task_subFolders:
                        for prop_task_software_subFolder in prop_task_software_subFolders:
                            os.makedirs(os.path.join(assetDir, prop_subFolder, prop_task_subFolder, prop_task_software_subFolder))

        #self.assignedShots = self.projectManager.getAssignedShots()

        '''
        for asset in self.assignedAssets:
            self.my_tasks_listWidget.addItem(asset)
            self.assets_listWidget.addItem(asset)

        self.assignedShots = self.projectManager.getAssignedShots()
        for shot in self.assignedShots:
            self.my_tasks_listWidget.addItem(shot)
            self.shots_listWidget.addItem(shot)
        '''
    def new_maya_proj(self):
        try:
            self.projectManager.newMayaProj(self.asset_maya_path, self.task_name, self.task_type)
            self.close()
        except:
            print 'Noting selected'


    def getTaskInfo(self, item):
        self.my_tasks_files.clear()
        task = item.data()
        self.task_name = task.split(' (')[0]
        self.task_type = task.split(' (')[1]
        self.task_type = self.task_type[:-1]

        # Sets percentage
        for asset in self.assignedAssets:
            if asset.Name == self.task_name:
                if int(asset.BidPercent) > 100:
                    self.bid_time_bar.setValue(100)
                else:
                    self.bid_time_bar.setValue(int(asset.BidPercent))

        # Checks if file exists.
        for asset in self.assignedAssets:
            if asset.Name == self.task_name:
                self.asset_maya_path = os.path.join(self.projectManager.assetFolder, asset.Type, asset.Name, asset.Task, 'work', 'maya')
                for f in os.listdir(self.asset_maya_path):
                    if f.endswith('.ma'):
                        self.my_tasks_files.addItem(f)


    def get_file_version_selected(self, item):
        self.file_version_selected = item.data()

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
                    cmds.workspace(self.asset_maya_path, o=True)
                    cmds.file(os.path.join(self.asset_maya_path, self.file_version_selected), open=True)
                    self.close()
                elif unsavedMsgRet == unsavedMsg.No:
                    cmds.file(new=True, force=True)         
                    cmds.workspace(self.asset_maya_path, o=True)
                    cmds.file(os.path.join(self.asset_maya_path, self.file_version_selected), open=True)
                    self.close()
                elif unsavedMsgRet == unsavedMsg.Cancel:
                    pass
            else:
                cmds.workspace(self.asset_maya_path, o=True)
                cmds.file(os.path.join(self.asset_maya_path, self.file_version_selected), open=True)
                self.close()
                     
        except Exception as e: print(e)

    def cancel(self):
        self.close()

    def msgbtn(self):
        print('Canceling') 

def showUI():
    ui = ProjectManagerUI()
    ui.show()
    return ui
