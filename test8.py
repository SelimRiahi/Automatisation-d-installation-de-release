import zipfile
import os
def extract_file(file_path, output_dir):
    """
    Extracts a .ear or .war file to a specified directory.

    Parameters:
    file_path (str): The path to the .ear or .war file.
    output_dir (str): The directory where the file should be extracted.
    """
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
        print(f"Extracted {file_path} to {output_dir}")

def extract_ear_and_war_files(ear_file_path, output_dir):
    """
    Extracts an .ear file and any .war files it contains to a specified directory.

    Parameters:
    ear_file_path (str): The path to the .ear file.
    output_dir (str): The directory where the .ear file and .war files should be extracted.
    """
    # Extract the .ear file
    extract_file(ear_file_path, output_dir)

    # Extract any .war files
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.war'):
                war_file_path = os.path.join(root, file)
                war_output_dir = os.path.join(root, os.path.splitext(file)[0])
                extract_file(war_file_path, war_output_dir)

# Usage
ear_file_path = '/home/selim/projet/deploy/EarProject1.ear'  # Replace  .ear file path
output_dir = '/home/selim/projet/TESTOO'  # Replace  output directory path
extract_ear_and_war_files(ear_file_path, output_dir)