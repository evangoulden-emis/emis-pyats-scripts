from pyats.topology import loader

def check_connectivity(testbed_file):
    # Load your testbed
    testbed = loader.load('testbed.yaml')

    print(f"--- Starting Connectivity Check for Testbed: {testbed.name} ---")

    for device_name, device in testbed.devices.items():
        try:
            print(f"Connecting to {device_name}...")
            # Individual connection call
            device.connect()
            print(f"Successfully connected to {device_name}")

            # Optional: Run a command to verify
            # print(device.execute('show version'))

            device.disconnect()
        except Exception as e:
            print(f"Failed to connect to {device_name}: {e}")

    print("--- Connectivity Check Complete ---")

if __name__ == "__main__":
    # Ensure your testbed file is named 'testbed.yaml' or update the path below
    check_connectivity('testbed/emis-testbed.yaml')
