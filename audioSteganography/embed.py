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



form_class_embed = uic.loadUiType("embed.ui")[0]


class embedWindowClass(QtGui.QMainWindow, form_class_embed):
	def __init__(self, parent = None):
		super(embedWindowClass, self).__init__(parent = None)
		self.setupUi(self)
		self.fileNameText = ""
		self.fileNameAudio = ""
		self.audioFileExtensions = ["mp3", "wav"]
		self.imageFileExtensions = ["jpg", "png"]
		self.fileType = "audio"
		self.browseAudio.clicked.connect(self.btnBrowseAudioClicked)
		self.browseFile.clicked.connect(self.btnBrowseTextfileClicked)
		self.embedButton.clicked.connect(self.btnEmbedClicked)
		self.closeButton.clicked.connect(self.btnCloseClicked)

	def encodeDataAudio(self, seedVal, message, inputFile, outputFile):
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
		message = message.strip()
		# print message
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

		# print len(permutation)		
		asci = binaryMessage[0]
		count = 0
		for bit in asci:
			val = ord(bit) - ord('0')
			if(data[permutation[count]]%2 != val%2):
				data[permutation[count]] += 1
			# print permutation[count], data[permutation[count]]	
			count += 1

		for i in range(1,len(message)+1):
			print i
			asci = binaryMessage[i]
			count = 0
			for bit in asci:
				val = ord(bit) - ord('0')
				if(data[permutation[8*i+count]]%2 != val%2):
					data[permutation[8*i+count]] += 1
				# print permutation[8*i+count], data[permutation[8*i+count]]	
				count += 1
		# print binaryMessage		

		scipy.io.wavfile.write(outputFile,rate,data)

	def as_32_bit_string(self, n):
		"""return param n(must be an int or char) packed in a 32 bit string"""
		# rightshift n bytewise from 0 to 3 bytes. use chr(n) to chop 1 byte
		# representation of the current shifting position
		byte_string = ''
		for c in range(24, -8, -8):
			byte_string += chr(n >> c & 0xff)
		# return n packed in a 32 bit string
		return byte_string

	def as_bits(self, data):
		"""
		returns a generator that provides a bit representation
		of the input data
		"""
		# bit representation of the payload
		# itertools.product: cartesian product of input iterables
		# product(A, B) returns the same as ((x,y) for x in A for y in B)

		# all chars in data will be shifted 7,6,5,4,3,2,1,0 bits to the right
		# thus a binary/bit representation of char is created
		return (ord(char) >> shift & 1
			for char, shift in itertools.product(data, range(7, -1, -1)))

	def n_tupled(self, data, n, fillvalue):
		"""
		returns an iterator that packs data in tuples of length n
		padded with the fillvalue
		"""
		# izip_longest(*iterables[, fillvalue])
		# izip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
		# make an iterator that aggregates elements from each of the iterables.
		# if the iterables are of uneven length, missing values are filled-in with
		# fillvalue. iteration continues until the longest iterable is exhausted.

		# cast data to an iterator and pass it n times in a tuple to izip_longest
		# the generator exhaustes itself while zipping - thats why passing *[iterator]*n works
		return itertools.izip_longest(*[iter(data)] *n, fillvalue=fillvalue)

	def hide_msg(self, image, data):
		""""
		hide the payload in the least significant bits of the image
		return the manipulated image or None
		"""

		def set_least_sig_bit(cc, bit):
			"""
			set the least significant bit of a color component
			"""
			# get the lsb by a bitwise and of the color component and
			# the inversion of 1
			# manipulate the lsb by a bitwise or with the bit to set
			return cc & ~1 | bit

		def hide_bits(pixel, bits):
			"""
			hide the bit in a color component
			return the tupled pixel with manipulated lsb
			"""
			# tuple the 3 color components and the 3 payload bits by
			# passing them to the zip function. zip returns a list of tuples
			# instead of an iterator(like izip)
			print type(pixel)
			return tuple(itertools.starmap(set_least_sig_bit, zip(pixel, bits)))

		hdr = self.as_32_bit_string(len(data))
		payload = '%s%s' % (hdr, data)
		n_pxls = image.size[0]*image.size[1]
		n_bnds = len(image.getbands())

		if len(payload)*8 <= n_pxls*n_bnds:
			img_data = image.getdata()
			# create a generator(with tuples of length n_bnds) that
			# iterates over every bit of the payload
			payload_bits = self.n_tupled(self.as_bits(payload), n_bnds, 0)
			# starmap - makes an iterator that calls the hide_bits function using
			# arguments obtained from the zipped image data and payload (tupled by izip)
			new_img_data = itertools.starmap(hide_bits, itertools.izip(img_data, payload_bits))
			# create the image with the manipulated least significant bits
			image.putdata(list(new_img_data))
			print "message successfully hidden in image!!"
			return image


	def encodeDataImage(self, seedVal, message, img, outputFile):
		print img
		image = Image.open(img)
		secret = self.hide_msg(image, message)
		name, ext = os.path.splitext(img)
		secret.save('%s.%s' % (outputFile, ext))
		i = Image.open('%s.%s' % (outputFile,ext))	

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
		key = str(self.keyBox.toPlainText())

		self.inputFileName = (self.fileNameAudio).split('.')
		self.inputFileName = self.inputFileName[len(self.inputFileName)-1]
		print self.inputFileName

		if(self.inputFileName in self.imageFileExtensions):
			self.fileType = "image"

		print self.fileType	
		print(self.fileNameAudio)	
		if(self.fileType == "audio"):
			self.encodeDataAudio(key, textMessage, self.fileNameAudio, outputFile)
		else:
			self.encodeDataImage(key, textMessage, str(self.fileNameAudio), outputFile)
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
		
app = QtGui.QApplication(sys.argv)
w = QtGui.QWidget()		
embedWindow = embedWindowClass()
embedWindow.show()
app.exec_()
