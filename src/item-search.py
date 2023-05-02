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
            r'\b[A-Z0-9]{3}-[A-Z0-9]{5}-[A-Z0-9]{3}\b',
            r'\b[A-Z0-9]{3}-[A-Z0-9]{5}-[A-Z0-9]{2}\b',
            r'\b[A-Z0-9]{3}-[A-Z0-9]{5}\b(?!-)',
            r'\b(?<!-)\d{2}-\d{5}\b',
            r'\bECO-\d{2}-\d{5}\b',
            r'\bACM-\d{5}-\d{2}\b',
            r'\bACM-\d{5}\b(?!-)',
            r'\bCER-\d{5}-\d{2}\b',
            r'\bCER-\d{5}\b(?!-)',
            r'\bCEP-\d{5}-\d{2}\b',
            r'\bCEP-\d{5}\b(?!-)',
            r'\bCSP-\d{5}-\d{2}\b',
            r'\bCSP-\d{5}\b(?!-)',
            r'\bCSR-\d{5}-\d{2}\b',
            r'\bCSR-\d{5}\b(?!-)',
            r'\bCLN-\d{5}-\d{2}\b',
            r'\bCLN-\d{5}\b(?!-)',
            r'\bDDP-\d{5}\b',
            r'\bDCD-\d{5}-\d{2}\b',
            r'\bDCD-\d{5}\b(?!-)',
            r'\bDHF-\d{5}-[A-Z0-9]{2}\b',
            r'\bDHF-\d{5}\b(?!-)',
            r'\bDMR-\d{5}-[A-Z0-9]{2}\b',
            r'\bDMR-\d{5}\b(?!-)',
            r'\bDOT-\d{5}-\d{2}\b',
            r'\bDOT-\d{5}\b(?!-)',
            r'\bEDR-\d{5}\b(?!-)',
            r'\bFRM-\d{5}\b(?!-)',
            r'\bLRP-\d{5}\b(?!-)',
            r'\bLRR-\d{5}\b(?!-)',
            r'\bLHR-\d{5}\b(?!-)',
            r'\bLHR-\d{5}-\d{2}\b',
            r'\bLHR-\d{5}-\d{3}\b',
            r'\bMPI-\d{5}\b(?!-)',
            r'\bMKG-\d{5}\b(?!-)',
            r'\bMKG-\d{5}-\d{2}\b',
            r'\bMA-\d{5}\b(?!-)',
            r'\bPCP-\d{5}-\d{2}\b',
            r'\bPCR-\d{5}\b(?!-)',
            r'\bPMSP-\d{5}\b(?!-)',
            r'\bPMSR-\d{5}\b(?!-)',
            r'\bPSUR-\d{5}\b(?!-)',
            r'\bQPL-\d{5}\b(?!-)',
            r'\bRAD-\d{5}\b(?!-)',
            r'\bRSK-\d{5}\b(?!-)',
            r'\bSLS-\d{5}\b(?!-)',
            r'\bSWP-\d{5}\b(?!-)',
            r'\bSOP-\d{5}\b(?!-)',
            r'\bSTM-\d{5}\b(?!-)',
            r'\bTFN-\d{5}\b(?!-)',
            r'\bTFN-\d{5}-\d{2}\b',
            r'\bTP-\d{5}\b(?!-)',
            r'\bTP-\d{5}-\d{2}\b',
            r'\bTR-\d{5}\b(?!-)',
            r'\bTR-\d{5}-\d{2}\b',
            r'\bWRK-\d{5}\b(?!-)',
            r'\bFAB-\d{5}-\d{3}-\d{3}\b',
            r'\bBRD-\d{5}-\d{3}-\d{3}\b',
            r'\bGTI-\d{5}-\d{2}\b',
            r'\bEQP-\d{5}\b',
            r'\bPRT-\d{5}-\d{3}-\d{3}\b',
            r'\bPRT-\d{5}-\d{3}\b',
            r'\bLBL-\d{5}-\d{3}\b',
            r'\bOTS-\d{5}-\d{3}\b',
            r'\bSCH-\d{5}-\d{3}-\d{3}\b',
            r'\bSW-\d{5}-\d{3}-\d{3}\b',
            r'\bTFX-\d{5}-\d{3}-\d{3}\b'
        ]

        matches = []
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            page_text = page.get_text().replace(" ", "")
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
                unique_matches = list(OrderedDict.fromkeys([match for match, _, _ in matches]))
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
