import PyPDF2
import docx
import re
from tkinter import filedialog
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys

listofitems = []

# find all instances of an item in the document provided
def FindItems(text):
    try:
        items = re.findall('[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9]', text)
        listofitems = list(dict.fromkeys(items))
    except:
        print('can not find valid item #\'s')
    else:
        print(listofitems)
        return(listofitems)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = ('Welcome!')
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
        browseButton.clicked.connect(self.uploadFile)

        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    @pyqtSlot()
    def uploadFile(self):
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
            self.win = ListWindow()

class ListWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.title = ('Item List')
        self.left = 10
        self.top = 10
        self.width = 400
        self.height = 300
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        vbox = QVBoxLayout()
        itemIndex = 0
        self.itemList = QListWidget()
        print(listofitems)
        self.itemList.insertItem(0, "test")
        for item in listofitems:
            self.itemList.insertItem(item, listofitems[item])
            itemIndex+=1
            print(listofitems[item])
        vbox.addWidget(self.itemList)
        self.setLayout(vbox)
        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())