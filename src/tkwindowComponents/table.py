import tkinter as tk
from tkinter import ttk


class Tablerone(ttk.Frame):
  def __init__(self, parent=None, col=1):
    super().__init__(parent)
    # column major
    self.dict = {}
    self.table = [[] for i in range(col)]

  def newRow(self, *args):
    nextRow = len(self.table[0])
    for i in range(len(args)):
      self.table[i].append(args[i])
      if args[i] is not None:
        args[i].grid(row=nextRow, column=i, sticky="nsew", padx=2, pady=2)
    return nextRow

  def none(self):
    return None

  def label(self, /, id=None, **kwargs):
    lab = ttk.Label(self, **kwargs, background="")
    if id is not None:
      self.dict[id] = lab
    return lab

  def comboBox(self, /, id=None, default=None, command=None, **kwargs):
    combo = ttk.Combobox(self, **kwargs)
    if id is not None:
      self.dict[id] = combo
    if default is not None:
      combo.current(default)
    if command is not None:
      combo.bind("<<ComboboxSelected>>", command)
    return combo

  def spinBox(self, /, id=None, default=None, **kwargs):
    spinbox = ttk.Spinbox(self, **kwargs)
    if id is not None:
      self.dict[id] = spinbox
    if default is not None:
      spinbox.set(default)
    return spinbox

  def checkButton(self, /, id=None, **kwargs):
    button = ttk.Checkbutton(self, **kwargs)
    if id is not None:
      self.dict[id] = button
    return button

  def button(self, /, id=None, **kwargs):
    button = ttk.Button(self, **kwargs)
    if id is not None:
      self.dict[id] = button
    return button

  def entry(self, /, id=None, **kwargs):
    ent = ttk.Entry(self, **kwargs, background="")
    if id is not None:
      self.dict[id] = ent
    return ent

  def get(self, id: str = None, row: int = None, col: int = None):
    if row is None or col is None:
      return self.dict[id]
    else:
      return self.table[col][row]
