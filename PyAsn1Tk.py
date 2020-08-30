from tkinter import *
from tkinter import filedialog
import os.path
import os, sys

#
# Utilty to read BER Asn1 File in Python3 with GUI Tk
#

class Application(object):

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

	def getTag(self, filea, iLevel):
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

		CodeTag =  "%s-%s [%s] offset [%s]" % (id,tag,taghex,startByte)
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
			if self.getTag(filea,iLevel):
				break

		iLevel=iLevel-1
		return 0

# Tk Interface Definicion
	def __init__(self, parent):
		self.parent= parent
#		self.content = Frame(self.parent, padding=(5,5,5,5))
		self.content = Frame(self.parent)
		self.txtTrad = Text(self.content, relief="sunken", width=50, height=30)
		self.offsetFrom = Label(self.content, text="Offset From")
		self.offsetTo = Label(self.content, text="Offset To")
		self.offsetEntryF = Entry(self.content)
		self.offsetEntryT = Entry(self.content)

		self.bTypeTAP = BooleanVar()
		self.bHexRapr = BooleanVar()

		self.bTypeTAP.set(False)
		self.bHexRapr.set(False)

		self.typeTAP = Checkbutton(self.content, text="TAP Notation", variable=self.bTypeTAP, onvalue=False)
		self.hexRapr = Checkbutton(self.content, text="Tag Hex Value", variable=self.bHexRapr, onvalue=False)

		self.select = Button(self.content, text="Select a File", command=self.ReadButton_Click)
		self.save = Button(self.content, text="Save on File", command=self.SaveButton_Click)
		self.cancel = Button(self.content, text="Clear All", command=self.ClearButton_Click)
		self.bQuit = Button(self.content, text="Quit",command=self.Quit)

		self.content.grid(column=0, row=0, sticky=(N, S, E, W))

		self.txtTrad.grid(column=1, row=1, columnspan=5, rowspan=6, sticky=(N, S, E, W))

# Offset Managment to develop
#		self.offsetFrom.grid(column=2,row=0, padx=5, pady=5)
#		self.offsetEntryF.grid(column=3,row=0, padx=5, pady=5)
#		self.offsetTo.grid(column=4,row=0,padx=5, pady=5) 
#		self.offsetEntryT.grid(column=5,row=0,padx=5, pady=5, disable=)

		self.select.grid(column=0,row=1, sticky=(N, E, W), padx=5, pady=5)
		self.save.grid(column=0,row=2, sticky=(N, E, W), padx=5, pady=5)
		self.cancel.grid(column=0,row=3, sticky=(N, E, W), padx=5, pady=5)
# Type TAP and Hex Rapr to develop		
#		self.typeTAP.grid(column=0,row=4, sticky=(N, E, W), padx=5, pady=5)
#		self.hexRapr.grid(column=0,row=5, sticky=(N, E, W), padx=5, pady=5)
		self.bQuit.grid(column=0,row=6, sticky=(S, E, W), padx=5, pady=5)

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
		self.content.rowconfigure(5, weight=1)
		self.content.rowconfigure(6, weight=1)

		self.parent.title('PyAsn1Tk 1.0')

# Tk Interface Definicion		
#	def __init__(self, parent):
#		self.parent= parent
#
#		self.textFrame=Frame(self.parent)
#		
#		self.lyricsText = Text(self.textFrame,width=130,height=30)
#		self.lyricsText.pack({'side':'left'})
##		self.lyricsText.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
#
##		self.lyricsScrollbar=Scrollbar(self.textFrame)
#		self.lyricsScrollbar.pack({'side':'left', 'expand':'yes', 'fill':'y'})
#
#		self.textFrame.pack()
#
#		self.lyricsScrollbar['command']=self.lyricsText.yview
#		self.lyricsText['yscrollcommand']=self.lyricsScrollbar.set
#
#		self.ReadButton=Button(self.parent,text="Select a File",command=self.ReadButton_Click)
#		self.ReadButton.pack()
#
##		self.DeleteButton=Button(self.parent,text="Save on File",command=self.SaveButton_Click)
#		self.DeleteButton.pack()
#
#		self.DeleteButton=Button(self.parent,text="Clear All",command=self.ClearButton_Click)
#		self.DeleteButton.pack()
#
#		self.OutputLabel = Label(self.parent, text="")
#		self.OutputLabel.pack()
#
##        self.imq=PhotoImage(file='exit.gif')
#        self.imq=Button('exit');
    
#		self.QuitButton=Button(self.parent,text="Quit",command=self.Quit)
#		self.QuitButton.pack()

#		self.parent.title('PyAsn1Tk 1.0')

	def ReadButton_Click(self):
		filename = filedialog.askopenfilename()
		
		if os.path.isfile(filename):
			self.limpia()
			fileasn1=open(filename,"rb")
			iLevel = 0
			self.getTag(fileasn1,iLevel)
			fileasn1.close()
		else:
			self.txtTrad.delete(1.0, END)
			self.txtTrad.insert(INSERT,"File " + filename + " No Exists.")
			
	def SaveButton_Click(self):
		filename = filedialog.asksaveasfilename()
		
		if os.path.isdir(filename):
		    self.txtTrad.insert(INSERT," Error " + filename + " is a Directory.")
		else:
			fileasn1s=open(filename,"w")
			fileasn1s.write(self.txtTrad.get(1.0,END))
			fileasn1s.close()
	def ClearButton_Click(self):
		self.txtTrad.delete(1.0, END)
	def Quit(self):
		self.parent.destroy()

root = Tk()
PyAsn1Tk = Application(root)
    
root.mainloop() 