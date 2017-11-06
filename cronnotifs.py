import os
import requests

db = requests.get('https://api.myjson.com/bins/'+str(os.environ.get('myjsonId'))).json()

requests.get(db["config"]["appUrl"]+'/sendCurrentMenuAllUsers'+db["config"]["botToken"])