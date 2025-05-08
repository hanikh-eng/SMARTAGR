import paramiko

def function_call():
    # Raspberry Pi connection details
    RPI_IP = '192.168.16.54'
    RPI_USER = 'marko'
    RPI_PASSWORD = '03126809lpn'

    client = paramiko.SSHClient()

    # Automatically add the host key if it's missing
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to Raspberry Pi via SSH
        client.connect(RPI_IP, username=RPI_USER, password=RPI_PASSWORD)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close SSH connection
        client.close()
