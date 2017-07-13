from projManager import projectManager
from PySide2 import QtWidgets, QtUiTools
from maya import cmds
import os

class PublishUI(QtWidgets.QDialog):

    def __init__(self):
        super(PublishUI, self).__init__()
        self.build_publish_UI()

    def build_publish_UI(self):
        loader = QtUiTools.QUiLoader()
        self.publish_ui = loader.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'UI', 'publish.ui'))

        self.publish_alembic_layout = self.publish_ui.findChild(QtWidgets.QVBoxLayout, 'verticalLayout_7')

        # Function to add alembics from selection
        self.publishAbc()


        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.publish_ui)
        self.setLayout(mainLayout)

    def publishAbc(self):
        selected_geo = cmds.ls(sl=True)
        for item in selected_geo:
            self.item = QtWidgets.QCheckBox(item)

            self.publish_alembic_layout.addWidget(self.item)
def showUI():
    ui = PublishUI()
    ui.show()
    return ui
