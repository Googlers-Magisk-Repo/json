import sys
import json
import os
from github import Github
from datetime import datetime

# Configuration
REPO_NAME = os.getenv('REPO_NAME')
REPO_TITLE = os.getenv('REPO_TITLE')
REPO_WEBSITE = os.getenv('REPO_WEBSITE')
REPO_SUPPORT = os.getenv('REPO_SUPPORT')
REPO_DONATE = os.getenv('REPO_DONATE')
REPO_SUBMIT_MODULE = os.getenv('REPO_SUBMIT_MODULE')

# Initialize the GitHub objects
g = Github(os.environ['GIT_TOKEN'])
user = g.get_user(REPO_NAME)
repos = user.get_repos()

# Skeleton for the repository
meta = {
    # Fetch the last repository update
    "last_update": int(user.updated_at.timestamp() * 1000),
    "name": REPO_TITLE,
    "website": REPO_WEBSITE,
    "support": REPO_SUPPORT,
    "donate": REPO_DONATE,
    "submitModule": REPO_SUBMIT_MODULE,
    "modules": []
}

def convert_value(value):
    # Convert boolean values
    if value.lower() == 'true':
        return True
    elif value.lower() == 'false':
        return False
    # Convert integer values
    try:
        return int(value)
    except ValueError:
        # Convert float values
        try:
            return float(value)
        except ValueError:
            # Keep string values as is
            return value

# Iterate over all public repositories
for repo in repos:
    # It is possible that module.prop does not exist (meta repo)
    try:
        moduleprop = repo.get_contents("module.prop")
        moduleprop_raw = moduleprop.decoded_content.decode("UTF-8")

        properties = {}
        for line in moduleprop_raw.splitlines():
            if "=" not in line:
                continue
            lhs, rhs = line.split("=", 1)
            properties.update({
               lhs: convert_value(rhs)
            })

        # Get the last update timestamp of the module.prop file
        last_update_timestamp = moduleprop.last_modified

        # Convert the string to a datetime object
        last_update_datetime = datetime.strptime(last_update_timestamp, '%a, %d %b %Y %H:%M:%S %Z')

        # Get the timestamp of the last update
        last_update_timestamp = datetime.timestamp(last_update_datetime)

        module = {
            "id": properties.get("id"),
            "last_update": int(last_update_timestamp * 1000),
            "prop_url": f"https://raw.githubusercontent.com/{repo.full_name}/{repo.default_branch}/module.prop",
            "zip_url": f"https://github.com/{repo.full_name}/archive/{repo.default_branch}.zip",
            "notes_url": f"https://raw.githubusercontent.com/{repo.full_name}/{repo.default_branch}/README.md",
            "stars": int(repo.stargazers_count),
            "props": properties,
        }

        # Handle file to ignore the index process for the current module
        if properties.get("noIndex"):
            continue
        else:
            # Append to skeleton
            meta.get("modules").append(module)

    except:
        continue

# Return our final skeleton
print(json.dumps(meta, indent=4))
