import PyPDF2
import docx
import re
from tkinter import filedialog
from PyQt5 import QtGui
from PyQt5.QtCore import QSize, Qt, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QDesktopWidget, QLabel
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
        self.left = 10
        self.top = 10
        self.width = 400
        self.height = 300
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(400, 400)

        titleLabel = QLabel(self)
        titleLabel.setText("Galvanize Item Search")
        titleLabel.setFont(QtGui.QFont('Arial', 15))
        titleLabel.adjustSize()
        titleLabel.move(100, 50)

        logoLabel = QLabel(self)
        pixmap = QPixmap('resources/galvanize-therapeutics-squarelogo-1666689080199.png')
        logoLabel.setPixmap(pixmap)
        logoLabel.move(100, 100)
        logoLabel.resize(pixmap.width(), pixmap.height())

        browseLabel = QLabel(self)
        browseLabel.setText("Choose a file: ")
        browseLabel.move(100, 320)

        browseButton = QPushButton('Browse', self)
        browseButton.setToolTip('Choose a file')
        browseButton.move(200, 320)
        browseButton.clicked.connect(self.on_click)

        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    @pyqtSlot()
    def on_click(self):
        UploadFile()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())