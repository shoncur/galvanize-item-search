import PyPDF2
import textract
from tkinter import filedialog

# reader = PyPDF2.PdfReader('100-00040-013_B Software Design Specification.pdf')
# pages = len(reader.pages)
# for i in range(pages):
#     text = reader.pages[i].extract_text()
#     print(text)

# text = textract.process('01RegexTest.txt')
# print(text)

def UploadFile(event=None):
    filename = filedialog.askopenfilename()
    try:
        reader = PyPDF2.PdfReader(filename)
        pages = len(reader.pages)
        text = ""
        for i in range(pages):
            text += reader.pages[i].extract_text()
    except:
        try:
            text = textract.process(filename)
        except:
            print('invalid file')
        else:
            print(text)
    else:
        print(text)

UploadFile()