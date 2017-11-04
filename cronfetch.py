import os
import requests

requests.get(str(os.environ.get('appUrl')+'/fetchMenuItems'+str(os.environ.get('botToken'))))