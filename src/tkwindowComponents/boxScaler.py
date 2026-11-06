import tkinter as tk
from tkinter import ttk
from .stylingHelper import StyleEnum as Ste
from typing import Literal


# class BoxScaler(ttk.Frame):
#   def __init__(self, parent,
#                index,
#                scaleDirection : Literal["vertical","horizontal"] = "horizontal",
#               ):
#     super().__init__(parent,relief="ridge",cursor="fleur")
#     self.parent : ttk.Frame = parent
#     self.scaleDirection = scaleDirection
#     self.index = index
#     if scaleDirection == "vertical":
#       self.config(height = Ste.PADD.value,cursor="sb_v_double_arrow")
#     else:
#       self.config(width = Ste.PADD.value,cursor="sb_h_double_arrow")
#     self.x = None
#     self.y = None
#     self.bind("<B1-Motion>", self.holdDrag)
#     self.bind("<ButtonRelease-1>", self.unhold)

  
#   def holdDrag(self,event):
#     dx = 0 if self.x is None else (event.x - self.x)
#     dy = 0 if self.y is None else (event.y - self.y)
    
#     self.x = event.x
#     self.y = event.y

#     [sideA,sideB] = self.index
#     match self.scaleDirection:
#       case "vertical":
#         weightA = self.parent.grid_rowconfigure(sideA)["weight"]
#         weightB = self.parent.grid_rowconfigure(sideB)["weight"]
#         total = weightA + weightB
#         change = 0
#         if weightA < weightB:
#           change = weightA*max(min(dy*2/self.parent.winfo_height(),1),-1)
#         else:
#           change = weightB*max(min(dy*2/self.parent.winfo_height(),1),-1)
        
#         if dy > 0:
#           self.parent.grid_rowconfigure(index=(sideA,),weight = total - max(int(weightB - change),1))
#           self.parent.grid_rowconfigure(index=(sideB,),weight = max(int(weightB - change)))
#         elif dy < 0:
#           self.parent.grid_rowconfigure(index=(sideA,),weight = max(int(weightA - change),1))
#           self.parent.grid_rowconfigure(index=(sideB,),weight = total - max(int(weightA - change),1))
#       case _ :
#         weightA = self.parent.grid_columnconfigure(sideA)["weight"]
#         weightB = self.parent.grid_columnconfigure(sideB)["weight"]
#         total = weightA + weightB
#         change = 0
#         if weightA > weightB:
#           change = weightA*min(abs(dx)/self.parent.winfo_height(),1)
#         else:
#           change = weightB*min(abs(dx)/self.parent.winfo_height(),1)
        
#         if dx < 0:
#           self.parent.grid_columnconfigure(index=(sideA,),weight = max(0,int(weightA - change)))
#           self.parent.grid_columnconfigure(index=(sideB,),weight = total - max(0,int(weightA - change)))
#         elif dx > 0:
#           self.parent.grid_columnconfigure(index=(sideA,),weight = total - max(0,int(weightB - change)))
#           self.parent.grid_columnconfigure(index=(sideB,),weight = max(0,int(weightB - change))) # In-place updates.
#     self.update_idletasks()
    
#   def unhold(self,event):
#     self.x = None
#     self.y = None

class BoxScaler(ttk.Frame):
  def __init__(self, parent,
               elementA,
               elementB,
               scaleDirection : Literal["vertical","horizontal"] = "horizontal",
              ):
    """
    Custom element to provide rescaling ability to .grid() based tables.

    Args:
      parent (ttk.frame): The parent that contains this element, important that the column/row weights are configured to be large (1000:1000:2000 instead of 1:1:2) to provide more finetuned scaling.
      elementA (ttk.frame): An element that belongs to one side of the scaler. Use one that has sticky="nsew" or similar to get accurate size of the column/row.
      elementB (ttk.frame): An element that belongs to the other side of the scaler. Use one that has sticky="nsew" or similar to get accurate size of the column/row.
      scaleDirection (Literal["vertical","horizontal"]): The direction the scaler will scale in.
    """
    super().__init__(parent,relief="ridge",cursor="fleur")
    self.parent : ttk.Frame = parent
    self.isHold = False
    self.isHorizontal = scaleDirection == "horizontal"
    if self.isHorizontal:
      self.config(width = Ste.PADD.value,cursor="sb_h_double_arrow")
    else:
      self.config(height = Ste.PADD.value,cursor="sb_v_double_arrow")
    self.A = elementA
    self.B = elementB
    self.bind("<Button-1>",self.hold)
    self.bind("<ButtonRelease-1>", self.unhold)

  def dirred(self,a,b):
    return a if self.isHorizontal else b

  def hold(self,event):
    if self.isHold: return
    self.pos0 = self.dirred(event.x,event.y)
    self.isHold = True
  

  def unhold(self,event):
    if not self.isHold: return
    
    pxSizeA = self.dirred(self.A.winfo_width, self.A.winfo_height)()
    pxSizeB = self.dirred(self.B.winfo_width, self.B.winfo_height)()
    pxTotal = pxSizeA + pxSizeB
    sideA = self.A.grid_info()[self.dirred("column","row")]
    sideB = self.B.grid_info()[self.dirred("column","row")]
    weightA = self.dirred(self.parent.grid_columnconfigure,self.parent.grid_rowconfigure)(sideA)["weight"]
    weightB = self.dirred(self.parent.grid_columnconfigure,self.parent.grid_rowconfigure)(sideB)["weight"]
    weightTotal = weightA + weightB

    deltaPos = self.dirred(event.x - self.pos0,event.y - self.pos0)
    deltaWeight = min(max(-weightA,deltaPos*weightTotal//pxTotal),weightB)
    
    self.dirred(self.parent.grid_columnconfigure,self.parent.grid_rowconfigure)(index=(sideA,),weight=weightA + deltaWeight)
    self.dirred(self.parent.grid_columnconfigure,self.parent.grid_rowconfigure)(index=(sideB,),weight=weightB - deltaWeight)

    self.isHold = False