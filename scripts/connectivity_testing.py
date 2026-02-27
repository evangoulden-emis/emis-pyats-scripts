from pyats.topology import loader


def check_connectivity(testbed_file):
    # Load your testbed
    testbed = loader.load(testbed_file)

    print(f"--- Starting Connectivity Check for Testbed: {testbed.name} ---")
    success = list()
    failure = list()
    for device_name, device in testbed.devices.items():
        try:

            # Individual connection call
            device.connect(log_stdout=False)
            success.append(device_name)

            device.disconnect()
        except Exception as e:
            failure.append(device_name)

    print("--- Connectivity Check Complete ---")

    for device in success:
        print(f"�� Successfully Connected to {device}")

    for device in failure:
        print(f"❌ Failed to connect to {device}")


if __name__ == "__main__":
    # Ensure your testbed file is named 'testbed.yaml' or update the path below
    check_connectivity('testbed/emis-testbed.yaml')
