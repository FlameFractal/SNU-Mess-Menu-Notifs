import os
import requests

requests.get(str(os.environ.get('appUrl')+'/sendCurrentMenuAllUsers'+str(os.environ.get('botToken'))))