import sys
from PyQt5.QtWidgets import QApplication
import unittest
import os
from Wizardd import MyWizard
import filecmp

class TestDatabaseDrivers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a QApplication instance before running the tests
        cls.app = QApplication(sys.argv)

    @classmethod
    def tearDownClass(cls):
        # Clean up QApplication instance after running all tests
        cls.app.quit()

    def setUp(self):
        # Create an instance of MyWizard
        self.wizard = MyWizard()

        # Import the server name and the path to the unzipped folder from the application
        self.server_name = self.wizard.intro_page.serverNameLineEdit.text()
        self.unzipped_folder_path = self.wizard.intro_page.zipFileLineEdit.text()

    def test_copy_database_drivers(self):
        # Determine the directories present in the unzipped folder
        unzipped_com_dir = os.path.join(self.unzipped_folder_path, 'com')
        unzipped_org_dir = os.path.join(self.unzipped_folder_path, 'org')
        com_exists = os.path.exists(unzipped_com_dir)
        org_exists = os.path.exists(unzipped_org_dir)

        # Check if 'com' and 'org' directories are copied to the correct destination
        destination_dir = os.path.join(os.path.dirname(self.unzipped_folder_path), self.server_name)
        server_com_dir = os.path.join(destination_dir, 'modules', 'system', 'layers', 'base', 'com')
        server_org_dir = os.path.join(destination_dir, 'modules', 'system', 'layers', 'base', 'org')

        if com_exists:
            self.assertTrue(os.path.exists(server_com_dir))
            self.assertTrue(directories_are_identical(unzipped_com_dir, server_com_dir))
        if org_exists:
            self.assertTrue(os.path.exists(server_org_dir))
            self.assertTrue(directories_are_identical(unzipped_org_dir, server_org_dir))

def directories_are_identical(dir1, dir2):
    # Recursively compare contents of two directories
    dir1_files = set(os.listdir(dir1))
    dir2_files = set(os.listdir(dir2))
    if dir1_files != dir2_files:
        return False
    for file in dir1_files:
        file1 = os.path.join(dir1, file)
        file2 = os.path.join(dir2, file)
        if os.path.isdir(file1):
            if not directories_are_identical(file1, file2):
                return False
        elif not filecmp.cmp(file1, file2):
            return False
    return True

if __name__ == '__main__':
    unittest.main()
