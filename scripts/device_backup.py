from datetime import datetime
from github import Github
from github import Auth
import os
from github.InputGitTreeElement import InputGitTreeElement
import time
from pyats.topology import loader
import logging

log_filename = "backup_run.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_filename),  # Writes to this file
        logging.StreamHandler()  # Still shows in your terminal
    ]
)
logger = logging.getLogger(__name__)


def backup_network_configs(testbed_file, backup_dir: str ='/var/network-backups/'):
    # Create backup directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_backup_path = os.path.join(backup_dir, timestamp)
    os.makedirs(current_backup_path, exist_ok=True)

    # Load testbed
    testbed = loader.load(testbed_file)
    print(f"--- Starting Backups for {len(testbed.devices)} devices ---")

    for name, device in testbed.devices.items():
        try:
            print(f"Connecting to {name}...")
            device.connect(log_stdout=False, learn_hostname=True)

            # Determine backup command based on OS type
            if device.os in ['iosxe', 'nxos']:
                config = device.execute('show running-config')
            elif device.os == 'panos':
                # Palo Alto specific: exports the running config
                config = device.execute('show config running')
            else:
                print(f"⚠️ Skipping {name}: OS '{device.os}' backup not configured.")
                logger.info(f"Skipping {name}: OS '{device.os}' backup not configured.")
                device.disconnect()
                continue

            # Save to file
            file_path = os.path.join(current_backup_path, f"{name}.cfg")
            with open(file_path, 'w') as f:
                f.write(config)

            print(f"✅ Backup saved for {name}")
            logger.info(f"Backup saved for {name}")
            device.disconnect()

        except Exception as e:
            logger.error(f"Failed to backup {name}: {e}")
            print(f"❌ Failed to backup {name}: {e}")

    print(f"--- Local Backups completed for {len(testbed.devices)} devices ---")
    logger.info(f"Local Backups completed for {len(testbed.devices)} devices")

    push_to_github(backup_dir=backup_dir)
    print(f"--- Pushing to GitHub completed ---")


def push_to_github(backup_dir: str):
    # Configuration
    ACCESS_TOKEN = os.environ.get('GH_PAT-TOKEN')
    REPO_NAME = "emisgroup/network-device-backups"
    BASE_BRANCH = "main"
    NEW_BRANCH_NAME = f"backup-{int(time.time())}"

    auth = Auth.Token(ACCESS_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(REPO_NAME)
    base_sha = repo.get_git_ref(f"heads/{BASE_BRANCH}").object.sha
    repo.create_git_ref(ref=f"refs/heads/{NEW_BRANCH_NAME}", sha=base_sha)

    # 2. Upload Files and Create Tree
    element_list = []
    for root, _, files in os.walk(backup_dir):
        for file in files:
            path = os.path.join(root, file)
            remote = os.path.relpath(path, backup_dir)
            with open(path, "rb") as f:
                blob = repo.create_git_blob(f.read().decode("utf-8"), "utf-8")
            element_list.append(InputGitTreeElement(path=remote, mode='100644', type='blob', sha=blob.sha))

    # 3. Commit and PR
    tree = repo.create_git_tree(element_list, repo.get_git_tree(sha=base_sha))
    commit = repo.create_git_commit(f"Backup: {NEW_BRANCH_NAME}", tree, [repo.get_git_commit(base_sha)])
    repo.get_git_ref(f"heads/{NEW_BRANCH_NAME}").edit(sha=commit.sha)


if __name__ == "__main__":
    backup_network_configs('testbed/emis-testbed.yaml')
