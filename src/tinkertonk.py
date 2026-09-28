import tkinter as tk
from tkinter import ttk
import multiprocessing
import queue

# spawns a Tkinter window to display diagnostic data
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
    self.live = True
    self.queue = queue
    self.records = []
    self.low = 999999
    self.lowRecords = []
    self.lowCount = 0
    self.title("Cheating")
    self.geometry("500x250") 
    self.minsize(500,250) 
    self.fpsLabel = ttk.Label(text= "FPS:")
    self.fpsNumber = ttk.Label(text = "nothing yet")
    self.lowLabel = ttk.Label(text= "1% low:")
    self.lowNumber = ttk.Label(text = "nothing yet")
    self.fpsLabel.pack()
    self.fpsNumber.pack()
    self.lowLabel.pack()
    self.lowNumber.pack()
    self.check_queue()
    self.mainloop()

  def check_queue(self):
    try:
      while True:
        val = self.queue.get_nowait()
        if val is None: return self.destroy()

        self.lowCount = (self.lowCount+1)%100
        self.low = min(self.low,val)
        if self.lowCount == 0:
          self.lowNumber.config(text=str(int(self.low)))
          # self.lowRecords.append(self.low)
          self.low = val
        self.records.append(val)
    except queue.Empty:
      # if len(self.lowRecords) != 0:
      #   avg = self.lowRecords[0]
      #   for data in self.lowRecords[1:]:
      #     avg += data
      #   avg /= len(self.lowRecords)
      #   self.lowNumber.config(text=str(int(avg)))
      #   self.lowRecords = []
      if len(self.records) >= 100:
        avg = self.records[0]
        for data in self.records[1:]:
          avg += data
        avg /= len(self.records)
        self.fpsNumber.config(text=str(int(avg)))
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
