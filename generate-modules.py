import sys
import json
import os
from github import Github

# Configuration
REPO_NAME = "Googlers-Repo"
REPO_TITLE = "Googlers Magisk Repo"
REPO_WEBSITE = "https://dergoogler.com/repo"
REPO_SUPPORT = "https://t.me/The_Googler"
REPO_MMRL_OWNER = "FGPqXIzgATOwXrThZ7duE3AJnet2"
REPO_DONATE = None
REPO_SUBMIT_MODULE = None

# Skeleton for the repository
meta = {
    "last_update": "",
    "name": REPO_TITLE,
    "mmrlOwner": REPO_MMRL_OWNER,
    "website": REPO_WEBSITE,
    "support": REPO_SUPPORT,
    "donate": REPO_DONATE,
    "submitModule": REPO_SUBMIT_MODULE,
    "modules": []
}

# Initialize the GitHub objects
g = Github(os.environ['GIT_TOKEN'])
user = g.get_user(REPO_NAME)
repos = user.get_repos()

# Fetch the last repository update
meta["last_update"] = int(user.updated_at.timestamp() * 1000)

# Iterate over all public repositories
for repo in repos:
    # It is possible that module.prop does not exist (meta repo)
    try:
        # Parse module.prop into a python object
        moduleprop_raw = repo.get_contents(
            "module.prop").decoded_content.decode("UTF-8")

        moduleprop = {}
        for line in moduleprop_raw.splitlines():
            if "=" not in line:
                continue
            lhs, rhs = line.split("=", 1)
            moduleprop.update({
                lhs: rhs
            })

        module = {
            "id": moduleprop.get("id"),
            "last_update": int(repo.updated_at.timestamp() * 1000),
            "prop_url": f"https://raw.githubusercontent.com/{repo.full_name}/{repo.default_branch}/module.prop",
            "zip_url": f"https://github.com/{repo.full_name}/archive/{repo.default_branch}.zip",
            "notes_url": f"https://raw.githubusercontent.com/{repo.full_name}/{repo.default_branch}/README.md",
            # "stars": int(repo.stargazers_count),
            "props": moduleprop,
        }

        # Handle file to ignore the index process for the current module
        if moduleprop.get("gr_ignore") == "yes":
            continue
        else:
            # Append to skeleton
            meta["modules"].append(module)

    except:
        continue

# Return our final skeleton
print(json.dumps(meta, indent=4))
