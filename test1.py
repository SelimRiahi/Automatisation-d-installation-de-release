import sys
from PyQt5.QtWidgets import QApplication
import os
import filecmp
import difflib
import zipfile
import shutil
import tempfile
import mimetypes
import pytest
import json
def get_files_of_type(directory, file_extension):
    return set(os.path.join(root.replace(directory, ''), f) 
               for root, dirs, files in os.walk(directory) 
               for f in files if f.endswith(file_extension))

def get_files_of_type_in_dir(directory, file_extension):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(file_extension)]

def extract_file(file_path, output_dir):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
def extract_ear_and_war_files(ear_file_path, output_dir):
    extract_file(ear_file_path, output_dir)
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.war'):
                war_file_path = os.path.join(root, file)
                war_output_dir = os.path.join(root, os.path.splitext(file)[0])
                extract_file(war_file_path, war_output_dir)

def compare_dirs(dir1, dir2):
    comparison = filecmp.dircmp(dir1, dir2)
    assert len(comparison.left_only) == 0, f"Files in {dir1} but not in {dir2}: {comparison.left_only}"
    assert len(comparison.right_only) == 0, f"Files in {dir2} but not in {dir1}: {comparison.right_only}"
    assert len(comparison.diff_files) == 0, f"Files with differing contents in {dir1} and {dir2}: {comparison.diff_files}"
    for common_dir in comparison.common_dirs:
        compare_dirs(os.path.join(dir1, common_dir), os.path.join(dir2, common_dir))
class TestDatabaseDrivers:
    def setup_method(self):
        # Create a QApplication instance before running the tests
        self.app = QApplication(sys.argv)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        server_name_file = os.path.join(current_dir, 'server_name.txt')
        unzipped_folder_path_file = os.path.join(current_dir, 'unzipped_folder_path.txt')
        with open(server_name_file, 'r') as f:
         self.server_name = f.read().strip()
        with open(unzipped_folder_path_file, 'r') as f:
         self.unzipped_folder_path = f.read().strip()
        self.extraction_folder_path = tempfile.mkdtemp(dir=os.getcwd())  # create a temporary directory in the current working directory

    def teardown_method(self):
        # Clean up QApplication instance after running all tests
        self.app.quit()
        shutil.rmtree(self.extraction_folder_path)

    def test_copy_database_drivers(self):
        unzipped_com_dir = None
        unzipped_org_dir = None
        for root, dirs, files in os.walk(self.unzipped_folder_path):
         if 'com' in dirs:
            unzipped_com_dir = os.path.join(root, 'com')
         if 'org' in dirs:
            unzipped_org_dir = os.path.join(root, 'org')
         if unzipped_com_dir and unzipped_org_dir:
            break
        
       
        
        com_exists = os.path.exists(unzipped_com_dir) if unzipped_com_dir else False
        org_exists = os.path.exists(unzipped_org_dir) if unzipped_org_dir else False
        # Check if 'com' and 'org' directories are copied to the correct destination
        destination_dir = os.path.join(os.path.dirname(self.unzipped_folder_path), self.server_name)
        server_com_dir = os.path.join(destination_dir, 'modules', 'system', 'layers', 'base', 'com')
        server_org_dir = os.path.join(destination_dir, 'modules', 'system', 'layers', 'base', 'org')
        server_com_dirs = set(os.listdir(server_com_dir)) if os.path.exists(server_com_dir) else set()
        server_org_dirs = set(os.listdir(server_org_dir)) if os.path.exists(server_org_dir) else set()
        com_checked = False
        org_checked = False
        errors = []
        if com_exists:
    # Get the directory inside 'com'
          unzipped_com_subdir = next(os.walk(unzipped_com_dir))[1][0]
          com_checked = True 
    # Define the directories in both locations
          unzipped_subdir_path = os.path.join(unzipped_com_dir, unzipped_com_subdir)
          server_subdir_path = os.path.join(server_com_dir, unzipped_com_subdir)
 
    # Check if the directories exist in both locations
          if not os.path.exists(unzipped_subdir_path) or not os.path.exists(server_subdir_path):
            errors.append(f"{unzipped_com_subdir} directory does not exist ")
          else:
        # Get the contents of the directories
            unzipped_subdir_contents = set(os.listdir(unzipped_subdir_path))
            server_subdir_contents = set(os.listdir(server_subdir_path))

        # Print the contents
            print(f"Unzipped {unzipped_com_subdir} contents: {unzipped_subdir_contents}")
            print(f"Server {unzipped_com_subdir} contents: {server_subdir_contents}")
        # Check that all contents of the server directory also exist in the unzipped directory
            assert server_subdir_contents.issubset(unzipped_subdir_contents)
          
          unzipped_xml_files = get_files_of_type(unzipped_subdir_path, '.xml')
          unzipped_jar_files = get_files_of_type(unzipped_subdir_path, '.jar')
          server_xml_files = get_files_of_type(server_subdir_path, '.xml')
          server_jar_files = get_files_of_type(server_subdir_path, '.jar')
          if not server_xml_files.issubset(unzipped_xml_files):
           errors.append('Missing XML files in com unzipped directory')
          if not server_jar_files.issubset(unzipped_jar_files):
           errors.append('Missing JAR files in com unzipped directory')

    # Also check that all .xml and .jar files in the unzipped directory also exist in the server directory
          if not unzipped_xml_files.issubset(server_xml_files):
           errors.append('Missing XML files in com server directory')
          if not unzipped_jar_files.issubset(server_jar_files):
           errors.append('Missing JAR files in com server directory')

# Repeat the same process for 'org'
        
        if org_exists:
    # Get the directory inside 'org'
           unzipped_org_subdir = next(os.walk(unzipped_org_dir))[1][0]
           unzipped_subdir_path = os.path.join(unzipped_org_dir, unzipped_org_subdir)
           server_subdir_path = os.path.join(server_org_dir, unzipped_org_subdir)  # Use the same subdirectory name
           if not os.path.exists(unzipped_subdir_path) or not os.path.exists(server_subdir_path):
            errors.append(f"{unzipped_org_subdir} directory does not exist ")
           else: 
            unzipped_subdir_contents = set(os.listdir(unzipped_subdir_path))
            server_subdir_contents = set(os.listdir(server_subdir_path))
            print(f"Unzipped {unzipped_org_subdir} contents: {unzipped_subdir_contents}")
            print(f"Server {unzipped_org_subdir} contents: {server_subdir_contents}")

        # Check that all contents of the server directory also exist in the unzipped directory
            assert server_subdir_contents.issubset(unzipped_subdir_contents)
             
           unzipped_xml_files = get_files_of_type(unzipped_subdir_path, '.xml')
           unzipped_jar_files = get_files_of_type(unzipped_subdir_path, '.jar')
           server_xml_files = get_files_of_type(server_subdir_path, '.xml')
           server_jar_files = get_files_of_type(server_subdir_path, '.jar')   
           if not server_xml_files.issubset(unzipped_xml_files):
            errors.append('Missing XML files in org unzipped directory')
           if not server_jar_files.issubset(unzipped_jar_files):
            errors.append('Missing JAR files in org unzipped directory')
 
    # Also check that all .xml and .jar files in the unzipped directory also exist in the server directory
           if not unzipped_xml_files.issubset(server_xml_files):
            errors.append('Missing XML files in org server directory')
           if not unzipped_jar_files.issubset(server_jar_files):
            errors.append('Missing JAR files in org server directory')
        if errors:
          raise AssertionError('\n'.join(errors))    
        if not com_exists and not org_exists:
         raise AssertionError("Neither 'com' nor 'org' directories were found in the unzipped folder. ")


    def test_copy_standalone_xml(self):
    # Arrange
     source_standalone_xml = None

    # Assert
     for root, dirs, files in os.walk(self.unzipped_folder_path):
        if 'standalone.xml' in files:
            source_standalone_xml = os.path.join(root, 'standalone.xml')
            break

     assert source_standalone_xml is not None, "Source standalone.xml not found."

     destination_dir = os.path.join(self.server_name, 'standalone', 'configuration')
     assert os.path.exists(destination_dir), "Destination directory not found."

     destination_file = os.path.join(destination_dir, 'standalone.xml')
     assert os.path.exists(destination_file), "Destination standalone.xml not found."

     with open(source_standalone_xml, 'rb') as f:
        source_contents = f.read().decode('utf-8').replace('\r\n', '\n').replace('\r', '\n')

     with open(destination_file, 'rb') as f:
        destination_contents = f.read().decode('utf-8').replace('\r\n', '\n').replace('\r', '\n')

     if source_contents != destination_contents:
        diff = difflib.unified_diff(
            source_contents.splitlines(),
            destination_contents.splitlines(),
            fromfile='source',
            tofile='destination',
        )
        print(''.join(diff))
        assert False, "Source and destination standalone.xml files are not the same."


    def test_ear_files_contents(self):
        deployments_dir = os.path.join(self.server_name, 'standalone', 'deployments')
        unzipped_ear_files = get_files_of_type_in_dir(self.unzipped_folder_path, '.ear')
        server_ear_files = get_files_of_type_in_dir(deployments_dir, '.ear')

        assert os.path.isdir(deployments_dir), "Deployments directory does not exist."
        assert set(os.path.basename(f) for f in unzipped_ear_files) == set(os.path.basename(f) for f in server_ear_files), "Mismatch in .ear files names between unzipped folder and server deployments directory."

        for ear_file in unzipped_ear_files:
         output_dir = os.path.join(self.extraction_folder_path, os.path.splitext(os.path.basename(ear_file))[0])
         extract_ear_and_war_files(ear_file, output_dir)

         server_ear_file = os.path.join(deployments_dir, os.path.basename(ear_file))
         server_output_dir = os.path.join(self.extraction_folder_path, os.path.splitext(os.path.basename(server_ear_file))[0] + "_server")
         extract_ear_and_war_files(server_ear_file, server_output_dir)

    # Compare file names
         unzipped_files = set(file for root, dirs, files in os.walk(output_dir) for file in files)
         server_files = set(file for root, dirs, files in os.walk(server_output_dir) for file in files)
         assert unzipped_files == server_files, f"Mismatch in file names between {output_dir} and {server_output_dir}."

    # Compare file contents
         for root, dirs, files in os.walk(output_dir):
          for file in files:
           unzipped_file_path = os.path.join(root, file)
           server_file_path = unzipped_file_path.replace(output_dir, server_output_dir)
           mime_type = mimetypes.guess_type(unzipped_file_path)[0]
           if mime_type not in ['text/plain', 'application/xml', 'text/xml']:
              continue
        
           with open(unzipped_file_path, 'r') as f1, open(server_file_path, 'r') as f2:
            diff = difflib.unified_diff(
                f1.readlines(),
                f2.readlines(),
                fromfile=unzipped_file_path,
                tofile=server_file_path,
            )

           diff_report = ''.join(diff)
           assert not diff_report, f"Mismatch in contents of {unzipped_file_path} and {server_file_path}:\n{diff_report}"
    def test_configuration(self):
     current_dir = os.path.dirname(os.path.abspath(__file__))
     file_path = os.path.join(current_dir, 'configuration_state.json')
     with open(file_path, 'r') as f:
        state = json.load(f)


    # Assert that the state is as expected
     assert state['base_url'] is not None
     assert state['base_url'].startswith("https://")
     assert state['url'] is not None
     assert state['url'].startswith(state['base_url'])
     assert state['response_text'] is not None
     assert isinstance(state['response_text'], str)


  

    def test_execute_sql_scripts(self):
     # Count the number of SQL files in the unzipped folder
     sql_file_count = sum(1 for root, dirs, files in os.walk(self.unzipped_folder_path) for file in files if file.endswith('.sql'))
     current_dir = os.path.dirname(os.path.abspath(__file__))
     file_path = os.path.join(current_dir, 'output.txt')
    # Assert
     with open(file_path, 'r') as f:
        output = f.read()
     assert "Executing SQL scripts..." in output
     assert "Found corresponding .conf file for .sql file:" in output
     assert "stdout:" in output
     assert "stderr:" in output
     assert "Unsupported database type:" not in output
     assert "An error occurred while executing the .sql file:" not in output
     assert output.count(".sql file executed successfully!") == sql_file_count
     assert "No corresponding .conf file found for .sql file:" not in output

@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """Cleanup a testing session."""
    def remove_files():
        if os.path.exists('server_name.txt'):
            os.remove('server_name.txt')
        if os.path.exists('unzipped_folder_path.txt'):
            os.remove('unzipped_folder_path.txt')
        if os.path.exists('configuration_state.json'): 
            os.remove('configuration_state.json')    
        if os.path.exists('output.txt'):
            os.remove('output.txt')    
    request.addfinalizer(remove_files)
    