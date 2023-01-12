from github import Github
import sqlite3
import csv
import shutil
import configparser
from operator import itemgetter

def get_last_row_col_value(file_path):
    # Open the csv file
    with open(file_path, newline='') as file:
        # Read the rows from the csv file
        rows = list(csv.reader(file))

    if rows:
        # Get the value of the last row, first column
        last_row_col_value = rows[-1][0]
        return last_row_col_value
    else:
        print(f"{file_path} is empty!")

def sort_and_save_csv(file_path):
    # Open the csv file
    with open(file_path, newline='') as file:
        # Read the rows from the csv file
        rows = list(csv.reader(file))

    # Sort the rows by the date in column A
    sorted_rows = sorted(rows, key=itemgetter(0))

    # Open the file again to write the sorted rows
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        for row in sorted_rows:
            writer.writerow(row)
    print(f"{file_path} is sorted and saved!")

def check_changes(db_path, date_export):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Retrieve the current information from the "balances" table
    c.execute("SELECT * FROM balances WHERE date>'" + date_export + "' ORDER BY date ASC")
    current_data = set(c.fetchall())

    if current_data:
        # Open a file to store the new rows
        with open('temp.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            # Write the header row
            for row in current_data:
                writer.writerow(row)

        return('NOT_EMPTY')
    else:
        print("The table is empty. No new entries.")  
        return('EMPTY')          

def rename_csv(db_path, file_path):
     # Connect to the database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Get pilot name to differentiate user and name the csv
    c.execute("SELECT name FROM career")
    name = set(c.fetchall())

    # Extracting only the name
    name = name.pop()[0]

    # Get last date entry
    date = get_last_row_col_value(file_path)

    # Replace : with - in date
    date = date.replace(':', '_')

    # New name
    new_file = name + '_' + date + '.csv'

    # Current file name
    old_file = file_path

    # Rename
    shutil.move(old_file, new_file)

    # Return the name of the file
    return(new_file)

def export_to_github(access_token, file_name):
    # access token
    g = Github(access_token)

    # repository
    repo = g.get_repo("elyetis/neofly_synchro")

    try:
        # Get the file
        file_content = repo.get_contents(file_name)
        print(f"{file_name} is present in the {repo} repository.")
    except: 
        print(f"{file_name} is not present in the {repo} repository.")

        # The contents of the file
        with open(file_name, "r") as file:
            file_content = file.read()

        # The commit message
        commit_message = file_name

        # The branch name
        branch = "main"

        # Encode the file content so it can be uploaded
        file_content = file_content.encode()

        # Create the new file
        repo.create_file(file_name, commit_message, file_content, branch=branch)

def import_from_github(access_token, repo, user_import, date_import):
    # access token
    g = Github(access_token)
    
    # repository
    repo = g.get_repo(repo)

    # List all the files in the root directory
    files = repo.get_contents("uploads")

    # filter the list
    files = filter(lambda x: x.name.startswith(user_import) and x.name.endswith(".csv"), files)

    # Print the file names
    for file in files:
        # We want to have the date of the file from it's name to know if it's more recent than the last import
        # So we remove the Pseudo prefix and csv affix
        date_of_file = file.name.replace(user_import + "_", "").replace(".csv", "")

        # Then replace '_' with ':' in the hours
        date_of_file = date_of_file.replace("_", ":")

        # If it's more recent than the last import
        if date_of_file > date_import:

            # Download the files
            file_name = file.name
            file_content = file.decoded_content
            # Write the content to a local file
            with open(file_name, "wb") as f:
                f.write(file_content)







# Initalisation des variables .ini

ini = configparser.ConfigParser()
ini.read('neofly_sync.ini')

user_export = ini.get('config', 'user_export')
user_import = ini.get('config', 'user_import')
repo = ini.get('config', 'repo')
date_export = ini.get('config', 'date_export')
date_import = ini.get('config', 'date_import')
db_path = ini.get('config', 'db_path')



print(user_export + ' | ' + user_import  + ' | ' + repo + ' | ' + date_export + ' | ' + date_import + ' | ' + db_path)

#Git Access token
access_token = "access_token"



#---------------------------------


new_entries = check_changes(db_path, date_export)

if new_entries != 'EMPTY':
    sort_and_save_csv('temp.csv')
    name_of_exportcsv = rename_csv(db_path, 'temp.csv')
    export_to_github(access_token, name_of_exportcsv)

    ini['config']['date_export'] = get_last_row_col_value(name_of_exportcsv)

    with open('neofly_sync.ini', 'w') as configfile:
        ini.write(configfile)


import_from_github(access_token, repo, user_import, date_import)

