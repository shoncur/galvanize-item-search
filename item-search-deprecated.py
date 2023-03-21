# Author: Shaun Currie
# Date: 2023-01-24

# Goal:
#   To create a simple application that takes in a document, and outputs a list of item numbers

from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import Text

import re

from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
import textract

# This is called when the user clicks the "browse" button
def UploadAction(event=None):
   filename = filedialog.askopenfilename()
   try:
      reader = PdfReader(filename)
      pages = len(reader.pages)
      for i in range(pages):
         text = reader.pages[i].extract_text()
   except:
      try:
         text = textract.process(filename)
      except:
         print('invalid file')
   else:
      print('Selected:', filename)    
      ttk.Label(mainframe, text=filename).grid(column=1, row=2, sticky=(E))
      FindItems(filename)

# Find all instances of an item in the document
def FindItems(filename):
   textfile = open(filename, 'r')
   filetext = textfile.read()
   textfile.close()
   matches = re.findall("[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9]", filetext)
   listofitems = list(dict.fromkeys(matches))
   ttk.Label(mainframe, text=listofitems).grid(column=1, row=3)

# Instantiate tkinter
root = Tk()
root.title("Item Number Search")

# Setting up the grid for adding elements to the application
mainframe = ttk.Frame(root, padding="12 12 12 12")
mainframe.grid(column=0, row=0, sticky=(N, E, W, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# "Choose a File: " label and "Browse" button
ttk.Label(mainframe, text="Choose a File: ").grid(column=1, row=1, sticky=(W))
ttk.Button(mainframe, text="Browse", command=UploadAction).grid(column=2, row=1, sticky=(W))

# Render the GUI
root.mainloop()
