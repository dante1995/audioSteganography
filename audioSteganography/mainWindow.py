import sys
from PyQt4 import QtCore, QtGui, uic
from embed import embedWindowClass
from extract import extractWindowClass

mainwindowGUI = uic.loadUiType("mainWindow.ui")[0]
form_class_embed = uic.loadUiType("embed.ui")[0]
form_class_extract = uic.loadUiType("extract.ui")[0]

class MainWindowClass(QtGui.QMainWindow, mainwindowGUI):
	def __init__(self, parent = None):
		super(MainWindowClass, self).__init__(parent = None)
		self.setupUi(self)
		self.embedButton.clicked.connect(self.btnEmbedClicked)
		self.extractButton.clicked.connect(self.btnExtractClicked)
		self.exitButton.clicked.connect(self.btnExitClicked)

	def btnEmbedClicked(self):
		self.embedWindow = embedWindowClass()	
		self.embedWindow.show()

	def btnExtractClicked(self):
		self.extractWindow = extractWindowClass()	
		self.extractWindow.show()

	def btnExitClicked(self):
		self.close()			


if __name__ == '__main__':

	app = QtGui.QApplication(sys.argv)
	w = QtGui.QWidget()		
	mainWindow = MainWindowClass()
	mainWindow.show()
	app.exec_()