from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import codecs
import os.path
import os, sys

import threading
import time

#
# Utilty to read BER Asn1 File in Python3 with GUI Tk
#
# v1.0 - First Version
# v1.1 - 07/09/2020 - Add TAP Notation and Tag Hex Value
# v1.2 - 08/09/2020 - Add offset Start and offset End 
# v1.3 - 09/09/2020 - Add scrollbar to TXT widget and Icon
# v1.4 - 13/09/2020 - Add Threads Managment and Progress Bar
# v1.5 - 27/09/2020 - Add Stop Button during reading file
# v2.0 - Add Convert File
# v2.1 - Bug Fixing in Convertion
# v2.1.1 - Bug Fixing in GUI
# v2.2 - Search Function

class tagType:
	def __init__(self, convType, descrTag):
		self.convType = convType
		self.descrTag = descrTag
	def getConvType(self):
		return self.convType	
	def getDescrTag(self):
		return self.descrTag	

class Application(object):

# Function to convert values in A(Ascii) N(Number) or B(Binary)
	def convValueFromHex(self, valueHex, convType):
		valueConvToRet=valueHex
		try:
			if convType == "A" and len(valueHex) > 0:
				valueConvToRet=codecs.decode(codecs.decode(valueHex,'hex'),'ascii')
			if convType == "N" and len(valueHex) > 0:
				valueConvToRet=str(int(valueHex,16))
			if convType == "B" and len(valueHex) > 0:
				end_length = len(valueHex) * 4
				hex_as_int = int(valueHex, 16)
				hex_as_binary = bin(hex_as_int)
				valueConvToRet = hex_as_binary[2:].zfill(end_length)
		except:
			valueConvToRet="Error in Convertion"
		return valueConvToRet

	def getXCenter(self):
		root_x = root.winfo_rootx()
		dimx = root.winfo_width()
		return root_x + int(dimx/2)

	def getYCenter(self):
		root_y = root.winfo_rooty()
		dimy = root.winfo_height()
		return root_y + int(dimy/2)

# Function to stop thread
	def stopThread(self, t1):
		global stop_threads
		stop_threads = True

# Function for progress Bar
	def progress_file(self, t1, fileasn1, filedim):
		win = Toplevel(root)
		win_x = self.getXCenter()
		win_y = self.getYCenter()
		win.geometry(f'+{win_x}+{win_y}')
		win.grab_set()
		win.resizable(height = False, width = False)
		win.title("Reading File")
		win.rowconfigure(0, weight=1)
		win.rowconfigure(1, weight=1)
		win.rowconfigure(2, weight=1)
		win.rowconfigure(3, weight=1)
		win.columnconfigure(0, weight=1)
		win.columnconfigure(2, weight=1)
		progress = ttk.Progressbar(win, orient = HORIZONTAL, 
            length = 100, mode = 'determinate') 
		progress.grid(row=1, column=1)
		b = Button(win, text="Stop", command= lambda: self.stopThread(t1, ))
		b.grid(row=3, column=1)
		progress['value'] = 0
		t1.join(timeout=1)
		while t1.isAlive() is True:
			progress['value'] = fileasn1.tell()*100/filedim
			t1.join(timeout=1)
		progress['value'] = fileasn1.tell()*100/filedim
		fileasn1.close()
		win.destroy()

# Function to delete txtTrad
	def limpia(self):
		self.txtTrad.delete(1.0, END)

# Function to check infinite End 
	def CtrlInfinitiveEnd(self, filea):
		curpos=filea.tell()
		for i in range(2):
			if self.readAsn1(filea) != "00":
				break
		if i == 2:
			return 1
		filea.seek(curpos)
		return 0

# Function to get primitive value
	def GetPrimitiveValue(self,filea, lenValue):
		sretvalue=""
		ind=0
		while (lenValue > 0 and (ind < lenValue)) or (lenValue < 0 and self.CtrlInfinitiveEnd(filea) == 0): 
			sretvalue="%s%s" % (sretvalue,self.readAsn1(filea))
			ind = ind + 1
		return sretvalue    

# Function to read Asn1 file
	def readAsn1(self,filea):
		aByte=""
		try:
			bByte=filea.read(1)
			if len(bByte) > 0:
				aByte="%02x" % ord(bByte)
		except IOError as e:
			print("I/O Error (%s): %s" % (e.errno, e.strerror))
			self.txtTrad.insert(INSERT,"I/O Error (%s): %s" % (e.errno, e.strerror))
		return aByte

# Recursive Function to read Tag
	def getTag(self, filea, iLevel, offSetTo):

#		print("In GetTag")
		startByte=filea.tell()
		taghex=self.readAsn1(filea)

		if taghex == '':
			return 1
		next=int(taghex,16)

		next = next & 0xff
		if next == 0x00:
			return 0
		
		id = (next & 192) >> 6
		if ((next & 32) >> 5) == 1:
			flag="false"
		else:
			flag="true"

		tag=next & 31

		if tag == 31:
			taghex= "%s%s" % (taghex,self.readAsn1(filea))
			nextbis=int(taghex,16)
			nextbis=nextbis & 0xff

			tag=nextbis & 127
			while 128 == (nextbis & 128):
				appo=self.readAsn1(filea)
				if appo == '':
				   break
				taghex= "%s%s" % (taghex,appo)
				nextbis=int(taghex,16)
				nextbis=nextbis & 0xff
				tag = (tag << 7) | ( nextbis & 127)

# OffSet
		offSet = "%010d" % (startByte)

# Tag rappresentation

		if self.bTypeTAP.get() == False:
			CodeTag =  "%s-%s" % (id,tag)
		else:
			CodeTag =  "%s" % (tag)

		global CodeTagToDisplay
		tagSplit = CodeTagToDisplay.split(".")
		if len(tagSplit[0]) > 0 and len(tagSplit) > 1:
			for ind in range(iLevel):
				if ind > 0:
					CodeTagToDisplay = CodeTagToDisplay + "." + tagSplit[ind]
				else:
					CodeTagToDisplay = tagSplit[ind]
		if iLevel > 0:			
			CodeTagToDisplay = CodeTagToDisplay + "." + CodeTag
		else:
			CodeTagToDisplay = CodeTag
# Tag Name
		if len(convHash) > 0:				
			if CodeTag in convHash:
				CodeTagToDisplayR = "[" + CodeTagToDisplay + "] {" + convHash[CodeTag].getDescrTag().strip() + "}"
			else:
				CodeTagToDisplayR = "[" + CodeTagToDisplay + "]"	
		else:
			CodeTagToDisplayR = "[" + CodeTagToDisplay + "]"	

# Hex Tag
		if self.bHexRapr.get() == True:
			CodeTag = CodeTag +  " [%s] " % (taghex)

		appo=self.readAsn1(filea)
		if appo == '':
			return 1

		next=int(appo,16)
		nbyte=next & 127

		if (next&128) == 0 :
			length=nbyte
		else:
			if nbyte > 0 :
				if nbyte > 4 :
					codeTag="ERROR TAG"
					return 1
				else:
					appo=self.readAsn1(filea)
					if appo == '':
						return 1
					next=int(appo,16)
					length=next
					for contabyte in range(1,nbyte):
						appo=self.readAsn1(filea)
						if appo == '':
							return 1
						next=int(appo,16)
						length=(length<<8) | next
			else:
				length = -1
		
		#sIndent=""        
		#for i in range(iLevel):
		#	sIndent="\t%s" % sIndent

# OffSet
		offSet = offSet + ":%03d" % (iLevel+1)

		sTagToPrint=""
		if length < 0:
			sTagToPrint="%s %s length : indefinite" % (offSet,CodeTagToDisplayR)
		else:
			sTagToPrint="%s %s length : %d" % (offSet,CodeTagToDisplayR,length)

		if flag == "true" :
			value = self.GetPrimitiveValue(filea,length)
			if len(convHash) > 0:	
				convHash[CodeTag].getDescrTag().strip()
				valueConverted = self.convValueFromHex(value,convHash[CodeTag].getConvType())
				self.txtTrad.insert(INSERT,"%s \"%s\"h Value(" % (sTagToPrint,value))
				if valueConverted.startswith("Error"):
					self.txtTrad.insert(INSERT,"%s" % valueConverted,"red")
				else:
					self.txtTrad.insert(INSERT,"%s" % valueConverted)
					
				self.txtTrad.insert(INSERT,")%s\n" % convHash[CodeTag].getConvType())	 
			else:	
				self.txtTrad.insert(INSERT,"%s \"%s\"h\n" % (sTagToPrint,value))
		else:
			self.txtTrad.insert(INSERT,"%s\n" % sTagToPrint)

		iLevel = iLevel + 1
		while ( ((length > 0) and ((filea.tell()) - startByte + 1) <= length) or ((length < 0) and self.CtrlInfinitiveEnd(filea) == 0) ):
			global stop_threads
			if stop_threads == True:
				break
			if offSetTo > 0 and filea.tell() > offSetTo:
				break
			if self.getTag(filea,iLevel,offSetTo):
				break
		iLevel = iLevel - 1

		return 0

# Function to manage change checkbox conv mode
	def convModeAction(self):
		if self.bConvMode.get() == False:
			self.convFile.config(state=NORMAL)
			self.convFile.delete(0, 'end')
			self.convFile.config(state=DISABLED)
			self.selConv.config(state=DISABLED)
			convHash.clear()
		else:
			self.selConv.config(state=NORMAL)

# Function to search
	def Search_Click(self):
		#remove tag 'found' from index 1 to END 
		global currentPos
		self.txtTrad.tag_remove('found', '1.0', END)  
		s = self.txtSearch.get()  
		if s: 
			idx = currentPos
			while 1: 
            #searches for desried string from index 1 
				idx = self.txtTrad.search(s, idx, nocase=1,stopindex=END)  
				if not idx:
					self.popup_msg("Not Found")
					currentPos = '1.0'
					break
              
            #last index sum of current index and 
            #length of text 
				lastidx = '%s+%dc' % (idx, len(s))  
            #overwrite 'Found' at idx 
				self.txtTrad.tag_add('found', idx, lastidx)  
				currentPos = lastidx 
				break

# Tk Interface Definicion
	def __init__(self, parent):
		self.parent= parent
#		self.content = Frame(self.parent, padding=(5,5,5,5))
		self.content = Frame(self.parent)

# Vertical (y) Scroll Bar
		self.scroll = Scrollbar(self.content)
		self.txtTrad = Text(self.content, relief="sunken", width=50, height=30, yscrollcommand=self.scroll.set)
		self.txtTrad.tag_config("red", background="white", foreground="red")
		self.txtTrad.tag_config("found", background="yellow", foreground="black")
#		self.scroll.config(command=self.txtTrad.yview)

# Convertion File 
		self.selConv = Button(self.content, text="Select Conv File", command=self.ReadConvButton_Click)
		self.selConv.config(state=DISABLED)
		self.convFile = Entry(self.content)
		self.convFile.config(state=DISABLED)

# Offset
		self.offsetFrom = Label(self.content, text="Offset From")
		self.offsetTo = Label(self.content, text="Offset To")
		self.offsetEntryF = Entry(self.content)
		self.offsetEntryT = Entry(self.content)

# Search

		self.txtSearch = Entry(self.content)
		self.buttSearch = Button(self.content, text="Search", command=self.Search_Click)

# Options

		self.bTypeTAP = BooleanVar()
		self.bHexRapr = BooleanVar()
		self.bConvMode = BooleanVar()

		self.bTypeTAP.set(False)
		self.bHexRapr.set(False)
		self.bConvMode.set(False)

		self.typeTAP = Checkbutton(self.content, text="TAP Notation", variable=self.bTypeTAP)
		self.hexRapr = Checkbutton(self.content, text="Tag Hex Value", variable=self.bHexRapr)
		self.convMode = Checkbutton(self.content, text="Convertion Tag", variable=self.bConvMode, command=self.convModeAction)

		self.select = Button(self.content, text="Select a File", command=self.ReadButton_Click)
		self.save = Button(self.content, text="Save on File", command=self.SaveButton_Click)
		self.save.config(state=DISABLED)
		self.cancel = Button(self.content, text="Clear All", command=self.ClearButton_Click)
		self.bQuit = Button(self.content, text="Quit",command=self.Quit)

		self.content.grid(column=0, row=0, sticky=(N, S, E, W))

		self.scroll.grid(column=6, row=3, rowspan=8, sticky=(N, S, E, W))
		self.txtTrad.grid(column=1, row=3, columnspan=5, rowspan=8, sticky=(N, S, E, W))

		self.scroll.config(command=self.txtTrad.yview)

# Dispose Conv File Managment
		self.selConv.grid(column=1,row=0,sticky=(N, E, W),padx=5,pady=5)
		self.convFile.grid(column=2,row=0,columnspan=4,sticky=(N, E, W),padx=5,pady=5)

# Offset Managment to develop
		self.offsetFrom.grid(column=1,row=1, sticky=(N, E, W), padx=5, pady=5)
		self.offsetEntryF.grid(column=2,row=1, sticky=(N, E, W), padx=5, pady=5)
		self.offsetTo.grid(column=3,row=1,sticky=(N, E, W), padx=5, pady=5) 
		self.offsetEntryT.grid(column=4,row=1,sticky=(N, E, W), padx=5, pady=5)
# Search 
		self.buttSearch.grid(column=1,row=2,sticky=(N, E, W), padx=5, pady=5)
		self.txtSearch.grid(column=2,row=2,columnspan=4,sticky=(N, E, W), padx=5, pady=5)
		

		self.select.grid(column=0,row=3, sticky=(N, E, W), padx=5, pady=5)
		self.save.grid(column=0,row=4, sticky=(N, E, W), padx=5, pady=5)
		self.cancel.grid(column=0,row=5, sticky=(N, E, W), padx=5, pady=5)

# Type TAP and Hex Rapr to develop		
		self.typeTAP.grid(column=0,row=6, sticky=(N, W), padx=5, pady=5)
		self.hexRapr.grid(column=0,row=7, sticky=(N, W), padx=5, pady=5)
		self.convMode.grid(column=0,row=8, sticky=(N, W), padx=5, pady=5)
		self.bQuit.grid(column=0,row=9, sticky=(S, E, W), padx=5, pady=5)

		parent.columnconfigure(0, weight=1)
		parent.rowconfigure(0, weight=1)
		self.content.columnconfigure(0, weight=1)
		self.content.columnconfigure(1, weight=1)
		self.content.columnconfigure(2, weight=1)
		self.content.columnconfigure(3, weight=1)
		self.content.columnconfigure(4, weight=1)
		self.content.columnconfigure(5, weight=1)
		self.content.rowconfigure(0, weight=0)
		self.content.rowconfigure(1, weight=0)
		self.content.rowconfigure(2, weight=0)
		self.content.rowconfigure(3, weight=0)
		self.content.rowconfigure(4, weight=0)
		self.content.rowconfigure(5, weight=0)
		self.content.rowconfigure(6, weight=0)
		self.content.rowconfigure(7, weight=0)
		self.content.rowconfigure(8, weight=1)

		self.parent.title(titleApp)

	def popup_msg(self, msg):
		win = Toplevel()
		win_x = self.getXCenter()
		win_y = self.getYCenter()
		win.geometry(f'+{win_x}+{win_y}')
		win.grab_set()
		win.resizable(height = False, width = False)
		win.wm_title("Error Msg")

		l = Label(win, text=msg)
		l.grid(row=1, column=1)
		b = Button(win, text="Okay", command=win.destroy)
		b.grid(row=2, column=1)

		win.rowconfigure(0, weight=1)
		win.rowconfigure(1, weight=1)
		win.rowconfigure(2, weight=1)
		win.rowconfigure(3, weight=1)
		win.columnconfigure(0,weight=1)
		win.columnconfigure(1,weight=1)
		win.columnconfigure(2,weight=1)

	def is_number(self, value):
		try:
			int(value)
			return True
		except:
			return False

# Function on Select Conv File
	def ReadConvButton_Click(self):
		flagErr = False
		filenameconv = filedialog.askopenfilename()
		if len(filenameconv) > 0:	
			if os.path.isfile(filenameconv):
				filerconv=open(filenameconv,"r")
				for line in filerconv:
					values = line.split("|")
					if len(values) != 3:
						self.popup_msg("Wrong line <" + line + "> not have 3 fields separated by '|'.")
						flagErr = True
						break	
					else:
						if values[1] != "A" and values[1] != "B" and values[1] != "N" and values[1] != "H":
							self.popup_msg("Wrong line <" + line + "> convertion type no correct admited only A, B, N or H.")
							flagErr = True
							break	
						if len(values[2]) == 0:	
							self.popup_msg("Wrong line <" + line + "> description is not present.")
							flagErr = True
							break	
						convHash[values[0]] = tagType(values[1],values[2])
				filerconv.close()	

# Set File Conversion file
				if flagErr == False:
					self.convFile.config(state=NORMAL)
					self.convFile.insert(0,os.path.basename(filenameconv))
					self.convFile.config(state=DISABLED)
					self.popup_msg("Loaded " + str(len(convHash)) + " Tag Informations.")

	def ReadButton_Click(self):
		if (len(self.offsetEntryF.get()) > 0 and self.is_number(self.offsetEntryF.get()) == False) or (len(self.offsetEntryT.get()) > 0 and self.is_number(self.offsetEntryT.get()) == False):
			self.popup_msg("OffSet From or OffSet To are not numerical.")
		else:
			if ( (len(self.offsetEntryF.get()) > 0) and (len(self.offsetEntryT.get()) > 0) and int(self.offsetEntryT.get()) <= int(self.offsetEntryF.get()) ):
				self.popup_msg("OffSet From is greater of equal to OffSet To.")
			else:
				if len(self.offsetEntryF.get()) > 0 :
					offSetFrom = int(self.offsetEntryF.get())
				else:
					offSetFrom = 0

				if len(self.offsetEntryT.get()) > 0 :
					offSetTo = int(self.offsetEntryT.get())
				else:
					offSetTo = 0

				self.currentPos = '1.0'
				self.txtSearch.delete(0,'end')

				filename = filedialog.askopenfilename()
				if len(filename) > 0:	
					if os.path.isfile(filename):
						self.limpia()
						fileasn1=open(filename,"rb")
						iLevel = 0
						if offSetFrom > 0:
							fileasn1.seek(offSetFrom)
						file_stats = os.stat(filename)	
						self.save.config(state=NORMAL)
						self.txtTrad.insert(INSERT,	"ASN1 FILE %s SIZE : %d\n\n" % (os.path.basename(filename),file_stats.st_size))
#						self.getTag(fileasn1,iLevel,offSetTo)
# Start Thread
						global stop_threads
						stop_threads = False
						t1 = threading.Thread(target=self.getTag, args=(fileasn1,iLevel,offSetTo, ), daemon=None)
						t1.start()
						t2 = threading.Thread(target=self.progress_file, args=(t1,fileasn1,file_stats.st_size, ))
						t2.start()
#						fileasn1.close()
					else:
						self.txtTrad.delete(1.0, END)
						self.txtTrad.insert(INSERT,"File " + filename + " No Exists.")
			
	def SaveButton_Click(self):
		filename = filedialog.asksaveasfilename()
		
		if len(filename) > 0:
			if os.path.isdir(filename):
				self.txtTrad.insert(INSERT," Error " + filename + " is a Directory.")
			else:
				fileasn1s=open(filename,"w")
				fileasn1s.write(self.txtTrad.get(1.0,END))
				fileasn1s.close()

	def ClearButton_Click(self):
		self.txtTrad.delete(1.0, END)
		self.bTypeTAP.set(False)
		self.bHexRapr.set(False)
		self.offsetEntryF.delete(0,'end')
		self.offsetEntryT.delete(0,'end')
		self.convFile.config(state=NORMAL)
		self.convFile.delete(0, 'end')
		convHash.clear(); # remove all entries in Hash Table
		self.selConv.config(state=DISABLED)
		self.save.config(state=DISABLED)
		self.convFile.config(state=DISABLED)
		self.bConvMode.set(False)
		self.currentPos = '1.0'
		self.txtSearch.delete(0,'end')

	def Quit(self):
		self.parent.destroy()
		root.destroy()

currentPos = '1.0'
titleApp = 'PyAsn1Tk 2.2'
fileicon = 'icon\pyAsn1Tk.ico'

if not hasattr(sys, "frozen"):
	fileicon = os.path.join(os.path.dirname(__file__), fileicon) 
else:  
	fileicon = os.path.join(sys.prefix, fileicon)

CodeTagToDisplay = ""
stop_threads = False
convHash = {}
root = Tk()
PyAsn1Tk = Application(root)

if os.path.isfile(fileicon):
	root.iconbitmap(default=fileicon)    

root.mainloop() 