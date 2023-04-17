import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QListWidget, QRadioButton, QMessageBox
import fitz
import re
from collections import OrderedDict
from PyQt5.QtGui import QPixmap

class PDFReader(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('PDF Reader')

        # Create logo
        self.logo_label = QLabel(self)
        pixmap = QPixmap('galvanize_logo.png')
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setScaledContents(True)

        # Create widgets
        self.browse_button = QPushButton('Browse', self)
        self.browse_button.clicked.connect(self.browse_pdf)
        self.label = QLabel('No PDF file selected', self)
        self.list_widget = QListWidget(self)
        self.page_number_label = QLabel('Show page numbers:', self)
        self.show_page_numbers_radio = QRadioButton('Yes', self)
        self.show_page_numbers_radio.setChecked(True)
        self.show_page_numbers_radio.toggled.connect(self.toggle_page_numbers)
        self.download_button = QPushButton('Download', self)
        self.download_button.clicked.connect(self.download_matches)
        self.download_button.setEnabled(False)

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.logo_label)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.label)
        layout.addWidget(self.page_number_label)
        layout.addWidget(self.show_page_numbers_radio)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.download_button)

        self.setLayout(layout)

    def browse_pdf(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open PDF File', '', 'PDF Files (*.pdf)')
        if file_name:
            self.label.setText(f'Selected file: {file_name}')
            self.extract_numbers(file_name)
        else:
            self.label.setText('No PDF file selected')
            self.list_widget.clear()
            self.download_button.setEnabled(False)

    def extract_numbers(self, file_name):
        self.list_widget.clear()

        # Open PDF and extract text
        pdf_document = fitz.open(file_name)

        # Search for numbers/letters in XXX-XXXXX-XXX format and store the page number
        pattern = r'\b[A-Z0-9]{3}-[A-Z0-9]{5}-[A-Z0-9]{3}\b'
        matches = []
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            page_text = page.get_text().replace(" ", "")  # Remove spaces from extracted text
            page_matches = re.findall(pattern, page_text)
            if page_matches:
                matches.extend([(match, page_num + 1) for match in page_matches])  # Add page number to each match

        if matches:
            # Display matches based on selected mode
            if self.show_page_numbers_radio.isChecked():
                # Display all matches with page numbers
                for match, page_num in matches:
                    item = f'Match: {match} | Page: {page_num}'
                    self.list_widget.addItem(item)
            else:
                # Display unique matches without page numbers
                unique_matches = list(OrderedDict.fromkeys([match for match, _ in matches]))
                for match in unique_matches:
                    self.list_widget.addItem(f'Match: {match}')
            self.download_button.setEnabled(True)
        else:
            self.list_widget.addItem('Nothing found')
            self.download_button.setEnabled(False)

    def toggle_page_numbers(self):
        if self.label.text() != 'No PDF file selected':
            self.extract_numbers(self.label.text().split(': ')[1])  # Re-extract and display matches based on new mode
        else:
            QMessageBox.warning(self, 'Error', 'Please select a PDF file first.', QMessageBox.Ok)

    def download_matches(self):
        if self.list_widget.count() == 0:
            QMessageBox.warning(self, 'Error', 'No matches found to download.', QMessageBox.Ok)
            return

        file_name, _ = QFileDialog.getSaveFileName(self, 'Save Matches', '', 'Text Files (*.txt)')
        if file_name:
            with open(file_name, 'w') as file:
                if self.show_page_numbers_radio.isChecked():
                    # Write all matches with page numbers
                    for i in range(self.list_widget.count()):
                        item = self.list_widget.item(i).text()
                        file.write(f'{item}\n')
                else:
                    # Write unique matches without page numbers
                    unique_matches = list(OrderedDict.fromkeys([self.list_widget.item(i).text() for i in range(self.list_widget.count())]))
                    for item in unique_matches:
                        file.write(f'{item}\n')

            QMessageBox.information(self, 'Success', f'Matches have been downloaded to: {file_name}', QMessageBox.Ok)
        else:
            QMessageBox.warning(self, 'Error', 'File name not provided.', QMessageBox.Ok)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PDFReader()
    window.show()
    sys.exit(app.exec_())
