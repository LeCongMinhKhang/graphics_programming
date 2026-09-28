import tkinter as tk
from tkinter import ttk
import multiprocessing
import queue
import datetime
# spawns a Tkinter window to display diagnostic data
class Tablerone(ttk.Frame):
  def __init__(self,parent,col = 1):
    super().__init__(parent)
    # column major
    self.dict = {}
    self.table = [[] for i in range(col)]

  def newRow(self,*args):
    nextRow = len(self.table[0])
    for i in range(len(args)):
      self.table[i].append(args[i])
      args[i].grid(row = nextRow,column = i, sticky = "se",padx=2,pady=2)
    return nextRow

  def label(self,/,id=None,**kwargs):
    lab = ttk.Label(self,**kwargs)
    if id is not None: 
      self.dict[id] = lab
    return lab
  
  def getById(self,id):
    return self.dict[id]
  
  def get(self,row,col):
    return self.table[col][row]

class Tonkapi:
  def __init__(self):
    self.shared_queue = multiprocessing.Queue()
    multiprocessing.Process(
      target=App, 
      args=(self.shared_queue,)
    ).start()
  
  def fps(self,val):
    self.shared_queue.put(val)
  def kill(self):
    self.shared_queue.put(None)

class App(tk.Tk):
  def __init__(self,queue):
    super().__init__()
    self.protocol("WM_DELETE_WINDOW", lambda: queue.put(None))
    self.live = True
    self.queue = queue
    self.records = []
    self.low = 999999
    self.lowRecords = []
    self.lowCount = 0

    self.title("Cheating")
    self.geometry("500x250") 
    self.minsize(500,250) 
    
    self.exportButton = ttk.Button(self,text="Export to csv",command=lambda: self.export(self.table))
    self.table = Tablerone(self,col = 2)
    self.table.grid(row=0,column=0,sticky="nsew")
    self.table.newRow(
      self.table.label(text="Average FPS:"),
      self.table.label(text="nothing yet", id="fps")
    )
    row = self.table.newRow(
      self.table.label(text="Lowest 1%:"),
      self.table.label(text="nothing yet", id="low")
    )
    self.exportButton.grid(row=row+1,column=0)
    # self.fpsLabel = ttk.Label(text= "FPS:")
    # self.fpsNumber = ttk.Label(text = "nothing yet")
    # self.lowLabel = ttk.Label(text= "1% low:")
    # self.lowNumber = ttk.Label(text = "nothing yet")
    # self.fpsLabel.pack()
    # self.fpsNumber.pack()
    # self.lowLabel.pack()
    # self.lowNumber.pack()
    self.check_queue()
    self.mainloop()

  def export(self,table):
    with open(f"./{datetime.datetime.now(datetime.UTC).strftime("%d-%m-%y_%H-%M-%S")}.csv","w",encoding="utf8") as file:
      file.writelines("\n".join([",".join([table.get(r,c)["text"] for c in range(len(table.table))]) for r in range(len(table.table[0]))]))
  
  def check_queue(self):
    try:
      while True:
        val = self.queue.get_nowait()
        if val is None: return self.destroy()

        self.lowCount = (self.lowCount+1)%100
        self.low = min(self.low,val)
        if self.lowCount == 0:
          self.table.getById("low").config(text=str(int(self.low)))
          # self.lowRecords.append(self.low)
          self.low = val
        self.records.append(val)
    except queue.Empty:
      if len(self.records) >= 100:
        avg = self.records[0]
        for data in self.records[1:]:
          avg += data
        avg /= len(self.records)
        self.table.getById("fps").config(text=str(int(avg)))
        self.records = []
        self.after(100, self.check_queue)
      else:
        self.after(100, self.check_queue)

  


# def window(root,ma):
#   num = ttk.IntVar(value=0)
#   label = ttk.Label(root, textvariable=num, font=("Arial", 16))
#   button = ttk.Button(root, text = "balls", command = lambda: ma.action("changeTab",[thedata]))
#   label.pack(pady=20)
#   button.pack(pady=20)
