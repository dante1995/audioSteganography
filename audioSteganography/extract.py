import sys
from PyQt4 import QtCore, QtGui, uic
from pydub import AudioSegment
from struct import unpack, pack
import numpy as np
import wave
import scipy.io.wavfile
import random
import hashlib
import Image
import itertools
import os

form_class_extract = uic.loadUiType("extract.ui")[0]

class extractWindowClass(QtGui.QMainWindow, form_class_extract):
	def __init__(self, parent = None):
		super(extractWindowClass, self).__init__(parent = None)
		self.setupUi(self)
		self.fileNameAudio = ""
		self.audioFileExtensions = ["mp3", "wav"]
		self.imageFileExtensions = ["jpg", "png"]
		self.fileType = "audio"
		self.browseButton.clicked.connect(self.btnBrowseClicked)
		self.extractButton.clicked.connect(self.btnExtractClicked)
		self.exitButton.clicked.connect(self.btnExitClicked)

	def extractDataAudio(self, seedVal, inputFile, outputFile):
		rate1, data = scipy.io.wavfile.read(inputFile)
		# seedVal = int(seedVal)
		print "seedVal"
		print seedVal
		m = hashlib.sha256(seedVal)
		seedVal = m.hexdigest()
		print "hex" + str(seedVal)
		seedVal = int(seedVal,16)
		print "int" + str(seedVal)
		random.seed(seedVal)
		permutation = []
		
		binaryMessage = []
		lengthBinary = ""
		
		try:
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
		except:
			notification = "Wrong key entered!!" 
			self.popupLabel.setAlignment(QtCore.Qt.AlignCenter)
			self.popupLabel.setText(notification)	
		
		outputFile = outputFile+".txt"
		f = open(outputFile,"w")
		f.write(outputMessage)	

	def extract_msg(self, image):
		
		def get_least_sig_bits(image):
			"""get the least significant bits from image"""
			pxls = image.getdata()
			return (cc & 1 for pxl in pxls for cc in pxl)

		bits = get_least_sig_bits(image)

		def left_shift(n):
			# reduce(function, iterable[, initializer])
			# reduce(lambda x,y: x+y, [1, 2, 3, 4, 5]) calculates ((((1+2)+3)+4)+5)
			# apply function of two arguments cumulatively to the items of iterable,
			# from left to right, so as to reduce the iterable to a single value.

			# create a an iterator of the first n bits
			n_bits = itertools.islice(bits, n)
			# bitwise or n bits to get an int
			return reduce(lambda x,y: x << 1 | y, n_bits, 0)

		def next_ch():
			return chr(left_shift(8))

		def defer(func):
			return func()

		n_pxls = image.size[0] * image.size[1]
		n_bnds = len(image.getbands())

		# get data length from 8 bit as_32_bit_string
		data_length = left_shift(32)
		if n_pxls * n_bnds > 32 + data_length * 8:
			# defer next_chr data_length times
			return ''.join(itertools.imap(defer, itertools.repeat(next_ch, data_length)))	
	
	def extractDataImage(self, seedVal, inputFile, outputFile):
		image = Image.open(inputFile)
		outputMessage = self.extract_msg(image)
		outputFile = outputFile+".txt"
		f = open(outputFile,"w")
		f.write(outputMessage)

	def btnBrowseClicked(self):
		self.fileNameAudio = QtGui.QFileDialog.getOpenFileName(w, 'Open File', '/')
		# print self.fileNameAudio
		self.filenameLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.filenameLabel.setText(self.fileNameAudio)

	def btnExtractClicked(self):
		outputFile = str(self.filenameBox.toPlainText())
		key = str(self.keyBox.toPlainText())

		self.inputFileName = (self.fileNameAudio).split('.')
		self.inputFileName = self.inputFileName[len(self.inputFileName)-1]
		print self.inputFileName

		if(self.inputFileName in self.imageFileExtensions):
			self.fileType = "image"

		print self.fileType	
		print(self.fileNameAudio)	
		if(self.fileType == "audio"):
			self.extractDataAudio(key, self.fileNameAudio, outputFile)
		else:
			self.extractDataImage(key, str(self.fileNameAudio), outputFile)

		self.keyBox.clear()
		self.filenameBox.clear()
		self.filenameLabel.setText("")

		notification = "Message saved to " + outputFile + ".txt" 
		self.popupLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.popupLabel.setText(notification)

	def btnExitClicked(self):
		self.close()

app = QtGui.QApplication(sys.argv)
w = QtGui.QWidget()		
extractWindow = extractWindowClass()
extractWindow.show()
app.exec_()
