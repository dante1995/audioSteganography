import sys
from PyQt4 import QtCore, QtGui, uic
from pydub import AudioSegment
from struct import unpack, pack
import numpy as np
import wave
import scipy.io.wavfile
import random

form_class_embed = uic.loadUiType("embed.ui")[0]

class embedWindowClass(QtGui.QMainWindow, form_class_embed):
	def __init__(self, parent = None):
		super(embedWindowClass, self).__init__(parent = None)
		self.setupUi(self)
		self.fileNameText = ""
		self.fileNameAudio = ""
		self.browseAudio.clicked.connect(self.btnBrowseAudioClicked)
		self.browseFile.clicked.connect(self.btnBrowseTextfileClicked)
		self.embedButton.clicked.connect(self.btnEmbedClicked)
		self.closeButton.clicked.connect(self.btnCloseClicked)

	def encodeData(self, seedVal, message, inputFile, outputFile):
		seedVal = int(seedVal)
		random.seed(seedVal)
		permutation = []
		binaryMessage = []
		message = message.strip()
		print message
		binaryMessage.append(bin(len(message))[2:].zfill(8)) #length of message appended at the beginning
		
		for character in message:
			binaryMessage.append(bin(int(ord(character)))[2:].zfill(8))

		rate, data = scipy.io.wavfile.read(inputFile)
		
		for i in range(len(message)*8+8):
			perm = random.randint(25,len(data))
			if(perm not in permutation and data[perm] != ''):
				permutation.append(perm)
			else:
				i -= 1

		print len(permutation)		
		asci = binaryMessage[0]
		count = 0
		for bit in asci:
			val = ord(bit) - ord('0')
			if(data[permutation[count]]%2 != val%2):
				data[permutation[count]] += 1
			print permutation[count], data[permutation[count]]	
			count += 1

		for i in range(1,len(message)+1):
			print i
			asci = binaryMessage[i]
			count = 0
			for bit in asci:
				val = ord(bit) - ord('0')
				if(data[permutation[8*i+count]]%2 != val%2):
					data[permutation[8*i+count]] += 1
				print permutation[8*i+count], data[permutation[8*i+count]]	
				count += 1
		print binaryMessage		

		scipy.io.wavfile.write(outputFile,rate,data)

	def btnBrowseAudioClicked(self):
		self.fileNameAudio = QtGui.QFileDialog.getOpenFileName(w, 'Open File', '/')
		# print self.fileNameAudio
		self.audioFilenameLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.audioFilenameLabel.setText(self.fileNameAudio)		

	def btnBrowseTextfileClicked(self):
		self.fileNameText = QtGui.QFileDialog.getOpenFileName(w, 'Open File', '/')
		# print self.fileNameText
		self.textFilenameLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.textFilenameLabel.setText(self.fileNameText)	

	def btnEmbedClicked(self):
		textMessage = str(self.messageBox.toPlainText())
		print textMessage
		try:
			if(textMessage == ""):
				f = open(self.fileNameText, "r")
				textMessage = str(f.read())
		except:
			pass
		outputFile = self.filenameBox.toPlainText()
		key = self.keyBox.toPlainText()
		self.encodeData(key, textMessage, self.fileNameAudio, outputFile)
		self.messageBox.clear()
		self.filenameBox.clear()
		self.keyBox.clear()
		self.textFilenameLabel.setText("")
		self.audioFilenameLabel.setText("")
		notification = "Output saved to " + outputFile
		self.messageLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.messageLabel.setText(notification)

	def btnCloseClicked(self):
		self.close()	
		
# app = QtGui.QApplication(sys.argv)
# w = QtGui.QWidget()		
# embedWindow = embedWindowClass()
# embedWindow.show()
# app.exec_()
