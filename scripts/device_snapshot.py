import os
import logging
import json
from datetime import datetime
from pyats.topology import loader

# Configure logging for the Cron job
log_filename = "/var/log/network_snapshots.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(log_filename), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def run_snapshot(testbed_file, folder_name):
    testbed = loader.load(testbed_file)
    base_dir = os.path.join('snapshots', folder_name)

    # Features to learn (State data)
    features = ['interface', 'platform', 'vlan', 'routing', 'ospf']

    for name, device in testbed.devices.items():
        if device.os not in ['iosxe', 'nxos']:
            continue

        try:
            device.connect(log_stdout=False, learn_hostname=True)
            device_dir = os.path.join(base_dir, name)
            os.makedirs(device_dir, exist_ok=True)

            for feature in features:
                try:
                    # Learn the state and save as JSON
                    state = device.learn(feature)
                    with open(os.path.join(device_dir, f"{feature}.json"), 'w') as f:
                        json.dump(state.to_dict(), f, indent=4)
                except Exception as e:
                    logger.warning(f"Feature {feature} failed on {name}: {e}")

            logger.info(f"✅ Snapshot complete: {name}")
            device.disconnect()
        except Exception as e:
            logger.error(f"❌ Connection failed: {name}. Error: {e}")


if __name__ == "__main__":
    # If run manually, you can pass 'golden' as an argument
    # Otherwise, it defaults to a timestamp for the Cron job
    tag = datetime.now().strftime("%Y-%m-%d")
    run_snapshot('testbed/emis-testbed.yaml', tag)
