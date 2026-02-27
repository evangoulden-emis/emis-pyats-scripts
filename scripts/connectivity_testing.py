from pyats.topology import loader

def check_connectivity(testbed_file):
    # Load the testbed file
    testbed = loader.load(testbed_file)

    print(f"--- Starting Connectivity Check for Testbed: {testbed.name} ---")

    # Connect to all devices in parallel for efficiency
    # Note: Replace log_stdout=True with False if you want a cleaner output
    testbed.connect(log_stdout=False, learn_hostname=True)

    print("\n--- Summary ---")
    for device_name, device in testbed.devices.items():
        if device.connected:
            print(f"✅ {device_name:30} | Connected")
        else:
            print(f"❌ {device_name:30} | FAILED")

    # Disconnect from all devices
    testbed.disconnect()


if __name__ == "__main__":
    # Ensure your testbed file is named 'testbed.yaml' or update the path below
    check_connectivity('/Users/evan.goulden@optum.com/Library/CloudStorage/OneDrive-UHG/Code/pyATS/network-snapshot/testbed/emis-testbed.yaml')
