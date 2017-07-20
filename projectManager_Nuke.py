from PySide2 import QtWidgets, QtUiTools

class projectManagerNuke(QtWidgets.QDialog):
    def __init__(self):
        super(projectManagerNuke, self).__init__()
        self.publishDB = os.path.join(self.projectManager.projectFolder, 'tools', 'scripts', 'publish', 'publishDB')
