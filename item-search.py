import PyPDF2
import docx
import re
from tkinter import filedialog
from PyQt5.QtCore import QSize, Qt, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton
import sys

# allows the user to choose a file
def UploadFile(event=None):
    filename = filedialog.askopenfilename()
    # try for pdf
    try:
        reader = PyPDF2.PdfReader(filename)
        pages = len(reader.pages)
        pdfText = ""
        for i in range(pages):
            pdfText += reader.pages[i].extract_text()
        pdfText = pdfText.replace(" ", "")
    except:
        # try for docx NOT WORKING CURRENTLY
        try:
            doc = docx.Document(filename)
            fullText = []
            for para in doc.paragraphs:
                fullText.append(para.text)
            docText = '\n'.join(fullText)
            docText = docText.replace(" ", "")
        except:
            print('invalid file')
        else:
            print(docText)
            print('-----------------')
            FindItems(docText)
    else:
        print(pdfText)
        print('-----------------')
        FindItems(pdfText)

# find all instances of an item in the document provided
def FindItems(text):
    try:
        items = re.findall('[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9]', text)
        listofitems = list(dict.fromkeys(items))
    except:
        print('can not find valid item #\'s')
    else:
        print(listofitems)

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = ('Item Search')
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setMinimumSize(QSize(400,300))

        browseButton = QPushButton('Browse', self)
        browseButton.setToolTip('Choose a file')
        browseButton.clicked.connect(self.on_click)

        self.show()

    @pyqtSlot()
    def on_click(self):
        UploadFile()

if __name__ == '__main__':
    # application instance
    app = QApplication(sys.argv)

    ex = App()
    sys.exit(app.exec_())