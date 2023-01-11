from github import Github

#need pip install PyGithub


access_token = ""

# Authenticate with GitHub
g = Github(access_token)

# Get the repository
repo = g.get_repo("elyetis/neofly_syncro")

# Get the .db file
db_file = repo.get_contents("neofly.csv")

# Download the .db file
file_content = db_file.decoded_content

# Save the file
with open("neofly_import.csv", "wb") as f:
    f.write(file_content)