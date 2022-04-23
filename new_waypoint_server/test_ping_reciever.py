import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument("--ip", type=str, required=True)
args = parser.parse_args()

IP = args.ip
URL = f"http://{IP}:5000/pings/test_connection/"
response = requests.get(URL)
print(f"Response status code from {URL}:", response.status_code)