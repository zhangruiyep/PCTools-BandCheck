import os
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.font
import tkinter.ttk as ttk
import types
import serial.tools.list_ports
import threading
import time

from mcuDevice import *
from enum import Enum

class devState(Enum):
	IDLE = 1
	CONNECT = 2
	TEST = 3

class Application(ttk.Frame):
	def __init__(self, master=None):
		ttk.Frame.__init__(self, master)
		self.devCount = 1
		self.columnconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)
		self.grid(sticky=tk.NSEW)
		self.devList = []
		self.createWidgets()
		self.dev = None
		self.stopAll = False

		self.defaultFont = tkinter.font.nametofont("TkDefaultFont")
		self.defaultFont.configure(family="微软雅黑",     size=16)


	def initSerialFrame(self,frame):
		frame.dev = None
		frame.state = devState.IDLE
		frame.passCount = 0

		frame.InfoLable = ttk.Label(frame, text="端口号:", justify=tk.LEFT)
		frame.InfoLable.grid(row=0, sticky=tk.W, padx=10)

		frame.optionList = ["", ]
		for port in serial.tools.list_ports.comports():
			#print(port.description)
			frame.optionList.append(port.description)
		
		frame.v = tk.StringVar()
		#if len(frame.optionList) > 1:
		#	frame.v.set(frame.optionList[0])
		for op in frame.optionList:
			if op.find("ASR Modem Device") >= 0 and op.find("ASR Modem Device 2") < 0:
				frame.v.set(op)

		frame.platformOpt = ttk.OptionMenu(frame, frame.v, *frame.optionList)
		frame.platformOpt.grid(row = 0, column=1, sticky=tk.W, padx=10)

		frame.conState = ttk.Label(frame, text="未连接", justify=tk.LEFT, background='gray', foreground='white')
		frame.conState.grid(row = 0, column=2, sticky=tk.W, padx=10)

		frame.testState = ttk.Label(frame, text="未测试", justify=tk.LEFT, background='gray', foreground='white')
		frame.testState.grid(row = 0, column=3, sticky=tk.W, padx=10)

		#frame.thread = threading.Thread(target=self.testThread, name="Thread-AT", args=(), daemon=True)
		#frame.thread.start()

	def createWidgets(self):
		help_frame = ttk.Frame(self)
		help_frame.grid(row = 0, sticky=tk.NSEW, pady = 3)
		help_frame.InfoLable = ttk.Label(help_frame, text="使用说明：\n1、将设备连接到电脑。\n2、点击“刷新”，工具自动识别端口号。\n3、点击“开始”。\n4、设备对应的状态显示“通过”或“失败”后，拔掉设备。\n重复以上1~4步", justify=tk.LEFT)
		help_frame.InfoLable.grid(row=0, sticky=tk.W, padx=10)

		for i in range(1,self.devCount+1):
			serial_frame = ttk.Frame(self)
			serial_frame.grid(row = i, sticky=tk.NSEW, pady = 3)

			self.initSerialFrame(serial_frame)
			self.devList.append(serial_frame)

		#print(self.devList)

		actionFrame = ttk.Frame(self)
		actionFrame.grid(row = self.devCount+1, sticky=tk.NSEW, pady=3)

		self.startBtn = ttk.Button(actionFrame, text="开始", command=self.startTest)
		self.startBtn.grid(padx=10, row = 0, column = 0)
		self.refreshBtn = ttk.Button(actionFrame, text="刷新", command=self.refresh)
		self.refreshBtn.grid(padx=10, row = 0, column = 1)

	def testThread(self, idx):
		frame = self.devList[idx]
		while True:
			if (self.stopAll):
				break

			option = frame.v.get()
			#print(option)

			comNum = None
			for port in serial.tools.list_ports.comports():
				if (port.description == option):
					comNum = port.device
					break

			if (comNum == None):
				#print("no device")
				frame.conState["text"] = "未连接"
				frame.conState["background"] = "gray"
				if (frame.state == devState.TEST):
					frame.testState["text"] = "失败"
					frame.testState["background"] = "red"
					frame.passCount = 0
					if (frame.dev):
						frame.dev.close()
					frame.dev = None
					frame.state = devState.IDLE
					break
				continue

			print(comNum)

			if (frame.dev == None):
				frame.dev = mcuDevice(comNum, 10)
				ret = frame.dev.open()
				if (ret.result != "OK"):
					#tkinter.messagebox.showerror(ret.result, ret.msg)
					print("open %s fail" % comNum)
					frame.conState["text"] = "未连接"
					frame.conState["background"] = "gray"
					frame.dev = None
					time.sleep(1)
					continue
				else:
					frame.state = devState.CONNECT

			if (frame.state == devState.CONNECT):
				ret = frame.dev.runCmd(b'AT*BAND=0\r\n')
				if (ret.result == "OK"):
					frame.state = devState.TEST
					frame.conState["text"] = "已连接"
					frame.conState["background"] = "green"
					frame.testState["text"] = "测试中"
					frame.testState["background"] = "gray"
				else:
					frame.dev.close()
					frame.dev = None
					frame.state = devState.IDLE

			elif (frame.state == devState.TEST):
				ret = frame.dev.runCmd(b'AT*BAND?\r\n')
				if (ret.result == "OK"):
					frame.passCount += 1
					if (frame.passCount > 15):
						frame.testState["text"] = "通过"
						frame.testState["background"] = "green"
						ret = frame.dev.runCmd(b'AT*BAND=8\r\n')
						if (ret.result != "OK"):
							tkinter.messagebox.showerror("ERROR", "%s 恢复BAND失败，请检查设备设置是否正确！")
						frame.passCount = 0
						frame.dev.close()
						frame.dev = None
						break
				else:
					if (frame.passCount <= 15):
						frame.testState["text"] = "失败"
						frame.testState["background"] = "red"
						frame.passCount = 0
						frame.dev.close()
						frame.dev = None
						break

			time.sleep(1)

	def startTest(self):
		self.stopAll = False
		if (self.findDupDevs()):
			tkinter.messagebox.showerror("ERROR", "设备端口重复，请检查！")
			return

		for frame in self.devList:
			idx = self.devList.index(frame)
			frame.thread = threading.Thread(target=self.testThread, name="Thread-AT", args=(idx,), daemon=True)
			frame.thread.start()

	def refresh(self):
		self.stopAll = True
		self.devList.clear()
		for i in range(1,self.devCount+1):
			serial_frame = ttk.Frame(self)
			serial_frame.grid(row = i, sticky=tk.NSEW, pady = 3)

			self.initSerialFrame(serial_frame)
			self.devList.append(serial_frame)

	def findDupDevs(self):
		for frame_a in self.devList:
			for frame_b in self.devList:
				if (frame_a == frame_b):
					continue
				if (len(frame_a.v.get()) < 1) or (len(frame_b.v.get()) < 1):
					continue
				if (frame_a.v.get() == frame_b.v.get()):
					print("COM ERROR:",frame_a.v.get())
					return True
		return False

app = Application()
app.master.title('BAND检测工具 V1.6')
app.master.rowconfigure(0, weight=1)
app.master.columnconfigure(0, weight=1)
app.mainloop()
