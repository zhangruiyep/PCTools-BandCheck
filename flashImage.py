import os

class writeFileRet():
	def __init__(self, result, msg):
		self.result = result
		self.msg = msg

class flashImage():
	def __init__(self, filename, size, partfiles, progressCbFunc):
		self.filename = filename
		self.size = size
		self.partfiles = partfiles
		self.updateProgress = progressCbFunc
	
	def writeFile(self):
		fo = open(self.filename, "wb")
		paddingChar = [255]
		for fdata in self.partfiles:
			if fo.tell() > fdata[1]:
				retval = writeFileRet("Error", "OVERLAP %s" % fdata[0])
				return retval
				
			self.updateProgress(float(fo.tell())/self.size)
			
			# fill until part file start
			for i in range(fo.tell(), fdata[1]):
				fo.write(bytearray(paddingChar))

			self.updateProgress(float(fo.tell())/self.size)
			
			try:
				fi = open(fdata[0], "rb")
			except:
				retval = writeFileRet("Error", "%s can not open" % fdata[0])
				return retval
				
			# copy part file data				
			fo.write(fi.read())
			if (fo.tell() > self.size):
				retval = writeFileRet("Error", "%s out of flash" % fdata[0])
				return retval
			self.updateProgress(float(fo.tell())/self.size)
			
			fi.close()
		# padding to end fo file
		for i in range(fo.tell(), self.size):
			fo.write(bytearray(paddingChar))
		self.updateProgress(float(fo.tell())/self.size)
		fo.close()
		retval = writeFileRet("OK", "Done")
		return retval
	
