import zipfile
import shutil
import os
from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QProgressBar,QDesktopWidget, QTextEdit, QApplication, QLabel, QVBoxLayout, QWizard,  QPushButton, QLineEdit, QFileDialog, QHBoxLayout
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
import sys
import subprocess
import configparser
import fnmatch
from PyQt5.QtWidgets import  QSpacerItem, QSizePolicy
import requests
import urllib.parse
import glob
from PyQt5.QtCore import QTimer
import time
import json
import warnings
import tempfile
from PyQt5.QtWidgets import QMessageBox
import smtplib
from selenium import webdriver
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib
import os
import time
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import random
from email.mime.text import MIMEText
warnings.filterwarnings("ignore", message=".*sipPyTypeDict\(\) is deprecated.*")
class IntroPage(QtWidgets.QWizardPage):
    def __init__(self):
        super().__init__()

        
        self.label = QLabel("Please select the Server Name and the Zip File:")
        
        self.serverNameLabel = QLabel("Server Name:")
        self.serverNameLineEdit = QLineEdit()
        self.serverNameButton = QPushButton("Browse")
        self.serverNameButton.clicked.connect(self.selectServerName)

        self.serverNameLayout = QHBoxLayout()
        self.serverNameLayout.addWidget(self.serverNameLineEdit)
        self.serverNameLayout.addWidget(self.serverNameButton)

        self.zipFileLabel = QLabel("Zip File:")
        self.zipFileLineEdit = QLineEdit()
        self.zipFileButton = QPushButton("Browse")
        self.zipFileButton.clicked.connect(self.selectZipFile)
        self.zipFileLayout = QHBoxLayout()
        self.zipFileLayout.addWidget(self.zipFileLineEdit)
        self.zipFileLayout.addWidget(self.zipFileButton)

        self.registerField("serverName*", self.serverNameLineEdit)
        self.registerField("zipFile*", self.zipFileLineEdit)
        self.back_arrow = QLabel("\u2190", self)  
        self.back_arrow.setFont(QFont('Arial', 24))
        self.back_arrow.mousePressEvent = self.go_back
        self.title_label = QLabel("Server Setup", self)  
        self.title_label.setFont(QFont('Arial', 17))
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.back_arrow)  
        top_layout.addStretch(1)
        top_layout.addWidget(self.title_label) 
        top_layout.addStretch(1)

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))  
        layout.addWidget(self.label)
        layout.addWidget(self.serverNameLabel)
        layout.addLayout(self.serverNameLayout)
        layout.addWidget(self.zipFileLabel)
        layout.addLayout(self.zipFileLayout)
        self.setLayout(layout)

        self.serverNameLineEdit.textChanged.connect(self.checkCompletion)
        self.zipFileLineEdit.textChanged.connect(self.checkCompletion)
        
      
    def go_back(self,event):
        self.wizard().close()  
        login_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'login.py')
        subprocess.Popen(['python3', login_script_path])
    def selectServerName(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        server_name = str(QFileDialog.getExistingDirectory(self, "Select Server Name"))
        if server_name:
            is_valid=False
            for root, dirs, files in os.walk(server_name):
             if 'standalone' in dirs and 'modules' in dirs:
               is_valid = True
               break
            if not is_valid: 
               QMessageBox.critical(self, "Invalid Server Directory", "The selected directory does not appear to be a valid server directory.")
               return
            self.serverNameLineEdit.setText(server_name)
            file_path = os.path.join(current_dir, 'server_name.txt')
            with open(file_path, 'w') as f:
             f.write(server_name)

    def selectZipFile(self):
        zip_file = str(QFileDialog.getOpenFileName(self, "Select Zip File", "", "Zip Files (*.zip)")[0])
        if zip_file:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
             if not any('configurations métiers' in name for name in zip_ref.namelist()) or not any('database drivers' in name for name in zip_ref.namelist()):
                QMessageBox.critical(self, "Invalid Zip File", "The selected zip file does not appear to be a valid deployment zip file.")
                return
            self.zipFileLineEdit.setText(zip_file)

    def checkCompletion(self, text):
        self.completeChanged.emit()



class RegistrationPage(QtWidgets.QWizardPage):
    def __init__(self):
        super().__init__()

        self.setTitle(" ")
        self.setSubTitle("Completion of Automation Process")
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)

        self.outputTextEdit = QTextEdit()
        self.outputTextEdit.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.progressBar)
        layout.addWidget(self.outputTextEdit)
        self.setLayout(layout)
    
    def setOutput(self, output):
        self.outputTextEdit.setText(output)

    def setProgress(self, progress):
        self.progressBar.setValue(progress)
        if progress < 100:
            self.wizard().button(QWizard.NextButton).setEnabled(False)
        else:
            self.wizard().button(QWizard.NextButton).setEnabled(True)

class ConclusionPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Test Execution")
        self.setSubTitle("Installation completed. The tests will now be executed.")

        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 0)  
        self.emailLabel = QLabel("Email:")
        self.emailLineEdit = QLineEdit()
        self.emailLineEdit.setFixedWidth(200)
        self.sendButton = QPushButton("Send Report")
        self.sendButton.setFixedWidth(100)
        self.sendButton.clicked.connect(self.send_email)
        self.statusLabel = QLabel()
        layout = QVBoxLayout()
        layout.addWidget(self.progressBar)
        layout.addWidget(self.emailLabel)
        layout.addWidget(self.emailLineEdit)
        layout.addWidget(self.sendButton)
        layout.addWidget(self.statusLabel)
        self.setLayout(layout)

    def initializePage(self):
        super().initializePage()
        self.wizard().setOption(QtWidgets.QWizard.NoBackButtonOnLastPage, True)
        QTimer.singleShot(0, self.execute_tests)  


    def execute_tests(self):
     self.progressBar.setRange(0, 0) 
     try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test1_path = os.path.join(current_dir, 'test1.py')
        result=subprocess.run(['pytest', test1_path, '--html=report.html'], capture_output=True, text=True)
        self.test_output = result.stdout
     except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the tests: {e}")
     finally:
        firefox_process = subprocess.Popen(['firefox', 'report.html'])
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.monitor_firefox(firefox_process))
        self.timer.start(1000)
    def monitor_firefox(self, process):
     if process.poll() is not None:  
        self.progressBar.setRange(0, 1) 
        self.progressBar.setValue(1) 
        self.timer.stop()  

    def send_email(self):
    # Setup webdriver
     options = Options()
     options.add_argument('-headless')  # Run in headless mode
     driver = webdriver.Firefox(options=options)
 
    # Set the window size
     driver.set_window_size(2560, 1440)

    # Open the HTML report and take a screenshot
     report_path = 'file:///home/selim/projet/report.html'
     driver.get(report_path)
    # Save the screenshot
     screenshot_path = '/home/selim/projet/report.png'
     driver.save_screenshot(screenshot_path)
     driver.quit()

     msg = MIMEMultipart()
     msg['From'] = 'mail'
     msg['To'] = self.emailLineEdit.text()
     msg['Subject'] = 'Test Report'
     email_body = "Test Output:\n" + self.test_output
     msg.attach(MIMEText(email_body, 'plain'))

     with open(screenshot_path, 'rb') as file:
        img = MIMEImage(file.read())
     img.add_header('Content-Disposition', 'attachment; filename="report.png"')
     msg.attach(img)

     try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login('mail', 'password')
        server.send_message(msg)
        server.quit()
        self.statusLabel.setText('Email sent successfully')
     except Exception as e:
        self.statusLabel.setText(f'Failed to send email: {e}')

class SqlExecutionError(Exception):
    pass

class MyWizard(QtWidgets.QWizard):
    def __init__(self, parent=None):
        super(MyWizard, self).__init__(parent)
        self.centerOnScreen()
        self.intro_page = IntroPage()
        self.registration_page = RegistrationPage()
        self.conclusion_page = ConclusionPage()
        self.addPage(self.intro_page)
        self.addPage(self.registration_page)
        self.addPage(self.conclusion_page)

        self.setWindowTitle(" ")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setButtonText(QWizard.NextButton, "Next")
        self.setButtonText(QWizard.FinishButton, "Finish") 
        self.currentIdChanged.connect(self.update_button_layout)
        self.base_url = None
        self.url = None
        self.response_text = None
    def update_button_layout(self, id):
        if id == 0:
            # back button
            self.setButtonLayout([QWizard.Stretch, QWizard.NextButton, QWizard.FinishButton, QWizard.CancelButton])
        else:
            
            self.setButtonLayout([QWizard.Stretch, QWizard.BackButton, QWizard.NextButton, QWizard.FinishButton, QWizard.CancelButton])    
    def centerOnScreen(self):
        resolution = QDesktopWidget().screenGeometry()
        self.move(int((resolution.width() / 2) - (self.frameSize().width() / 2)),
                  int((resolution.height() / 2) - (self.frameSize().height() / 2)))

    def validateCurrentPage(self):
     if self.currentPage() == self.intro_page:
        server_name = str(self.intro_page.serverNameLineEdit.text())
        zip_file_path = str(self.intro_page.zipFileLineEdit.text())
        current_dir = os.path.dirname(os.path.realpath(__file__))
        if server_name and zip_file_path:
            output = StringIO()
            with redirect_stdout(output), redirect_stderr(output):
                try:
                    
                    destination_dir = os.path.dirname(zip_file_path)
                    unzipped_folder_path = os.path.join(destination_dir, os.path.basename(zip_file_path).replace('.zip', ''))
                    with open(os.path.join(current_dir, 'unzipped_folder_path.txt'), 'w') as f:
                         f.write(unzipped_folder_path)
                    if not os.path.exists(unzipped_folder_path):
                        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                            zip_ref.extractall(destination_dir)
                        print("File unzipped successfully!")
                        self.registration_page.setProgress(20) 
                         
                    
                    self.copy_database_drivers(unzipped_folder_path, server_name)
                    self.registration_page.setProgress(40)
                    self.copy_standalone_xml(unzipped_folder_path, server_name)
                    self.registration_page.setProgress(60)
                    self.execute_shell_scripts(unzipped_folder_path)
                    self.execute_sql_scripts(unzipped_folder_path, server_name)
                    self.registration_page.setProgress(80) 
                    self.move_ear_files(unzipped_folder_path, server_name)
                    QTimer.singleShot(5000, lambda: self.after_configuration(unzipped_folder_path, output))
                    
                except Exception as e:
                    print("An error occurred:", e)
                    self.registration_page.setProgress(80)  # Set progress to 80% if an error occurred
                self.registration_page.setOutput(output.getvalue())
     elif self.currentPage() == self.registration_page:
        if self.registration_page.progressBar.value() < 100:
            return False
     return True
    def after_configuration(self, unzipped_folder_path, output):
     configuration_output = StringIO()
     with redirect_stdout(configuration_output), redirect_stderr(configuration_output):
        success = self.configuration(unzipped_folder_path)
     output.write(configuration_output.getvalue())
    
     if success:
        self.registration_page.setProgress(100) 
        output.write("Tasks completed successfully!\n")
     else:
        output.write("Configuration failed.\n")

     self.registration_page.setOutput(output.getvalue())
    
    def copy_database_drivers(self, unzipped_folder_path, server_name):
     destination_dir = os.path.dirname(unzipped_folder_path)  
     database_drivers_path = os.path.join(unzipped_folder_path, 'database drivers')
     if os.path.exists(database_drivers_path):
        for dir_name in os.listdir(database_drivers_path):
            driver_path = os.path.join(database_drivers_path, dir_name)
            if os.path.isdir(driver_path):
                if dir_name == 'com':
                    self.copy_directory_with_verification(driver_path,
                                                          os.path.join(destination_dir, server_name, 'modules', 'system', 'layers', 'base', 'com'))
                elif dir_name == 'org':
                    self.copy_directory_with_verification(driver_path,
                                                          os.path.join(destination_dir, server_name, 'modules', 'system', 'layers', 'base', 'org'))
     else:
        print("Database drivers directory not found.")

    def copy_standalone_xml(self, unzipped_folder_path, server_name):
      print("Copying standalone.xml to destination...")
      for root, dirs, files in os.walk(unzipped_folder_path):
        if 'standalone.xml' in files:
            source_standalone_xml = os.path.join(root, 'standalone.xml')
            destination_file = os.path.join(server_name, 'standalone', 'configuration', 'standalone.xml')
            destination_dir = os.path.dirname(destination_file)
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)
            if os.path.exists(destination_file):
                print("Removing existing standalone.xml in wildfly.")
                os.remove(destination_file)
            shutil.copy2(source_standalone_xml, destination_file)
            print("Standalone.xml copied to wildfly successfully!")
            break
      else:
        print("Source standalone.xml not found.")


    def execute_shell_scripts(self, unzipped_folder_path):
        for root, dirs, files in os.walk(unzipped_folder_path):
            for file in files:
                if file.endswith('.sh'):
                    script_path = os.path.join(root, file)
                    print("Executing script: {}".format(script_path))
                    try:
                        subprocess.run(['sh', script_path], check=True)
                        print("Script executed successfully!")
                    except subprocess.CalledProcessError as e:
                        print("An error occurred while executing the script:", e)


    def move_ear_files(self, unzipped_folder_path, server_name):
     for root, dirs, files in os.walk(unzipped_folder_path):
        for file in files:
            if file.endswith('.ear'):
                ear_file_path = os.path.join(root, file)
                print("Found .ear file: {}".format(ear_file_path))
                destination_path = os.path.join(server_name, 'standalone', 'deployments', file)
                
                if os.path.exists(destination_path):
                    print("File already exists in the destination directory. Removing...")
                    os.remove(destination_path)
                
                shutil.copy(ear_file_path, destination_path)
                print(".ear file {} moved to server's standalone/deployments directory: {}".format(file, destination_path))

    def execute_sql_scripts(self, unzipped_folder_path, server_name):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(current_dir, 'output.txt'), 'w') as f:
         print("Executing SQL scripts...")
         f.write("Executing SQL scripts...\n")
         for root, dirs, files in os.walk(unzipped_folder_path):
            for file in files:
                if file.endswith('.sql'):
                    sql_file_path = os.path.join(root, file)
                    conf_file_path = self.find_conf_file(unzipped_folder_path, file.replace('.sql', '.conf'))
                    if conf_file_path:
                        print("Found corresponding .conf file for .sql file: {}".format(conf_file_path))
                        f.write("Found corresponding .conf file for .sql file: {}\n".format(conf_file_path))
                        config = configparser.ConfigParser()
                        config.read(conf_file_path)
                        db_type = config.get('database', 'DB_TYPE')
                        username = config.get('database', 'DB_USER')
                        password = config.get('database', 'DB_PASSWORD')
                        connection_string = config.get('database', 'DB_CONNECTION_STRING')
                        try:
                            if db_type.lower() == 'oracle':
                                sqlplus_cmd = ['sqlplus', '-S', f'{username}/{password}@{connection_string}']
                                with open(sql_file_path, 'r') as sql_file:
                                    sql_script = sql_file.read()
                                process = subprocess.Popen(sqlplus_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                stdout, stderr = process.communicate(input=sql_script.encode())

                                stdout_decoded = stdout.decode()
                                stderr_decoded = stderr.decode()
                                if process.returncode == 0:
                                    print("stdout:")
                                    print("stderr:", stderr_decoded)
                                    f.write("stdout:\n")
                                    f.write("stderr: {}\n".format(stderr_decoded))
                                else:    
                                 if"SP2-0552: Bind variable \"NEW\" not declared." not in stdout_decoded:
                                  print("stdout:", stdout_decoded)
                                 if "SP2-0552: Bind variable \"NEW\" not declared." not in stdout_decoded:
                                  f.write("stdout: {}\n".format(stdout_decoded))  
                            elif db_type.lower() == 'postgresql':
                                db_name = config.get('database', 'DB_NAME')
                                os.environ['PGPASSWORD'] = password
                                subprocess.run(['psql', '-h', 'localhost', '-U', username, '-d', db_name, '-f', sql_file_path],  check=True)
    
                            else:
                                print("Unsupported database type: {}".format(db_type))
                                f.write("Unsupported database type: {}\n".format(db_type))
                            print(".sql file executed successfully!")
                            f.write(".sql file executed successfully!\n")
                        except subprocess.CalledProcessError as e:
                            print("An error occurred while executing the .sql file:", e)
                            f.write("An error occurred while executing the .sql file: {}\n".format(e))
                            raise SqlExecutionError("An error occurred while executing the .sql file") from e
                    else:
                        print("No corresponding .conf file found for .sql file: {}".format(sql_file_path))
                        f.write("No corresponding .conf file found for .sql file: {}\n".format(sql_file_path))            

    def copy_directory_with_verification(self, source_dir, destination_dir):
        print("Copying contents of {} to {}".format(source_dir, destination_dir))
        if os.path.exists(destination_dir):
            print("Destination directory already exists.")
        else:
            os.makedirs(destination_dir)  

        for root, dirs, files in os.walk(source_dir):
            for file in files:
                source_file = os.path.join(root, file)
                relative_path = os.path.relpath(source_file, source_dir)
                destination_file = os.path.join(destination_dir, relative_path)
                destination_dirname = os.path.dirname(destination_file)

                if not os.path.exists(destination_dirname):
                    os.makedirs(destination_dirname)  

                shutil.copy2(source_file, destination_file)

        print("Contents copied to {} successfully!".format(destination_dir))

    def find_conf_file(self, root, filename):
        for root, dirs, files in os.walk(root):
            for file in fnmatch.filter(files, filename):
                return os.path.join(root, file)
        return None


    def configuration(self, unzipped_folder_path):
     import urllib3
     current_dir = os.path.dirname(os.path.realpath(__file__))
     urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


     base_url = "https://localhost:8443/User-app/api/config/reload"
     config_dir = os.path.join(unzipped_folder_path, "configurations métiers")
     xml_files = glob.glob(os.path.join(config_dir, "**", "*.xml"), recursive=True)
     if not xml_files:
        print("No XML files found in the 'configurations métiers' directory.")
        return
     file_path = xml_files[0]  

  
     encoded_file_path = urllib.parse.quote(file_path)

   
     url = f"{base_url}?path={encoded_file_path}"
     max_retries = 5
     backoff_factor = 0.5
     for i in range(max_retries):
        try:
         response = requests.get(url, verify=False)
         if response.status_code == 200:
            print(response.text)
            state = {
                'base_url': base_url,
                'url': url,
                'response_text': response.text,
            }
            with open(os.path.join(current_dir, 'configuration_state.json'), 'w') as f:
                    json.dump(state, f)
            return True
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
          print(f"GET request failed with exception: {e}. Retrying...")
        except requests.exceptions.HTTPError as e:
          print(f"GET request failed with status code: {e.response.status_code}. Retrying...")
        except requests.exceptions.RequestException as e:
          print(f"Unexpected error: {e}. Retrying...")

    # Exponential backoff
        time.sleep(backoff_factor * (2 ** i) + random.uniform(0, 1))

     print("Failed to get a response after maximum retries.")
     return False
     

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    # Set a custom style sheet
    app.setStyleSheet("""
        QWidget {
            background-color: #333;
            color: #fff;
            font-family: 'Arial';
        }
        QPushButton {
            background-color: #555;
            border: 2px solid #fff;
            border-radius: 5px;
            padding: 5px;
            color: #fff;
        }
        QPushButton:hover {
            background-color: #777;
        }
        QLineEdit {
            background-color: #555;
            border: 2px solid #fff;
            border-radius: 5px;
            padding: 5px;
            color: #fff;
        }
        QTextEdit {
            background-color: #555;
            border: 2px solid #fff;
            border-radius: 5px;
            padding: 5px;
            color: #fff;
        }
        QProgressBar {
            border: 2px solid #fff;
            border-radius: 5px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #777;
        }
    """)

    wizard = MyWizard()
    wizard.show()

    sys.exit(app.exec_())