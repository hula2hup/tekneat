import subprocess
import time
from pyngrok import ngrok

def run_flask_app():
    print("Starting Flask app...")
    flask_process = subprocess.Popen(['python', 'app.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return flask_process

if __name__ == "__main__":
    # Set ngrok auth token
    ngrok.set_auth_token('34n1KmfhFgQtZPWp7lMIItPrh9P_2AxHxhZVvFBciLyayWARU')

    flask_process = run_flask_app()
    time.sleep(5)  # Wait for Flask to start

    # Start ngrok tunnel
    print("Starting ngrok tunnel...")
    public_url = ngrok.connect(5000)
    print(f"Public URL: {public_url}")

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        ngrok.kill()
        flask_process.terminate()
