import sys
import fitz
import re
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QListWidget, QRadioButton, QMessageBox, QDialog
from PyQt5.QtGui import QPixmap, QIcon
from collections import OrderedDict

class PDFReader(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Galvanize Item Search')
        # Get absolute path of the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct absolute file path to the image file
        image_path = os.path.join(script_dir, 'resources', 'galvanize_logo.png')
        self.setWindowIcon(QIcon(image_path))

        # Create widgets
        self.browse_button = QPushButton('Browse', self)
        self.browse_button.clicked.connect(self.browse_pdf)
        self.label = QLabel('No PDF file selected', self)
        self.list_widget = QListWidget(self)
        self.page_number_label = QLabel('Show page numbers:', self)
        self.show_page_numbers_radio = QRadioButton('Yes', self)
        self.show_page_numbers_radio.setChecked(True)
        self.show_page_numbers_radio.toggled.connect(self.toggle_page_numbers)
        self.supported_numbers_button = QPushButton('Show Supported Item Numbers', self)
        self.supported_numbers_button.clicked.connect(self.supported_numbers_window)
        self.download_button = QPushButton('Download', self)
        self.download_button.clicked.connect(self.download_matches)
        self.download_button.setEnabled(False)

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.browse_button)
        layout.addWidget(self.label)
        layout.addWidget(self.page_number_label)
        layout.addWidget(self.show_page_numbers_radio)
        layout.addWidget(self.supported_numbers_button)
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

        # List of regex patterns for various number formats
        patterns = [
            r'\d{3}-\d{5}-\d{3}',
            r'\d{3}-\d{5}-\d{2}(?!\d)',
            r'\d{3}-\d{5}(?!-)',
            r'(?<!(\d|-))\d{2}-\d{5}',
            r'ECO-\d{2}-\d{5}',
            r'ACM-\d{5}-\d{2}',
            r'ACM-\d{5}(?!-)',
            r'CER-\d{5}-\d{2}',
            r'CER-\d{5}(?!-)',
            r'CEP-\d{5}-\d{2}',
            r'CEP-\d{5}(?!-)',
            r'CSP-\d{5}-\d{2}',
            r'CSP-\d{5}(?!-)',
            r'CSR-\d{5}-\d{2}',
            r'CSR-\d{5}(?!-)',
            r'CLN-\d{5}-\d{2}',
            r'CLN-\d{5}(?!-)',
            r'DDP-\d{5}',
            r'(?<!\w)DP-\d{4}',
            r'DCD-\d{5}-\d{2}',
            r'DCD-\d{5}(?!-)',
            r'DHF-\d{5}-[A-Z0-9]{2}',
            r'DHF-\d{5}(?!-)',
            r'DMR-\d{5}-[A-Z0-9]{2}',
            r'DMR-\d{5}(?!-)',
            r'DOT-\d{5}-\d{2}',
            r'DOT-\d{5}(?!-)',
            r'EDR-\d{5}(?!-)',
            r'FRM-\d{5}(?!-)',
            r'LRP-\d{5}(?!-)',
            r'LRR-\d{5}(?!-)',
            r'LHR-\d{5}(?!-)',
            r'LHR-\d{5}-\d{2}',
            r'LHR-\d{5}-\d{3}',
            r'MPI-\d{5}(?!-)',
            r'MKG-\d{5}(?!-)',
            r'MKG-\d{5}-\d{2}',
            r'MA-\d{5}(?!-)',
            r'PCP-\d{5}-\d{2}',
            r'PCR-\d{5}(?!-)',
            r'PMSP-\d{5}(?!-)',
            r'PMSR-\d{5}(?!-)',
            r'PSUR-\d{5}(?!-)',
            r'QPL-\d{5}(?!-)',
            r'RAD-\d{5}(?!-)',
            r'RSK-\d{5}(?!-)',
            r'SLS-\d{5}(?!-)',
            r'SWP-\d{5}(?!-)',
            r'SOP-\d{5}(?!-)',
            r'STM-\d{5}(?!-)',
            r'TFN-\d{5}(?!-)',
            r'TFN-\d{5}-\d{2}',
            r'TP-\d{5}(?!-)',
            r'TP-\d{5}-\d{2}',
            r'TR-\d{5}(?!-)',
            r'TR-\d{5}-\d{2}',
            r'WRK-\d{5}(?!-)',
            r'FAB-\d{5}-\d{3}-\d{3}',
            r'BRD-\d{5}-\d{3}-\d{3}',
            r'GTI-\d{5}-\d{2}',
            r'EQP-\d{5}',
            r'PRT-\d{5}-\d{3}-\d{3}',
            r'PRT-\d{5}-\d{3}',
            r'LBL-\d{5}-\d{3}',
            r'OTS-\d{5}-\d{3}',
            r'SCH-\d{5}-\d{3}-\d{3}',
            r'SW-\d{5}-\d{3}-\d{3}',
            r'TFX-\d{5}-\d{3}-\d{3}'
        ]

        matches = []
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            page_text = page.get_text().replace(" ", "").replace("\n", "")
            print(page_text)
            for pattern in patterns:
                page_matches = re.findall(pattern, page_text)
                if page_matches:
                    matches.extend([(match, pattern, page_num + 1) for match in page_matches])

        if matches:
            if self.show_page_numbers_radio.isChecked():
                for match, pattern, page_num in matches:
                    item = f'Page: {page_num} | {match}'
                    self.list_widget.addItem(item)
            else:
                #unique_matches = list(OrderedDict.fromkeys([match for match, _, _ in matches]))
                unique_matches = sorted(list(set([match for match, _, _ in matches])))
                for match in unique_matches:
                    self.list_widget.addItem(f'{match}')
            self.download_button.setEnabled(True)
        else:
            self.list_widget.addItem('Nothing found')
            self.download_button.setEnabled(False)

    def supported_numbers_window(self):
        # Create a new window
        window = QDialog(self)
        window.setWindowTitle('Supported Item Numbers')
        self.supported_list_widget = QListWidget(self)

        # List all supported item numbers - refer to regex in extract_numbers()
        # supported_item_numbers = [
        #     'ACM-XXXXX-XX',
        #     'ACM-XXXXX',
        #     'CER-XXXXX-XX',
        #     'CER-XXXXX',
        #     'CEP-XXXXX-XX',
        #     'CEP-XXXXX',
        #     'CSP-XXXXX-XX',
        #     'CSP-XXXXX',
        #     'CSR-XXXXX-XX',
        #     'CSR-XXXXX',
        #     'CLN-XXXXX-XX',
        #     'CLN-XXXXX',
        #     'DDP-XXXXX',
        #     'DCD-XXXXX-XX',
        #     'DCD-XXXXX',
        #     'DMR-XXXXX-XX',
        #     'DMR-XXXXX',
        #     'DHF-XXXXX-XX',
        #     'DHF-XXXXX',
        #     'ECO-XX-XXXXX',
        #     'FAB-XXXXX-XXX-XXX',
        #     'BRD-XXXXX-XXX-XXX',
        #     'GTI-XXXXX-XX',
        #     'EQP-XXXXX',
        #     'PRT-XXXXX-XXX-XXX',
        #     'PRT-XXXXX-XXX',
        #     'LBL-XXXXX-XXX',
        #     'OTS-XXXXX-XXX',
        #     'SCH-XXXXX-XXX-XXX',
        #     'SW-XXXXX-XXX-XXX',
        #     'TFX-XXXXX-XXX-XXX',
        #     'XXX-XXXXX-XXX',
        #     'XXX-XXXXX-XX',
        #     'XXX-XXXXX',
        #     'XX-XXXXX',
        # ]
        supported_item_numbers = [
            'ACM',
            'BRD',
            'CER',
            'CEP',
            'CSP',
            'CSR',
            'CLN',
            'DP',
            'DDP',
            'DCD',
            'DHF',
            'DMR',
            'DOT',
            'EDR',
            'EQP',
            'FAB',
            'FRM',
            'GTI',
            'LBL',
            'LRP',
            'LRR',
            'LHR',
            'MPI',
            'MKG',
            'MA',
            'OTS',
            'PCP',
            'PCR',
            'PMSP',
            'PMSR',
            'PRT',
            'PSUR',
            'QPL',
            'RAD',
            'RSK',
            'SCH',
            'SLS',
            'SW',
            'SWP',
            'SOP',
            'STM',
            'TFN',
            'TFX',
            'TP',
            'TR',
            'WRK',
        ]
        for item in supported_item_numbers:
            item = f'{item}'
            self.supported_list_widget.addItem(item)

        label = QLabel('The following item number prefixes are supported: ', window)
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.supported_list_widget)

        window.setLayout(layout)

        window.exec_()

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
    # Get absolute path of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct absolute file path to the image file
    image_path = os.path.join(script_dir, 'resources', 'galvanize_logo.png')
    app.setWindowIcon(QIcon(image_path))
    window = PDFReader()
    window.show()
    sys.exit(app.exec_())
