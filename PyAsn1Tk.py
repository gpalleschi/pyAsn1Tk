from tkinter import *
from tkinter import filedialog
from tkinter import ttk
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

class tagType:
	def __init__(self, convType, descrTag):
		self.convType = convType
		self.descrTag = descrTag
	def getConvType(self):
		return self.convType	
	def getDescrTag(self):
		return self.descrTag	

class Application(object):
	
	def stopThread(self, t1):
		global stop_threads
		stop_threads = True

	def progress_file(self, t1, fileasn1, filedim):
		win = Toplevel(root)
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
#			print("join t1 %s con timeout 1 Thread %d tell fileasn1 %d" % (t1.isAlive(), threading.active_count(),fileasn1.tell()))
#		print("close fileasn1 %d - %s Threads %d" % (fileasn1.tell(),t1.isAlive(),threading.active_count()))
		progress['value'] = fileasn1.tell()*100/filedim
		fileasn1.close()
#		print("exit progress_file")
		win.destroy()

	def limpia(self):
		self.txtTrad.delete(1.0, END)

	def CtrlInfinitiveEnd(self, filea):
		curpos=filea.tell()
		for i in range(2):
			if self.readAsn1(filea) != "00":
				break
		if i == 2:
			return 1
		filea.seek(curpos)
		return 0

	def GetPrimitiveValue(self,filea, lenValue):
		sretvalue=""
		ind=0
		while (lenValue > 0 and (ind < lenValue)) or (lenValue < 0 and self.CtrlInfinitiveEnd(filea) == 0): 
			sretvalue="%s%s" % (sretvalue,self.readAsn1(filea))
			ind = ind + 1
		return sretvalue    

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

# Tag rappresentation

		if self.bTypeTAP.get() == False:
			CodeTag =  "%s-%s" % (id,tag)
		else:
			CodeTag =  "%s" % (tag)

# Tag Name
		if len(convHash) > 0:				
			if CodeTag in convHash:
				CodeTag = CodeTag + " {" + convHash[CodeTag].getDescrTag().strip() + "}"
# Hex Tag
		if self.bHexRapr.get() == True:
			CodeTag = CodeTag +  " [%s] " % (taghex)

# OffSet
		CodeTag = CodeTag + " offset [%s]" % (startByte)

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
		sIndent=""        
		for i in range(iLevel):
			sIndent="\t%s" % sIndent


		sTagToPrint=""
		if length < 0:
			sTagToPrint="%s%s length : indefinite" % (sIndent,CodeTag)
		else:
			sTagToPrint="%s%s length : %d" % (sIndent,CodeTag,length)

		if flag == "true" :
			value = self.GetPrimitiveValue(filea,length)
			self.txtTrad.insert(INSERT,"%s Hex Value <%s>\n" % (sTagToPrint,value))
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

		iLevel=iLevel-1

		return 0

	def convModeAction(self):
		if self.bConvMode.get() == False:
			self.selConv.config(state=DISABLED)
			self.convFile.config(state=DISABLED)
			convHash.clear()
			self.convFile.delete(0, 'end')
		else:
			self.selConv.config(state=NORMAL)

# Tk Interface Definicion
	def __init__(self, parent):
		self.parent= parent
#		self.content = Frame(self.parent, padding=(5,5,5,5))
		self.content = Frame(self.parent)

# Vertical (y) Scroll Bar
		self.scroll = Scrollbar(self.content)
		self.txtTrad = Text(self.content, relief="sunken", width=50, height=30, yscrollcommand=self.scroll.set)
#		self.scroll.config(command=self.txtTrad.yview)

# Convertion File 
		self.selConv = Button(self.content, text="Select Conv File", command=self.ReadConvButton_Click)
		self.selConv.config(state=DISABLED)
		self.convFile = Entry(self.content)
		self.convFile.config(state=DISABLED)

		self.offsetFrom = Label(self.content, text="Offset From")
		self.offsetTo = Label(self.content, text="Offset To")
		self.offsetEntryF = Entry(self.content)
		self.offsetEntryT = Entry(self.content)

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
		self.cancel = Button(self.content, text="Clear All", command=self.ClearButton_Click)
		self.bQuit = Button(self.content, text="Quit",command=self.Quit)

		self.content.grid(column=0, row=0, sticky=(N, S, E, W))

		self.scroll.grid(column=6, row=2, rowspan=8, sticky=(N, S, E, W))
		self.txtTrad.grid(column=1, row=2, columnspan=5, rowspan=8, sticky=(N, S, E, W))

		self.scroll.config(command=self.txtTrad.yview)

# Dispose Conv File Managment
		self.selConv.grid(column=2,row=0,sticky=(N, E, W),padx=5,pady=5)
		self.convFile.grid(column=3,row=0,columnspan=3,sticky=(N, E, W),padx=5,pady=5)

# Offset Managment to develop
		self.offsetFrom.grid(column=2,row=1, padx=5, pady=5)
		self.offsetEntryF.grid(column=3,row=1, padx=5, pady=5)
		self.offsetTo.grid(column=4,row=1,padx=5, pady=5) 
		self.offsetEntryT.grid(column=5,row=1,padx=5, pady=5)

		self.select.grid(column=0,row=2, sticky=(N, E, W), padx=5, pady=5)
		self.save.grid(column=0,row=3, sticky=(N, E, W), padx=5, pady=5)
		self.cancel.grid(column=0,row=4, sticky=(N, E, W), padx=5, pady=5)
# Type TAP and Hex Rapr to develop		
		self.typeTAP.grid(column=0,row=5, sticky=(N, E, W), padx=5, pady=5)
		self.hexRapr.grid(column=0,row=6, sticky=(N, E, W), padx=5, pady=5)
		self.convMode.grid(column=0,row=7, sticky=(N, E, W), padx=5, pady=5)
		self.bQuit.grid(column=0,row=8, sticky=(S, E, W), padx=5, pady=5)

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
		self.content.rowconfigure(7, weight=1)
		self.content.rowconfigure(8, weight=1)

		self.parent.title(titleApp)

	def popup_msg(self, msg):
		win = Toplevel()
		win.wm_title("Error Msg")

		l = Label(win, text=msg)
		l.grid(row=0, column=0)

		b = Button(win, text="Okay", command=win.destroy)
		b.grid(row=1, column=0)

	def is_number(self, value):
		try:
			int(value)
			return True
		except:
			return False

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

				filename = filedialog.askopenfilename()
				if len(filename) > 0:	
					if os.path.isfile(filename):
						self.limpia()
						fileasn1=open(filename,"rb")
						iLevel = 0
						if offSetFrom > 0:
							fileasn1.seek(offSetFrom)
						file_stats = os.stat(filename)	
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
		self.convFile.config(state=NORMAL)
		self.convFile.delete(0, 'end')
		convHash.clear(); # remove all entries in Hash Table
		self.selConv.config(state=DISABLED)
		self.convFile.config(state=DISABLED)
		self.bConvMode.set(False)

	def Quit(self):
		self.parent.destroy()
		root.destroy()

titleApp = 'PyAsn1Tk 2.0'
fileicon = 'icon\pyAsn1Tk.ico'

if not hasattr(sys, "frozen"):
	fileicon = os.path.join(os.path.dirname(__file__), fileicon) 
else:  
	fileicon = os.path.join(sys.prefix, fileicon)

stop_threads = False
convHash = {}
root = Tk()
PyAsn1Tk = Application(root)

if os.path.isfile(fileicon):
	root.iconbitmap(default=fileicon)    

root.mainloop() 