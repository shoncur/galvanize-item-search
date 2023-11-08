import sys
import fitz
import re
import os
import csv
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QProgressDialog, QLineEdit, QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QListWidget, QRadioButton, QMessageBox, QDialog
from PyQt5.QtGui import QPixmap, QIcon
from collections import OrderedDict
from patterns import list_of_patterns, supported_item_numbers
import requests
from requests.exceptions import HTTPError
from base import BASE_URL
from get_path import get_resource_path

arena_session_id = None
rev_dict = {chr(65 + i): i + 1 for i in range(26)}

class LoginPopup(QDialog):
    def __init__(self):
        super().__init__()

        # Remove the "What's this?" button
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.setWindowTitle("Login")
        self.email_label = QLabel("Email:", self)
        self.email_entry = QLineEdit(self)
        self.password_label = QLabel("Password:", self)
        self.password_entry = QLineEdit(self)
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Login", self)
        self.login_button.clicked.connect(self.login)

        self.error_label = QLabel(self)
        self.error_label.setStyleSheet("color: red")

        layout = QVBoxLayout()
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_entry)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_entry)
        layout.addWidget(self.login_button)
        layout.addWidget(self.error_label)

        self.setLayout(layout)

    def login(self):
        email = self.email_entry.text()
        password = self.password_entry.text()
        
        url = f'{BASE_URL}/login'
        headers = {'Content-Type':'application/json'}

        try:
            data = {
                'email':f'{email}',
                'password':f'{password}'
            }
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            global arena_session_id
            arena_session_id = response.json()['arenaSessionId']
        except Exception as error:
            print(f'Invalid entry: {error}')
            self.error_label.setText(f'Enter a valid email/password')
            return

        self.accept()

class PDFReader(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Galvanize Item Search')
        # Get absolute path of the script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Create widgets
        self.browse_button = QPushButton('Browse', self)
        self.browse_button.clicked.connect(self.browse_pdf)
        self.label = QLabel('No PDF file selected', self)
        self.list_widget = QListWidget(self)
        self.page_number_label = QLabel('Show duplicate items:', self)
        self.show_page_numbers_radio = QRadioButton('Yes', self)
        self.show_page_numbers_radio.setChecked(False)
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

        matches = []
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            page_text = page.get_text()#.replace(" ", "").replace("\n", "")  no longer getting rid of spaces to fix table reading
            print(page_text)
            for pattern in list_of_patterns:
                page_matches = re.findall(pattern, page_text, re.DOTALL)
                if page_matches:
                    cleaned_matches = [re.sub(r'\s', '', match) for match in page_matches]
                    matches.extend([(match, pattern, page_num + 1) for match in cleaned_matches])

        if matches:
            if self.show_page_numbers_radio.isChecked():
                for match, pattern, page_num in matches:
                    item = f'Page: {page_num} | {match}'
                    self.list_widget.addItem(item)
                    print(f"'{match}'")
            else:
                unique_matches = sorted(list(set([match for match, _, _ in matches])))
                progress_dialog = QProgressDialog("Loading items...", "Cancel", 0, len(unique_matches), self)
                progress_dialog.setWindowModality(Qt.WindowModal)
                progress_dialog.setAutoReset(False)
                progress_dialog.setAutoClose(False)
                progress_dialog.setValue(0)
                for index, match in enumerate(unique_matches):
                    progress_dialog.setValue(index)
                    QApplication.processEvents()
                    try: # Get the item from the items world in Arena
                        item_url = f'{BASE_URL}/items?number={match}'
                        item_headers = {'arena_session_id':f'{arena_session_id}', 'Content-Type':'application/json'}
                        item_response = requests.get(item_url, headers=item_headers)
                        item_lifecycle_phase = item_response.json()['results'][0]['lifecyclePhase']['name']
                        item_revision = item_response.json()['results'][0]['revisionNumber']
                        self.list_widget.addItem(f'{match} || {item_lifecycle_phase} | Rev {item_revision}')
                        print(f"'{match}'")
                    except Exception as error: 
                        try: # Try to get the item from the supplieritems world
                            supplier_item_url = f'{BASE_URL}/supplieritems?number={match}'
                            supplier_item_response = requests.get(supplier_item_url, headers=item_headers)
                            supplier_item_guid = supplier_item_response.json()['results'][0]['guid']
                            supplier_item_sourcing_url = f'{BASE_URL}/supplieritems/{supplier_item_guid}/sourcing'
                            supplier_item_sourcing_response = requests.get(supplier_item_sourcing_url, headers=item_headers)
                            try:
                                linked_item = supplier_item_sourcing_response.json()['results'][0]['item']['number']
                                linked_item_url = f'{BASE_URL}/items?number={linked_item}'
                                linked_item_response = requests.get(linked_item_url, headers=item_headers)
                                linked_item_revision = linked_item_response.json()['results'][0]['revisionNumber']
                                linked_item_lifecycle_phase = linked_item_response.json()['results'][0]['lifecyclePhase']['name']
                                self.list_widget.addItem(f'{match} | {linked_item} | {linked_item_lifecycle_phase} | Rev {linked_item_revision}')
                            except:
                                self.list_widget.addItem(f'{match} | Something went wrong, please check item # in Arena to verify the issue')
                                print(f'{error}')
                        except:
                            self.list_widget.addItem(f'{match} | Item not found in Arena')
                            print(f'{error}')
                    if progress_dialog.wasCanceled():
                        break
                progress_dialog.close()
            self.download_button.setEnabled(True)
        else:
            self.list_widget.addItem('Nothing found')
            self.download_button.setEnabled(False)

    def supported_numbers_window(self):
        # Create a new window
        window = QDialog(self)
        window.setWindowTitle('Supported Item Numbers')
        self.supported_list_widget = QListWidget(self)

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
        # else:
        #     QMessageBox.warning(self, 'Error', 'Please select a PDF file first.', QMessageBox.Ok)     No need to currently display this error

    def download_matches(self):
        if self.list_widget.count() == 0:
            QMessageBox.warning(self, 'Error', 'No matches found to download.', QMessageBox.Ok)
            return

        file_name, _ = QFileDialog.getSaveFileName(self, 'Save Matches', '', 'CSV Files (*.csv);;Text Files (*.txt)')
        if file_name:
            if file_name.lower().endswith('.csv'):
                with open(file_name, 'w', newline='') as file:
                    writer = csv.writer(file)
                    if self.show_page_numbers_radio.isChecked():
                        header = ['Page Number', 'Part Number']
                        writer.writerow(header)
                        # Write all matches with page numbers
                        for i in range(self.list_widget.count()):
                            item = self.list_widget.item(i).text()
                            writer.writerow(item.split('|'))
                            # writer.writerow(re.split(r'\||=', item))  # Split into cells if "|" or "=" is present
                    else:
                        header = ['Part Number', 'Galvanize Equivalent', 'Lifecycle Status', 'Revision']
                        writer.writerow(header)
                        # Write unique matches without page numbers
                        unique_matches = list(OrderedDict.fromkeys([self.list_widget.item(i).text() for i in range(self.list_widget.count())]))
                        for item in unique_matches:
                            writer.writerow(item.split('|'))  # Split into cells if "|" is present
            else:
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
    logo_path = get_resource_path("resources/galvanize_logo.png")
    app.setWindowIcon(QIcon(logo_path))
 
    # Show login popup
    login_popup = LoginPopup()
    if login_popup.exec_() != QDialog.Accepted:
        sys.exit(0)

    # Create main window
    window = PDFReader()
    window.show()
    sys.exit(app.exec_())
