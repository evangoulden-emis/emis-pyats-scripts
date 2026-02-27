import os
from datetime import datetime
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


def backup_network_configs(testbed_file, backup_dir='backups'):
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


if __name__ == "__main__":
    backup_network_configs('testbed/emis-testbed.yaml')
