from projManager import projectManager
from PySide2 import QtWidgets, QtUiTools
import subprocess
import os
from maya import cmds
import maya.OpenMaya as om


class projectManagerTools(QtWidgets.QDialog):

    def __init__(self):
        super(projectManagerTools, self).__init__()
        reload (projectManager)
        self.projectManager = projectManager.ProjectManager()
        self.currentProj = self.getCurrentProj()
        self.build_projectManagerToolsUI()
        self.populatePublish()

    def build_projectManagerToolsUI(self):
        loader = QtUiTools.QUiLoader()
        self.projectManagerToolsUI = loader.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'UI', 'projectManagerTools.ui'))

        self.publish_asset = self.projectManagerToolsUI.findChild(QtWidgets.QPushButton, 'publish_btn')
        self.add_meta = self.projectManagerToolsUI.findChild(QtWidgets.QPushButton, 'meta')

        self.publish_btn = self.projectManagerToolsUI(QtWidgets.QPushButton, '')
        self.publishCheckBoxLayout = self.projectManagerToolsUI.findChild(QtWidgets.QVBoxLayout, 'verticalLayout_6')
        self.publishBtn = QtWidgets.QPushButton("Publish")


        self.publishBtn.clicked.connect(self.publishAlembic)
        self.add_meta.clicked.connect(self.addMeta)


        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.projectManagerToolsUI)
        self.setLayout(mainLayout)



    def populatePublish(self):
        self.publishBtn.setEnabled(False)
        self.metaItems = []
        self.checkBoxList = []

        allObjects = cmds.ls(dag=True)

        for obj in allObjects:
            if cmds.attributeQuery('publishMetadata', n=obj, exists=True):
                children = cmds.listRelatives(obj, children=True, fullPath=True) or []
                if len(children) == 1:
                    child = children[0]
                    objType = cmds.objectType(child)
                else:
                    objType = cmds.objectType(obj)

                if objType == 'mesh' or objType =='camera' or objType =='transform':
                    if objType == 'mesh':
                        type = 'Geometry'
                    elif objType == 'camera':
                        type = 'Camera'
                    elif objType == 'transform':
                        type = 'Group'

                    if 'assets' in self.currentProj['filePath']:
                        if type != 'Camera':
                            self.metaItems.append(obj)
                            self.publishCheckBox = QtWidgets.QCheckBox('[' + type + '] - ' + obj)
                            self.checkBoxDict = {'Name':  obj, 'ID': self.publishCheckBox, 'Type': type}
                            self.checkBoxList.append(self.checkBoxDict)
                            self.publishCheckBoxLayout.addWidget(self.publishCheckBox)

                    elif 'shots' in self.currentProj['filePath']:
                        self.metaItems.append(obj)
                        self.publishCheckBox = QtWidgets.QCheckBox('[' + type + '] - ' + obj)
                        self.checkBoxDict = {'Name':  obj, 'ID': self.publishCheckBox, 'Type': type}
                        self.checkBoxList.append(self.checkBoxDict)
                        self.publishCheckBoxLayout.addWidget(self.publishCheckBox)

        if self.checkBoxList:
            self.publishBtn.setEnabled(True)

        self.publishCheckBoxLayout.addWidget(self.publishBtn)




    def openProjectDir(self):
        projectdir = os.path.dirname(cmds.file(q=True, sn=True))
        try:
            os.startfile(projectdir)
        except:
            subprocess.call(["open", projectdir])

    def fast_playblast(self, widthArg=1280, heightArg=720):

        playblastDir = projectDir + "playblasts"
        playblastFile = projectDir + sceneName + ".mov"
        numCurrentFiles = []

        # Create a playblasts directory
        cmds.sysFile(playblastDir, makeDir=True)

        # Create playblast
        cmds.playblast(filename=sceneName, format="qt",  width=widthArg, height=heightArg, viewer=False, percent=100)

        # Check how many files are in the playblast folder
        allFilesList = cmds.getFileList(folder=images)

        # Looks for files with same file version in playblast folder
        # Script does not work if it doesnt detect any files to get revison number so that is what the if else statment is for
        # Two options: IF = if there is no playblast file.   ELSE = there are play blast files.
        if str(bool(allFilesList)) == "False":
           numFiles = "1"

           revisionID = numFiles.zfill(3)
           # Copy Playblast file and delete original

        else:
            # Remove Thumbs.db
            if 'Thumbs.db' in allFilesList: allFilesList.remove('Thumbs.db')

            # Turns version into playBlast version to remove counting of revions with 002,003,004 etc
            # Outcome example v002
            playBlastversion = 'v' + version

            # Looks for files with same file version in playblast folder
            for item in allFilesList:
                if playBlastversion in item:
                    numCurrentFiles.append(item)

                numFiles = str(len(numCurrentFiles) + 1)

                revisionID = numFiles.zfill(3)

        # Copy Playblast file to correct folder and delete original
        cmds.sysFile(playblastFile, copy=playblastDir + "/" + sceneName + "_r" + revisionID + ".mov")
        cmds.sysFile(playblastFile, delete=True)

        om.MGlobal.displayInfo("******* Fastblast completed successfully *******")

    def bashComp(self):
        try:
            self.currentProj = self.getCurrentProj()
            imagesVersionDir = os.path.join(self.currentProj['projectDir'], 'images', 'v' + self.currentProj['version'])
            currentRenderLayerDirs = [i for i in os.listdir(imagesVersionDir) if not i.startswith('.')]
            numCurrentFiles = []

            self.currentProjSplit = self.currentProj['projectDir'].split(os.path.sep)

            reviewDir = os.path.join(os.path.join('/', *self.currentProjSplit[0:-3]), 'review', 'maya')

            reviewFileList = [i for i in os.listdir(reviewDir) if i.endswith('.mov')]

            if not reviewFileList:
                numFiles = "1"
                revisionID = numFiles.zfill(3)
            else:
                reviewVersion = 'v' + self.currentProj['version']
                # Looks for files with same file version in playblast folder
                for item in reviewFileList:
                    if reviewVersion in item:
                        numCurrentFiles.append(item)

                    numFiles = str(len(numCurrentFiles) + 1)
                    revisionID = numFiles.zfill(3)

            # Give user option to chose which renderlayer to do bashComp, 'multiple merged?'
            if len(currentRenderLayerDirs) > 1:
                chosenRenderLayer = currentRenderLayerDirs[0]

            else:
                chosenRenderLayer = currentRenderLayerDirs[0]


            # Checks for all files that matches
            renderLayerFileList = [i for i in os.listdir(os.path.join(imagesVersionDir, chosenRenderLayer))
                                                            if i.startswith(self.currentProj['sceneName'][:-5] + '_' + chosenRenderLayer + '_v' +
                                                            self.currentProj['version'])]

            frameRange = ('1,' + str(len(renderLayerFileList)))

            # Gets the extension of the first file in list
            renderLayerExt = renderLayerFileList[0][-3:]
            nukeBashInput = os.path.join(imagesVersionDir, chosenRenderLayer, str(renderLayerFileList[0][0:-8:] + '####.' + renderLayerExt))
            nukeBashOutput = os.path.join('/' + reviewDir, str(renderLayerFileList[0][:-8] + 'review_r' + revisionID))



            # Creates the shell command to launch nuke with right commands
            nukeBashCommand = (str(self.projectManager.nukePath) + ' -x' + " " +
                               str(self.projectManager.nukeBashScript) + " " +
                               str(nukeBashInput) + " " +
                               str(nukeBashOutput) + " " +
                               str(self.projectManager.user) + " " +
                               str(self.currentProj['sceneName']) + " " +
                               str('r_' + revisionID) + " " +
                               str(self.projectManager.projectName) + " " +
                               str(frameRange))
            nukeRunBash = subprocess.call(nukeBashCommand, shell=True)

            # Checks for return code
            if nukeRunBash == 0:
                try:
                    os.startfile(reviewDir)
                except:
                    subprocess.call(["open", reviewDir])
                om.MGlobal.displayInfo('** bashComp finished successfully **')
            else:
                om.MGlobal.displayError('Something went wrong.')

            self.close()
        except:
            om.MGlobal.displayError('No rendered images can be found.')

    def publishAlembic(self):
        # Load the alembic plugin
        cmds.loadPlugin("AbcExport.mll", quiet=True)
        selection = cmds.ls(selection=True)

        alembicExportList = []

        for c in self.checkBoxList:
            if QtWidgets.QCheckBox.isChecked(c['ID']) == True:
                alembicExportList.append(c)

        if alembicExportList:
            outputPaths = []
            for i in alembicExportList:

                if 'assets' in self.currentProj['filePath']:
                    pStart = 1
                    pEnd = 1

                elif 'shots' in self.currentProj['filePath']:
                    pStart = 1
                    pEnd = 50

                publishItem = "-root " + i['Name']

                alembicVersionPath = os.path.join(self.currentProj['publishDir'], 'v' + self.currentProj['version'])
                alembicPath = os.path.join(alembicVersionPath, self.currentProj['sceneName'] + '_' + i['Name'] + '_publish.abc')

                if not os.path.isfile(alembicPath):
                    if not os.path.exists(alembicVersionPath):
                        os.makedirs(alembicVersionPath)
                    outputPaths.append(alembicPath)
                    command = "-attr ModelUsed -attr Namespace -attr scaleX -attr scaleY -attr scaleZ -attr visibility -frameRange %i %i -uvWrite -writeVisibility -worldSpace -eulerFilter -dataFormat hdf %s -file %s" % \
                              (pStart,
                               pEnd,
                               publishItem,
                               alembicPath)

                    cmds.AbcExport ( j = command )

            exitCode = 0
            if outputPaths:
                for f in outputPaths:
                    if os.path.isfile(f) == False:
                        exitCode += 1
            else:
                exitCode+=1

            if exitCode == 0:

                screenShotPath = os.path.join(alembicVersionPath, self.currentProj['sceneName'] + '_publish.jpg')
                cmds.viewFit()
                cmds.setAttr('defaultRenderGlobals.imageFormat', 8)
                cmds.playblast(completeFilename=screenShotPath, forceOverwrite=True, format='image', width=512, height=512,
                               showOrnaments=False, startTime=1, endTime=1, viewer=False)

                # Takes the current version, pluses 1, filles it with zeros and conc back to correct filepath.
                newVersion = (self.currentProj['fileName'][:-6] + str(int(self.currentProj['version']) + 1).zfill(3))
                cmds.file(rename=str(newVersion))
                cmds.file(save=True, type='mayaAscii')
                self.close()



                om.MGlobal.displayInfo('All alembics were exported successfully! ')

                try:
                    os.startfile(alembicVersionPath)
                except:
                    subprocess.call(["open", alembicVersionPath])

            else:
                om.MGlobal.displayError('Something went wrong. Please contact your suporvisor.')

        else:
            om.MGlobal.displayError('No items selected.')


    def addMeta(self):
        tagItems = cmds.ls(selection = True)
        sceneCams = cmds.listCameras(perspective=True)
        noItems = str(len(tagItems))

        # For each item
        for item in tagItems:
            cmds.select(item)

            # If Metadata exists delete it first and continue
            if cmds.attributeQuery('publishMetadata', n=item, exists=True):
                cmds.deleteAttr(item + '.publishMetadata')
                cmds.setAttr(item + '.useOutlinerColor', False)

            else:
                pass

            # Collect attributes
            uuidTag = cmds.ls(selection = True, uuid = True)[0]
            filePath = cmds.file(query=True,sn=True)
            version = (filePath.split('_v')[1]).split('.')[0]


            # Add attributes
            cmds.addAttr(longName='publishMetadata', niceName='Publish Metadata', numberOfChildren=6, attributeType='compound')
            cmds.addAttr(longName='uuid', niceName='UUID', dataType='string', parent='publishMetadata')
            cmds.addAttr(longName='alembic', niceName='Alembic Name', dataType='string', parent='publishMetadata')
            cmds.addAttr(longName='subframe', niceName='Subframe Size', at = 'enum', en='180 Degrees (Default):144 Degrees:90 Degrees', parent='publishMetadata')
            cmds.addAttr(longName='version', niceName='Publish Version', dataType='string',parent='publishMetadata')
            cmds.addAttr(longName='artist', niceName='Artist', dataType='string', parent='publishMetadata')
            cmds.addAttr(longName='note', niceName='User Notes', dataType='string', parent='publishMetadata')

            # Set attributes
            cmds.setAttr((item + '.uuid'),uuidTag, typ='string')
            cmds.setAttr((item + '.alembic'), item, typ='string')
            cmds.setAttr((item + '.version'), version, typ='string')
            cmds.setAttr((item + '.artist'), self.projectManager.user, typ='string')
            cmds.setAttr((item + '.note'),'Type a short note here if you like...', typ='string')


            # Lock Down Attributes
            cmds.setAttr(item + ".uuid", lock=True)
            cmds.setAttr(item + ".alembic", lock=True)
            cmds.setAttr(item + ".version", lock=True)

            #Colour item in outliner
            if item in sceneCams:
                # Colour code for Camera
                cmds.setAttr(item + '.useOutlinerColor', True)
                cmds.setAttr(item + '.outlinerColorR', 0.0)
                cmds.setAttr(item + '.outlinerColorG', 0.5)
                cmds.setAttr(item + '.outlinerColorB', 1.0)

            else:
                # Colour code for Geo
                cmds.setAttr(item + '.useOutlinerColor', True)
                cmds.setAttr(item + '.outlinerColorR', 1.0)
                cmds.setAttr(item + '.outlinerColorG', 0.7)
                cmds.setAttr(item + '.outlinerColorB', 0.0)

        om.MGlobal.displayInfo(noItems + ' items tagged with metadata successfully.')
        self.close()

    def getCurrentProj(self):
        projectDir = cmds.workspace(query=True, rootDirectory=True)
        filePath = cmds.file(query=True, sn=True)
        fileName = filePath.split('/')[-1]
        sceneName = fileName.split('.')[0]
        assetName = fileName.split('_')[0]
        task = sceneName.split('_')[1]
        version = sceneName.split('v')[1]

        currentProjSplit = projectDir.split(os.path.sep)
        publishDir = os.path.join(os.path.join('/', *currentProjSplit[0:-3]), 'publish', 'maya')


        currentProj = {'projectDir': projectDir, 'filePath': filePath, 'fileName': fileName, 'sceneName': sceneName,
                       'assetName': assetName, 'task': task, 'version': version, 'publishDir': publishDir}
        return (currentProj)



def showUI():
    ui = projectManagerTools()
    ui.show()
    return ui
