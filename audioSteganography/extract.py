import sys
from PyQt4 import QtCore, QtGui, uic
from pydub import AudioSegment
from struct import unpack, pack
import numpy as np
import wave
import scipy.io.wavfile
import random

form_class_extract = uic.loadUiType("extract.ui")[0]

class extractWindowClass(QtGui.QMainWindow, form_class_extract):
	def __init__(self, parent = None):
		super(extractWindowClass, self).__init__(parent = None)
		self.setupUi(self)
		self.filenameAudio = ""
		self.browseButton.clicked.connect(self.btnBrowseClicked)
		self.extractButton.clicked.connect(self.btnExtractClicked)
		self.exitButton.clicked.connect(self.btnExitClicked)

	def extractData(self, seedVal, inputFile, outputFile):
		rate1, data = scipy.io.wavfile.read(inputFile)
		seedVal = int(seedVal)
		random.seed(seedVal)
		permutation = []
		
		binaryMessage = []
		lengthBinary = ""
		
		for i in range(8):
			perm = random.randint(25,len(data))
			if(perm not in permutation and data[perm] != ''):
				permutation.append(perm)
			else:
				i -= 1

		for i in range(8):
			lengthBinary += str(data[permutation[i]]%2)
		
		length = int(lengthBinary,2)
		print length

		for i in range(length*8):
			perm = random.randint(25,len(data))
			if(perm not in permutation and data[perm] != ''):
				permutation.append(perm)
			else:
				i -=1

		outputMessage = ""
		for i in range(1,length+1):
			character = ''
			characterBinary = ""
			for j in range(8):
				characterBinary += str(data[permutation[8*i+j]]%2)
			character = chr(int(characterBinary,2))	
			outputMessage += character
		
		outputFile = outputFile+".txt"
		f = open(outputFile,"w")
		f.write(outputMessage)	

	def btnBrowseClicked(self):
		self.filenameAudio = QtGui.QFileDialog.getOpenFileName(w, 'Open File', '/')
		# print self.fileNameAudio
		self.filenameLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.filenameLabel.setText(self.filenameAudio)

	def btnExtractClicked(self):
		outputFile = str(self.filenameBox.toPlainText())
		key = str(self.keyBox.toPlainText())
		self.extractData(key, self.filenameAudio, outputFile)
		self.keyBox.clear()
		self.filenameBox.clear()
		self.filenameLabel.setText("")

		notification = "Message saved to " + outputFile + ".txt" 
		self.popupLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.popupLabel.setText(notification)

	def btnExitClicked(self):
		self.close()

# app = QtGui.QApplication(sys.argv)
# w = QtGui.QWidget()		
# extractWindow = extractWindowClass()
# extractWindow.show()
# app.exec_()
