import subprocess
import urllib.request
import zipfile
import time
import os

# Download ngrok
print("Downloading ngrok...")
url = 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip'
zip_path = 'ngrok.zip'
urllib.request.urlretrieve(url, zip_path)

# Check if ngrok.exe already exists
if os.path.exists('ngrok.exe'):
    print("ngrok.exe already exists, skipping download and extraction.")
else:
    # Unzip
    print("Extracting ngrok...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall('.')
        print("ngrok extracted successfully.")
    except Exception as e:
        print(f"Error extracting ngrok: {e}")
        exit(1)

# Set authtoken
print("Setting ngrok auth token...")
try:
    subprocess.run(['ngrok.exe', 'authtoken', '34n1KmfhFgQtZPWp7lMIItPrh9P_2AxHxhZVvFBciLyayWARU'], check=True)
    print("Auth token set successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error setting auth token: {e}")
    exit(1)

# Kill any existing ngrok processes
print("Stopping any existing ngrok tunnels...")
try:
    subprocess.run(['taskkill', '/f', '/im', 'ngrok.exe'], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Existing ngrok processes stopped.")
except Exception as e:
    print(f"Error stopping existing ngrok: {e}")

# Start tunnel
print("Starting ngrok tunnel on port 5000...")
tunnel_process = subprocess.Popen(['ngrok.exe', 'http', '5000'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Wait a bit and read output
time.sleep(15)
output, error = tunnel_process.communicate()

if error:
    print("Error starting tunnel:", error)
else:
    print("Tunnel started.")
    print("Output:", output)
    # Parse the URL from output
    lines = output.split('\n')
    for line in lines:
        if 'https://' in line and 'ngrok' in line:
            print("Public URL:", line.strip())
            break
    else:
        print("Could not find public URL in output. Check ngrok dashboard.")

# Keep running
try:
    tunnel_process.wait()
except KeyboardInterrupt:
    tunnel_process.terminate()
    print("Tunnel closed")
