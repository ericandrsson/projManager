from projManager import projectManager
from PySide2 import QtWidgets, QtUiTools
import os, shutil, subprocess, datetime, shelve
import pymel.core as pm
from maya import cmds, OpenMayaUI
import maya.OpenMaya as om


class projectManagerTools(QtWidgets.QDialog):

    def __init__(self):
        super(projectManagerTools, self).__init__()
        reload (projectManager)
        self.projectManager = projectManager.ProjectManager()
        self.currentProj = self.getCurrentProj()

        self.publishDB = os.path.join(self.projectManager.projectFolder, 'tools', 'scripts', 'publish', 'publishDB')

        self.build_projectManagerToolsUI()
        self.populateLoader()
        self.populatePublishAlembics()
        self.populatePublishRenders()

    def build_projectManagerToolsUI(self):
        loader = QtUiTools.QUiLoader()
        self.projectManagerToolsUI = loader.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'UI', 'projectManagerTools.ui'))
        # Find children
        self.publish_asset = self.projectManagerToolsUI.findChild(QtWidgets.QPushButton, 'publish_btn')
        self.cancelbtn = self.projectManagerToolsUI.findChild(QtWidgets.QPushButton, 'cancel_btn')
        self.quickDailyBtn = self.projectManagerToolsUI.findChild(QtWidgets.QPushButton, 'quickDaily_btn')
        self.renderPathBtn = self.projectManagerToolsUI.findChild(QtWidgets.QPushButton, 'renderPath_btn')
        self.syncFrameRangeBtn = self.projectManagerToolsUI.findChild(QtWidgets.QPushButton, 'syncFrameRange_btn')
        self.loaderWidget = self.projectManagerToolsUI.findChild(QtWidgets.QTableWidget, 'loaderTableWidget')
        self.alembicPublishWidget = self.projectManagerToolsUI.findChild(QtWidgets.QTableWidget, 'alembicPublish_TableWidget')
        self.rendersPublishWidget = self.projectManagerToolsUI.findChild(QtWidgets.QTableWidget, 'rendersPublish_TableWidget')
        self.publishCheckBoxLayout = self.projectManagerToolsUI.findChild(QtWidgets.QVBoxLayout, 'verticalLayout_6')
        self.alembicTab = self.projectManagerToolsUI.findChild(QtWidgets.QWidget, 'alembic_tab')
        self.renderTab = self.projectManagerToolsUI.findChild(QtWidgets.QWidget, 'render_tab')
        self.loadBtn = self.projectManagerToolsUI.findChild(QtWidgets.QPushButton, 'loaditem_btn')
        self.publishAlembicBtn = self.projectManagerToolsUI.findChild(QtWidgets.QPushButton, 'publishAlembic_btn')
        self.publishRenderBtn = self.projectManagerToolsUI.findChild(QtWidgets.QPushButton, 'publishRender_btn')
        self.addMetaBtn = self.projectManagerToolsUI.findChild(QtWidgets.QPushButton, 'plusMeta_btn')
        self.removeMetaBtn = self.projectManagerToolsUI.findChild(QtWidgets.QPushButton, 'minusMeta_btn')
        self.openImagesFolderBtn = self.projectManagerToolsUI.findChild(QtWidgets.QPushButton, 'openImagesFolder_btn')


        # Connections
        self.quickDailyBtn.clicked.connect(self.quickDaily)
        self.renderPathBtn.clicked.connect(self.popRenderPath)
        self.syncFrameRangeBtn.clicked.connect(self.syncFrameRange)
        self.publishAlembicBtn.clicked.connect(self.publishAlembic)
        self.publishRenderBtn.clicked.connect(self.publishRenders)
        self.cancelbtn.clicked.connect(lambda: self.close())
        self.removeMetaBtn.clicked.connect(self.removeMeta)
        self.addMetaBtn.clicked.connect(self.addMeta)
        self.loadBtn.clicked.connect(self.loadPublishFile)
        self.loaderWidget.clicked.connect(lambda: self.loadBtn.setEnabled(True))
        self.alembicPublishWidget.clicked.connect(lambda: self.publishAlembicBtn.setEnabled(True))
        self.openImagesFolderBtn.clicked.connect(self.openImagesFolder)

        self.removeMetaBtn.setEnabled(False)
        self.loadBtn.setEnabled(False)
        self.publishAlembicBtn.setEnabled(False)
        self.alembicTab.setEnabled(False)
        self.renderTab.setEnabled(False)

        # Alembic Publish
        if self.currentProj['projType'] == 'shot' or self.currentProj['projType'] == 'asset':
            if self.currentProj['task'] == 'anim' or self.currentProj['task'] == 'layout' or self.currentProj['task'] == 'model' or self.currentProj['task'] == 'rig':
                self.alembicTab.setEnabled(True)

        if self.currentProj['projType'] == 'shot' and self.currentProj['task'] == 'light':
            self.renderTab.setEnabled(True)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.projectManagerToolsUI)
        self.setLayout(mainLayout)

    def populateLoader(self):
        rowPosition = self.loaderWidget.rowCount()
        publishedItems = shelve.open(self.publishDB)
        for i in list(publishedItems.values()):
            self.loaderWidget.insertRow(rowPosition)
            self.loaderWidget.setItem(rowPosition , 0, QtWidgets.QTableWidgetItem(i['Name']))
            self.loaderWidget.setItem(rowPosition , 1, QtWidgets.QTableWidgetItem(i['Task']))
            self.loaderWidget.setItem(rowPosition , 2, QtWidgets.QTableWidgetItem(i['Type']))
            self.loaderWidget.setItem(rowPosition , 3, QtWidgets.QTableWidgetItem(i['Version']))
            self.loaderWidget.setItem(rowPosition , 4, QtWidgets.QTableWidgetItem(i['Artist']))
            self.loaderWidget.setItem(rowPosition , 5, QtWidgets.QTableWidgetItem(i['Time']))
        publishedItems.close()

    def loadPublishFile(self):
        selectedRow = self.loaderWidget.currentRow()
        publishedItems = shelve.open(self.publishDB)

        for i in list(publishedItems.values()):
            # Checks for name and time.
            if self.loaderWidget.item(selectedRow,0).text() == i['Name'] and self.loaderWidget.item(selectedRow,5).text() == i['Time']:
                self.publishedItemSel = i
        publishedItems.close()

        sceneReferenceList = cmds.file( q=True, l=True )

        if not self.publishedItemSel['Path'] in sceneReferenceList:
            cmds.file(self.publishedItemSel['Path'], r=True)
            om.MGlobal.displayInfo("Successfully referenced file.")
            self.close()

        else:
            om.MGlobal.displayError('Reference already exists in scene.')

    def addMeta(self):
        tagItems = cmds.ls(selection = True)
        if len(tagItems) > 1:
            om.MGlobal.displayError('Multiple object publishing is not supported. Please group all objects and name it correctly.')
        else:
            for item in tagItems:
                cmds.select(item)
                children = cmds.listRelatives(tagItems, children=True, fullPath=True) or []
                if len(children) == 1:
                    child = children[0]
                    objType = cmds.objectType(child)
                else:
                    objType = cmds.objectType(tagItems)

                if objType == 'mesh' or objType =='camera' or objType =='transform':
                    if objType == 'mesh':
                        itemType = 'geometry'
                    elif objType == 'camera':
                        itemType = 'camera'
                    elif objType == 'transform':
                        itemType = 'group'


                    exitCode = 1
                    correctGroupName = self.currentProj['name'] + '_' + self.currentProj['task'] + '_group'
                    # Checks if working on asset or shot
                    if self.currentProj['projType'] == 'asset':
                        publishType = self.currentProj['assetType']
                        if self.currentProj['task'] == 'model':
                            # Makes sure it's in a group.
                            if itemType == 'group':
                                # Makes sure the group is named correctly.
                                if item == correctGroupName:
                                    exitCode = 0
                                else:
                                    om.MGlobal.displayError('The group you are trying to publish is not named correctly. Correct: {}_{}_group'.format(self.currentProj['name'], self.currentProj['task']))

                            elif itemType == 'geometry':
                                try:
                                    if not cmds.objExists(correctGroupName):
                                        item = cmds.group(name = (self.currentProj['name'] + '_' + self.currentProj['task'] + '_group'))
                                        if item == self.currentProj['name'] + '_' + self.currentProj['task'] + '_group':
                                            exitCode = 0
                                    else:
                                        om.MGlobal.displayError('Correct named group already exists.')
                                except:
                                    pass

                            else:
                                om.MGlobal.displayError('The object is not valid for publish.')

                        # Checks if task is rig.
                        elif self.currentProj['task'] == 'rig':
                            pass


                    elif self.currentProj['projType'] == 'shot':
                        publishType = self.currentProj['projType']
                        if itemType == 'group':
                            # Makes sure the group is named correctly.
                            if item == self.currentProj['name'] + '_' + self.currentProj['task'] + '_group':
                                exitCode = 0
                            else:
                                om.MGlobal.displayError('The group you are trying to publish is not named correctly. Correct name: {}'.format(self.currentProj['name'] + '_' + self.currentProj['task'] + '_group'))

                        elif itemType == 'geometry':
                            try:
                                if not cmds.objExists(correctGroupName):
                                    item = cmds.group(name = (self.currentProj['name'] + '_' + self.currentProj['task'] + '_group'))
                                    if item == self.currentProj['name'] + '_' + self.currentProj['task'] + '_group':
                                        exitCode = 0
                                else:
                                    om.MGlobal.displayError('Correct named group already exists.')
                            except:
                                pass


                        elif itemType == 'camera':
                            if self.currentProj['task'] == 'layout':
                                if item != self.currentProj['name'] + '_' + 'renderCam':
                                    try:
                                        item = cmds.rename(str(item), str(self.currentProj['name']) + '_' + 'renderCam')
                                    except:
                                        pass
                                om.MGlobal.displayError('Please put camera in a correct named group.')
                            else:
                                om.MGlobal.displayError('Publishing camera is not allowed in {}'.format(self.currentProj['task']))




                    if exitCode == 0:
                        self.addMetaBtn.setEnabled(False)
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
                        cmds.addAttr(longName='objectType', niceName='Object Type', dataType='string', parent='publishMetadata')
                        cmds.addAttr(longName='subframe', niceName='Subframe Size', at = 'enum', en='180 Degrees (Default):144 Degrees:90 Degrees', parent='publishMetadata')
                        cmds.addAttr(longName='version', niceName='Publish Version', dataType='string',parent='publishMetadata')
                        cmds.addAttr(longName='artist', niceName='Artist', dataType='string', parent='publishMetadata')

                        # Set attributes
                        cmds.setAttr((item + '.uuid'),uuidTag, typ='string')
                        cmds.setAttr((item + '.alembic'), item, typ='string')
                        cmds.setAttr((item + '.objectType'), itemType, typ='string')
                        cmds.setAttr((item + '.version'), version, typ='string')
                        cmds.setAttr((item + '.artist'), self.projectManager.user, typ='string')


                        # Lock Down Attributes
                        cmds.setAttr(item + ".uuid", lock=True)
                        cmds.setAttr(item + ".alembic", lock=True)
                        cmds.setAttr(item + ".objectType", lock=True)
                        cmds.setAttr(item + ".version", lock=True)

                        #Colour item in outliner
                        if objType == 'camera':
                            # Colour code for camera
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

                        om.MGlobal.displayInfo('Items were tagged with metadata successfully.')
                        self.populatePublishAlembics()

    def removeMeta(self):
        tagItems = cmds.ls(dag=True)
        for item in tagItems:
            cmds.select(item)
            if cmds.attributeQuery('publishMetadata', n=item, exists=True):
                cmds.deleteAttr(item + '.publishMetadata')
                cmds.setAttr(item + '.useOutlinerColor', False)
                self.close()
                self.populatePublishAlembics()

    def populatePublishAlembics(self):
        metaItems = []
        allObjects = cmds.ls(dag=True)

        for obj in allObjects:
            if cmds.attributeQuery('publishMetadata', n=obj, exists=True):
                objectType = cmds.getAttr(obj + '.objectType')

                # If a shot set frame-range to time-slider
                if self.currentProj['projType'] == 'shot':
                    frameRange = str(int(cmds.playbackOptions(minTime=True, query=True))) + '-' + str(int(cmds.playbackOptions(maxTime=True, query=True)))
                # Else set 1-1
                if self.currentProj['projType'] == 'asset':
                    frameRange = '1-1'


                metaItems.append(obj)
                self.addMetaBtn.setEnabled(False)
                self.removeMetaBtn.setEnabled(True)

        if metaItems:
            rowPosition = self.alembicPublishWidget.rowCount()
            self.alembicPublishWidget.insertRow(rowPosition)
            self.alembicPublishWidget.setItem(rowPosition , 0, QtWidgets.QTableWidgetItem(metaItems[0]))
            try:
                self.alembicPublishWidget.setItem(rowPosition , 1, QtWidgets.QTableWidgetItem(self.currentProj['assetType']))
            except:
                self.alembicPublishWidget.setItem(rowPosition , 1, QtWidgets.QTableWidgetItem(objectType))

            self.alembicPublishWidget.setItem(rowPosition , 2, QtWidgets.QTableWidgetItem(self.currentProj['version']))
            self.alembicPublishWidget.setItem(rowPosition , 3, QtWidgets.QTableWidgetItem(frameRange))


    def publishAlembic(self):
        # Load the alembic plugin
        cmds.loadPlugin("AbcExport.mll", quiet=True)

        selectedRow = self.alembicPublishWidget.currentRow()
        publishItemRow = {'Name': self.alembicPublishWidget.item(selectedRow,0).text(),
                          'Type': self.alembicPublishWidget.item(selectedRow,1).text(),
                          'Version:': self.alembicPublishWidget.item(selectedRow,2).text(),
                          'FrameRange': self.alembicPublishWidget.item(selectedRow,3).text()}

        pStart = int(publishItemRow['FrameRange'].split('-')[0])
        pEnd = int(publishItemRow['FrameRange'].split('-')[1])

        publishItem = "-root " + publishItemRow['Name']
        alembicVersionPath = os.path.join(self.currentProj['publishDir'], 'v' + self.currentProj['version'])
        alembicPath = os.path.join(alembicVersionPath, self.currentProj['sceneName'] + '_publish.abc')
        #.replace("/","\\")

        if not os.path.isfile(alembicPath):
            if not os.path.exists(alembicVersionPath):
                os.makedirs(alembicVersionPath)
            command = "-attr ModelUsed -attr Namespace -attr scaleX -attr scaleY -attr scaleZ -attr visibility -frameRange %i %i -uvWrite -writeVisibility -worldSpace -eulerFilter -dataFormat hdf %s -file %s" % \
                      (pStart,
                       pEnd,
                       publishItem,
                       alembicPath)

            cmds.AbcExport ( j = command )


            currentTime = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            publishDB = shelve.open(self.publishDB)
            publishInfo = {'Artist': self.projectManager.user,
                           'Object': publishItemRow['Name'],
                           'Path': alembicPath,
                           'Time': currentTime,
                           'Type': publishItemRow['Type'],
                           'Version': self.currentProj['version'],
                           'Name': self.currentProj['name'],
                           'Task': self.currentProj['task'] }


            publishDB[str(self.currentProj['name'] + '_' + self.currentProj['task'])] = publishInfo
            publishDB.close()

            exitCode = 0
            if os.path.isfile(alembicPath) == False:
                exitCode += 1

            if exitCode == 0:
                # Takes the current version, pluses 1, filles it with zeros and conc back to correct filepath.
                newVersion = (self.currentProj['fileName'][:-6] + str(int(self.currentProj['version']) + 1).zfill(3))
                cmds.file(rename=str(newVersion))
                cmds.file(save=True, type='mayaAscii')
                self.close()

                om.MGlobal.displayInfo('All alembics were exported successfully! ')

            else:
                om.MGlobal.displayError('Something went wrong. Please contact your suporvisor.')

    def populatePublishRenders(self):
        try:
            imagesVersionDir = os.path.join(self.currentProj['projectDir'], 'images', 'v' + self.currentProj['version'])
            currentRenderLayerDirs = [i for i in os.listdir(imagesVersionDir) if not i.startswith('.')]
            failedLayersList = []
            self.renderLayersList = []

            # Checks for all files that matches
            for renderLayer in os.listdir(imagesVersionDir):
                renderFilesList = []
                fileCount = []
                totalFileSize = 0

                if not renderLayer.startswith('.'):
                    for renderFile in os.listdir(os.path.join(imagesVersionDir, renderLayer)):
                        try:
                            if renderFile.startswith(self.currentProj['sceneName'][:-5] + '_' + renderLayer + '_v' + self.currentProj['version']):
                                fileCount.append(int(renderFile[-8:-4]))
                                renderFileSize = os.path.getsize(os.path.join(imagesVersionDir, renderLayer, renderFile))
                                totalFileSize += os.path.getsize(os.path.join(imagesVersionDir, renderLayer, renderFile))
                                renderFileExt = renderFile[-3:]
                                renderFileList  = [renderFile, renderFileSize, renderFileExt]
                                renderFilesList.append(renderFileList)
                        except:
                            pass

                    if renderFilesList:
                        fileFrameRange = str(renderFilesList[0][0][-8:-4]) + '-' + str(renderFilesList[-1][0][-8:-4])
                        renderLayerPath = os.path.join(imagesVersionDir, renderLayer)
                        renderLayerDict = {'renderLayerName': renderLayer, 'Files': renderFilesList, 'fileFrameRange': fileFrameRange, 'renderLayerPath': renderLayerPath, 'fileCount': fileCount}
                        self.renderLayersList.append(renderLayerDict)
                    else:
                        # Adds renderLayers that are not matching format
                        failedLayersList.append(renderLayer)


            if self.renderLayersList:
                for renderLayer in self.renderLayersList:
                    # Looks at first and last frame and grabs its frame-range.
                    rowPosition = self.rendersPublishWidget.rowCount()
                    self.rendersPublishWidget.insertRow(rowPosition)
                    self.rendersPublishWidget.setItem(rowPosition , 0, QtWidgets.QTableWidgetItem(renderLayer['renderLayerName']))
                    self.rendersPublishWidget.setItem(rowPosition , 1, QtWidgets.QTableWidgetItem(self.currentProj['version']))
                    self.rendersPublishWidget.setItem(rowPosition , 2, QtWidgets.QTableWidgetItem(renderLayer['fileFrameRange']))
            '''
            if failedLayersList:
                failedRenderText = ""
                for i in failedLayersList:
                    if i == failedLayersList[-1]:
                        failedRenderText += str(i)
                    else:
                        failedRenderText += str(i) + ', '
                om.MGlobal.displayError('Failed to add {}. Filenames does not match renderLayer.'.format(failedRenderText.upper()))
            '''

        except:
            self.renderTab.setEnabled(False)

    def publishRenders(self):
        selectedIndexes = self.rendersPublishWidget.selectedIndexes()
        selectedRowList = ""

        # Takes the data and turns it into string.
        for i in selectedIndexes:
            selectedRowList += i.data() + ' '

        errorCode = 0
        badFramesEXR = []
        badFramesBytes = []
        incorrectFrameRange = []
        missingFrames = []
        renderLayersPublishList = []


        # Gets the framerange
        shotBreakDown = self.projectManager.getFrameRange(self.currentProj['name'])
        for item in shotBreakDown:
            if item['Shot_Code'] == self.currentProj['name']:
                shotFrameRange = item['FrameRange']
                shotFrameRangeStart = str(item['FrameRange']).split('-')[0]
                shotFrameRangeEnd = str(item['FrameRange']).split('-')[-1]


        # If contains string then we know what is selected.
        for renderLayer in self.renderLayersList:
            if renderLayer['renderLayerName'] in selectedRowList:
                renderDst = os.path.join(self.currentProj['publishDir'], 'v' + self.currentProj['version'], renderLayer['renderLayerName'])
                frameStart = int(renderLayer['Files'][0][0][-8:-4])
                frameEnd = int(renderLayer['Files'][-1][0][-8:-4])

                totalPossibleFramesList = []
                totalFramesList = []

                # If frame range is not matching shot append list with info.
                if frameStart != shotFrameRangeStart and frameEnd != shotFrameRangeEnd:
                    incorrectFrameRange.append([renderLayer['renderLayerName'], frameStart, frameEnd])

                for i in range(frameStart, frameEnd+1):
                    totalPossibleFramesList.append(i)

                # Gets the missing frames using difference
                framesDifference = (set(totalPossibleFramesList).difference(renderLayer['fileCount']))
                for i in framesDifference:
                    missingFrames.append(renderLayer['Files'][0][0][0:-8] + str(i).zfill(4) + '.' + str(renderLayer['Files'][0][2]))

                #renderFile[0], renderFileSize[1], renderFileExt[2]
                for frame in renderLayer['Files']:
                    if frame[2] != 'exr':
                        badFramesEXR.append(frame)

                    if int(frame[1]) < 100:
                        badFramesBytes.append(frame)

                # Checks if framerange is matching
                renderLayersPublishList.append([renderLayer['renderLayerPath'], renderDst])

        # If there are items in the list to be published, continue
        if renderLayersPublishList:
            # If there are bad frames ie not EXR or below 100 bytes, warn user and prompt.
            if badFramesEXR or badFramesBytes or incorrectFrameRange:
                popupMessage = QtWidgets.QMessageBox()
                popupMessage.setWindowTitle('Render Publish Warning')
                popupMessage.setText('One or more problems have been found with the files you are trying to publish.\nPress SHOW DETAILS to get more info.\nPress YES to proceed with publish.')

                if incorrectFrameRange:
                    inCorrectFrameRangeWarning = 'Render-layers containing frames with wrong frame-range.\nShot: {}-{}\n'.format(shotFrameRangeStart, shotFrameRangeEnd)
                    for i in incorrectFrameRange:
                        inCorrectFrameRangeWarning += (str(i[0]) + ': ' + str(i[1]) + '-' + str(i[2]) + '\n')
                else:
                    inCorrectFrameRangeWarning = ''

                if missingFrames:
                    missingFramesWarning = '\nMissing Frames:\n'
                    for i in missingFrames:
                        missingFramesWarning += (str(i) + '\n')
                else:
                    missingFramesWarning = ''

                if badFramesEXR:
                    badFramesEXRWarning = '\nFrames that are not EXR:\n'
                    for i in badFramesEXR:
                        badFramesEXRWarning += (str(i[0]) + '\n')
                else:
                    badFramesEXRWarning = ''

                if badFramesBytes:
                    badFramesBytesWarning = "\nFrames under 100 bytes:\n"
                    for i in badFramesBytes:
                        badFramesBytesWarning += (str(i[0]) + ', ' + str(i[1]) + ' bytes' + '\n')
                else:
                    badFramesBytesWarning = ''

                popupMessage.setDetailedText(inCorrectFrameRangeWarning + missingFramesWarning + badFramesEXRWarning + badFramesBytesWarning)
                popupMessage.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
                popupMessageRet = popupMessage.exec_()

                if popupMessageRet == popupMessage.Yes:
                    errorCode = 0

                elif popupMessageRet == popupMessage.Cancel:
                    errorCode = 1

            # Checks if errorCode suceeded and if there are items in list to publish
            if errorCode == 0:
                exitCode = 0
                pathExists = [i[1].replace("/", "\\") for i in renderLayersPublishList if os.path.exists(i[1])]

                for r in renderLayersPublishList:
                    try:
                        shutil.copytree(r[0], r[1])
                    except:
                        exitCode = 1

                if exitCode == 0:
                    # Copies the maya file.
                    shutil.copy(self.currentProj['filePath'], self.currentProj['publishDir'])
                    # Takes the current version, pluses 1, filles it with zeros and conc back to correct filepath.
                    newVersion = (self.currentProj['fileName'][:-6] + str(int(self.currentProj['version']) + 1).zfill(3))
                    cmds.file(rename=str(newVersion))
                    cmds.file(save=True, type='mayaAscii')
                    self.close()
                    self.popupMessage('Sucess', 'Publishing renders finished successfully!')
                else:
                    self.popupMessage('ERROR', 'Failed publishing renders')

            elif errorCode == 1:
                pass

            else:
                pass

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

    def quickDaily(self):
        selectedIndexes = self.rendersPublishWidget.selectedIndexes()
        selectedRowList = ""

        # Takes the data and turns it into string.
        for i in selectedIndexes:
            selectedRowList += i.data() + ' '

        renderLayersPublishList = []

        # If contains string then we know what is selected.
        for renderLayer in self.renderLayersList:
            if renderLayer['renderLayerName'] in selectedRowList:
                pass

                imagesVersionDir = os.path.join(self.currentProj['projectDir'], 'images', 'v' + self.currentProj['version'])
                currentRenderLayerDirs = [i for i in os.listdir(imagesVersionDir) if not i.startswith('.')]
                numCurrentFiles = []


                reviewDir = self.currentProj['projectDir'].replace("work/maya/","review/maya")
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

                # Checks for all files that matches
                renderLayerFileList = [i for i in os.listdir(os.path.join(imagesVersionDir, renderLayer['renderLayerName']))
                                                                if i.startswith(self.currentProj['sceneName'][:-5] + '_' + renderLayer['renderLayerName'] + '_v' +
                                                                self.currentProj['version'])]

                frameRange = ('1,' + str(len(renderLayerFileList)))

                # Gets the extension of the first file in list
                renderLayerExt = renderLayerFileList[0][-3:]
                nukeBashInput = os.path.join(imagesVersionDir, renderLayer['renderLayerName'], str(renderLayerFileList[0][0:-8:] + '####.' + renderLayerExt)).replace("/","\\")
                nukeBashOutput = os.path.join(reviewDir, str(renderLayerFileList[0][:-8] + 'review_r' + revisionID)).replace("/","\\")



                # Creates the shell command to launch nuke with right commands
                nukeBashCommand = (str(self.projectManager.nukePath) + ' -r' + " " +
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

        #except:
        #    om.MGlobal.displayError('No rendered images can be found.')

    def syncFrameRange(self):
        try:
            if self.currentProj['projType'] == 'shot':
                shotBreakDown = self.projectManager.getFrameRange(self.currentProj['name'])
                for item in shotBreakDown:
                    if item['Shot_Code'] == self.currentProj['name']:
                        startFrame = str(item['FrameRange']).split('-')[0]
                        endFrame = str(item['FrameRange']).split('-')[1]

                        cmds.playbackOptions(minTime=(startFrame))
                        cmds.playbackOptions(animationStartTime=(startFrame))
                        cmds.playbackOptions(maxTime=(endFrame))
                        cmds.playbackOptions(animationEndTime=(endFrame))
                        cmds.setAttr("defaultRenderGlobals.startFrame", startFrame)
                        cmds.setAttr("defaultRenderGlobals.endFrame", endFrame)

            else:
                pass
        except:
            pass

    def getCurrentProj(self):
        projectDir = cmds.workspace(query=True, rootDirectory=True)
        filePath = cmds.file(query=True, sn=True)
        fileName = filePath.split('/')[-1]
        sceneName = fileName.split('.')[0]
        name = fileName.split('_')[0]
        task = sceneName.split('_')[-2]
        version = sceneName.split('v')[1]
        publishDir = projectDir.replace("work/maya/","publish/maya")

        currentProj = {'projectDir': projectDir, 'filePath': filePath, 'fileName': fileName, 'sceneName': sceneName,
                       'name': name, 'task': task, 'version': version, 'publishDir': publishDir}

        # Gives projecttype specific variables
        if 'assets' in projectDir:
                currentProj['assetType'] = projectDir.split('/')[-6]
                currentProj['projType'] = 'asset'
        elif 'shots' in projectDir:
                currentProj['projType'] = 'shot'

        return (currentProj)

    def popupMessage(self, title, message):
        popupMessage = QtWidgets.QMessageBox()
        popupMessage.setWindowTitle(title)
        popupMessage.setText(message)
        popupMessage.setStandardButtons(QtWidgets.QMessageBox.Ok)
        popupMessage = popupMessage.exec_()

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
            om.MGlobal.displayInfo('Renderpaths set successfully.')
        except:
            om.MGlobal.displayError('V-Ray is not loaded or not set as current renderer.')

    def openImagesFolder(self):
        selectedIndexes = self.rendersPublishWidget.selectedIndexes()
        selectedRowList = ""

        # Takes the data and turns it into string.
        for i in selectedIndexes:
            selectedRowList += i.data() + ' '

        renderLayersPublishList = []

        # If contains string then we know what is selected.
        for renderLayer in self.renderLayersList:
            if renderLayer['renderLayerName'] in selectedRowList:
                imagesFolder = os.path.join(self.currentProj['projectDir'], 'images','v' + self.currentProj['version'], renderLayer['renderLayerName'])
                try:
                    os.startfile(imagesFolder)
                except:
                    subprocess.call(["open", imagesFolder])

def showUI():
    ui = projectManagerTools()
    ui.show()
    return ui
