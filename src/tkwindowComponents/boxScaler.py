import tkinter as tk
from tkinter import ttk
from .stylingHelper import StyleEnum as Ste
from typing import Literal

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