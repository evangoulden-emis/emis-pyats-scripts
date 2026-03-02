from github import Github
from github import Auth
import os
from github.InputGitTreeElement import InputGitTreeElement
import time


def push_to_github(backup_dir='backups'):
    # Configuration
    ACCESS_TOKEN = os.environ.get('GH_PAT-TOKEN')
    REPO_NAME = "evangoulden-emis/testing_pygithub"
    BASE_BRANCH = "main"
    LOCAL_BACKUP_PATH = "./backups"
    NEW_BRANCH_NAME = f"backup-{int(time.time())}"

    auth = Auth.Token(ACCESS_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(REPO_NAME)
    base_sha = repo.get_git_ref(f"heads/{BASE_BRANCH}").object.sha
    repo.create_git_ref(ref=f"refs/heads/{NEW_BRANCH_NAME}", sha=base_sha)

    # 2. Upload Files and Create Tree
    element_list = []
    for root, _, files in os.walk(LOCAL_BACKUP_PATH):
        for file in files:
            path = os.path.join(root, file)
            remote = os.path.relpath(path, LOCAL_BACKUP_PATH)
            with open(path, "rb") as f:
                blob = repo.create_git_blob(f.read().decode("utf-8"), "utf-8")
            element_list.append(InputGitTreeElement(path=remote, mode='100644', type='blob', sha=blob.sha))
    # 3. Commit and PR
    tree = repo.create_git_tree(element_list, repo.get_git_tree(sha=base_sha))
    commit = repo.create_git_commit(f"Backup: {NEW_BRANCH_NAME}", tree, [repo.get_git_commit(base_sha)])
    repo.get_git_ref(f"heads/{NEW_BRANCH_NAME}").edit(sha=commit.sha)


if __name__ == '__main__':
    push_to_github()