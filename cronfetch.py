import os
import requests

db = requests.get('https://api.myjson.com/bins/'+str(os.environ.get('myjsonId'))).json()

requests.get(db["config"]["appUrl"]+'/fetchMenuItems'+db["config"]["botToken"])