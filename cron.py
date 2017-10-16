import os
import requests

requests.get(str(os.environ.get('appUrl')+'/sendMenuAllUsers'+str(os.environ.get('botToken'))))