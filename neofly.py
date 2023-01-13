from github import Github
import os
import sqlite3
import csv
import shutil
import configparser
import psutil
from operator import itemgetter
from datetime import datetime, timedelta

def is_running(process_name):
    for process in psutil.process_iter():
        try:
            if process_name.lower() in process.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

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

        # Close the connection
        conn.close()

        return('NOT_EMPTY')
    else:
        print("The table is empty. No new entries.")  

        # Close the connection
        conn.close()

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

    # Close the connection
    conn.close()

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
        repo.create_file("uploads/" + file_name, commit_message, file_content, branch=branch)

def import_from_github(access_token, repo, user_import, date_import):
    # access token
    g = Github(access_token)
    
    # repository
    repo = g.get_repo(repo)

    # List all the files in the root directory
    files = repo.get_contents("uploads")

    # filter the list
    files = filter(lambda x: x.name.startswith(user_import) and x.name.endswith(".csv"), files)

    # Initialize a variable to keep track of whether you've found a file
    result_found = "EMPTY"

    # Print the file names
    for file in files:
        # We want to have the date of the file from it's name to know if it's more recent than the last import
        # So we remove the Pseudo prefix and csv affix
        date_of_file = file.name.replace(user_import + "_", "").replace(".csv", "")

        # Then replace '_' with ':' in the hours
        date_of_file = date_of_file.replace("_", ":")

        # If it's more recent than the last import
        if date_of_file > date_import:
            # Update result_found so we can return it's value
            result_found = "NOT_EMPTY"

            # Download the files
            file_name = file.name
            file_content = file.decoded_content
            # Write the content to a local file
            with open('neofly_sync_imports/' + file_name, "wb") as f:
                f.write(file_content)

    return(result_found)

def modify_import_content(user_import, export_UTC, import_UTC):
    folder_path = "neofly_sync_imports"

    # Get all the CSV files in the folder
    csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv') and file.startswith(user_import)]

    # Calculate time difference
    if export_UTC > import_UTC:
        time_dif = (import_UTC - export_UTC)*(-1)
    elif import_UTC > export_UTC:
        time_dif = (import_UTC - export_UTC)*(-1)


    # Open the new CSV file for writing
    with open(os.path.join(folder_path,"all_in_one.csv"), "w", newline="") as new_file:
        writer = csv.writer(new_file)
        # Loop through the CSV files and write the rows to the new file
        for file in csv_files:
            with open(os.path.join(folder_path, file), "r") as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    # Insert the name of the other user in the description
                    row[1] = user_import + " : " + row[1]

                    # Get the date of that entry
                    datetime_import = row[0]

                    # Convert to datetime objects
                    datetime_import = datetime.strptime(datetime_import, "%Y-%m-%d %H:%M:%S")

                    # Create a timedelta object from test2_datetime
                    timedelta_result = timedelta(hours=time_dif)

                    # Subtract the timedelta object from test1_datetime
                    datetime_result = datetime_import + timedelta_result

                    # Replace the value
                    row[0] = datetime_result

                    # Write the modified row to the new file
                    writer.writerow(row)

def insert_sort_balances(db_path):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Open the file
    with open('neofly_sync_imports/all_in_one.csv', newline='') as file:
        # Create a CSV reader
        reader = csv.DictReader(file, fieldnames=["date", "description", "incomes", "expenses", "owner"])
        
        # Loop through the rows
        for row in reader:
            # Data get the row content
            data = (row['date'], row['description'], row['incomes'], row['expenses'], row['owner'])

            # Retrieve the current information from the "balances" table
            c.execute("INSERT INTO balances (date, description, incomes, expenses, owner) VALUES (?, ?, ?, ?, ?)", data)
            
    # Commit the changes
    conn.commit()

    # Next step is to update the balances to sort it by date again

    # Sort the table by the 'date' column
    c.execute("SELECT * FROM balances ORDER BY date")

    # Fetch all the results
    results = c.fetchall()

    # update all rows
    i = 1
    for row in results:
        c.execute("UPDATE balances SET date = ?, description = ?, incomes = ?, expenses = ?, owner = ? WHERE rowid = ?", (row[0],row[1],row[2],row[3],row[4], i))
        i = i + 1

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()

def update_cash_in_career(db_path, user_export):
    # Open the file
    with open('neofly_sync_imports/all_in_one.csv', newline='') as file:
        # Create a CSV reader
        reader = csv.DictReader(file, fieldnames=["date", "description", "incomes", "expenses", "owner"])
        
        # Declare variable
        imported_cash_difference = 0

        # Loop through the rows
        for row in reader:
            incomes = int(row['incomes'])
            expenses = int(row['expenses'])
            imported_cash_difference = imported_cash_difference + incomes - expenses

    # Connect to the database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Get current cash value
    c.execute("SELECT cash FROM career")

    # Fetch all the results
    current_cash = int(c.fetchone()[0])

    # Get the new value
    updated_cash = current_cash + imported_cash_difference

    # Update cash with new value
    c.execute("UPDATE career SET cash = ? WHERE name = ?", (updated_cash, user_export))

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()

# ____________________________________________________________________________________________________________________________



# We don't want to execute if NeoFly.exe is running
if is_running("NeoFly.exe"):
    print("NeoFly.exe is running. Close Neofly before trying to synchronise.")
else:
    print("NeoFly.exe is not running.")


    # Initalisation variables .ini

    ini = configparser.ConfigParser()
    ini.read('neofly_sync.ini')

    user_export = ini.get('config', 'user_export')
    export_UTC = ini.get('config', 'export_UTC')
    user_import = ini.get('config', 'user_import')
    import_UTC = ini.get('config', 'import_UTC')
    repo = ini.get('config', 'repo')
    access_token = ini.get('config', 'access_token')
    date_export = ini.get('config', 'date_export')
    date_import = ini.get('config', 'date_import')
    db_path = ini.get('config', 'db_path')

    # Convert Timezone value to Int
    export_UTC = int(export_UTC)
    import_UTC  = int(import_UTC)


    # ____________________________________________________________________________________________________________________________


    new_entries = check_changes(db_path, date_export)

    if new_entries != 'EMPTY':
        sort_and_save_csv('temp.csv')
        name_of_exportcsv = rename_csv(db_path, 'temp.csv')
        export_to_github(access_token, name_of_exportcsv)

        ini['config']['date_export'] = get_last_row_col_value(name_of_exportcsv)

        with open('neofly_sync.ini', 'w') as configfile:
            ini.write(configfile)

    # Check if there is new files to import from github and download them, return 'NOT_EMPTY' if it was found
    result_found = import_from_github(access_token, repo, user_import, date_import)

    if result_found == 'NOT_EMPTY':
        # modify the content of the imported csv ( description, timezone ) and put it in a new all_in_one.csv
        modify_import_content(user_import, export_UTC, import_UTC)

        # insert and sort the new entries in 'balances'
        insert_sort_balances(db_path)

        # update cash in career
        update_cash_in_career(db_path, user_export)

        # update .ini with new import value
        ini['config']['date_import'] = get_last_row_col_value('neofly_sync_imports/all_in_one.csv')
        with open('neofly_sync.ini', 'w') as configfile:
            ini.write(configfile)

        print('Database updated.')
    else:
        print('Nothing new to import.')
