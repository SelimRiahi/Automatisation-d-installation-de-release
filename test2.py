import os
import subprocess
import filecmp
import configparser
from Wizardd import MyWizard

def test_executes_sql_script():
    test_obj = MyWizard()
    unzipped_folder_path = '/home/selim/projet/deploy'
    server_name = '/home/selim/projet/wildfly-26.1.3.Final'

    # Look for .conf files in the unzipped_folder_path
    for root, dirs, files in os.walk(unzipped_folder_path):
        for file in files:
            if file.endswith('.conf'):
                conf_file_path = os.path.join(root, file)

                # Read the database configuration from the .conf file
                config = configparser.ConfigParser()
                config.read(conf_file_path)
                db_type = config.get('database', 'DB_TYPE')
                username = config.get('database', 'DB_USER')
                password = config.get('database', 'DB_PASSWORD')
                connection_string = config.get('database', 'DB_CONNECTION_STRING')
                db_name = config.get('database', 'DB_NAME') if db_type.lower() == 'postgresql' else None

                # Create a dump of the database before executing the SQL scripts
                if db_type.lower() == 'oracle':
                    dump_cmd = ['expdp', f'{username}/{password}@{connection_string}', 'DIRECTORY=dump_dir', 'DUMPFILE=before.dmp']
                elif db_type.lower() == 'postgresql':
                    dump_cmd = ['pg_dump', '-h', 'localhost', '-U', username, '-d', db_name, '-f', 'before.sql']
                subprocess.run(dump_cmd, check=True)

                # Execute the SQL scripts
                test_obj.execute_sql_scripts(unzipped_folder_path, server_name)

                # Create another dump of the database after executing the SQL scripts
                if db_type.lower() == 'oracle':
                    dump_cmd[2] = 'DUMPFILE=after.dmp'
                elif db_type.lower() == 'postgresql':
                    dump_cmd[4] = 'after.sql'
                subprocess.run(dump_cmd, check=True)

                # Compare the two dumps
                assert filecmp.cmp('before.dmp' if db_type.lower() == 'oracle' else 'before.sql',
                                   'after.dmp' if db_type.lower() == 'oracle' else 'after.sql',
                                   shallow=False)

                # Clean up the test environment
                os.remove('before.dmp' if db_type.lower() == 'oracle' else 'before.sql')
                os.remove('after.dmp' if db_type.lower() == 'oracle' else 'after.sql')

test_executes_sql_script()