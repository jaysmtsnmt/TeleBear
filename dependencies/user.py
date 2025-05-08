# must check for data
# must be able to push data

import os
import pickle
from time import sleep
import api_gateway
import threading

from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.auth.credentials import Credentials

FULL_PATH = r"C:\Users\delay\OneDrive\Documents\Code & Programs\Visual Studio Code\TeleBear"
CACHEPATH = fr"{FULL_PATH}\cache"
CREDSPATH = fr"{FULL_PATH}\dependencies\credentials"
SCOPES = ['https://www.googleapis.com/auth/calendar']

auth_timeout = 90
t1 = threading.Thread(target=api_gateway.host)
t1.start()

sleep(1)

class User():
    def __init__(self, user):
        self.user = user
        self.redirect_uri = "https://570d-116-15-77-104.ngrok-free.app"

    def clearCache(self): #unique id
        path = fr"{CACHEPATH}\{self.user}"
        
        if os.path.exists(path):
            os.remove(path) 
            print(f"[DATA] Cache Cleared. | id: {self.user} ")
            return True
        
        else:
            print(f"[DATA] Cache does not exist. | id: {self.user} ")
            return False
        
    def updateVortalInformation(self, portal_credentials, user_class):
        """Update Vortal Information. 

        Args:
            portal_credentials (list): [username, password]
            user_class (str): VJC Class (format = {year}{stream}{number} (25S64))
        """
        username, password = portal_credentials
        
        data = {
            'username' : username,
            'password' : password,
            'class' : user_class
            
        }
        
        path = fr"{CACHEPATH}\{self.user}\login.pickle"
        
        with open(path, "wb") as file:
            pickle.dump(data, file)    
    
    def getVortalInformation(self, user):
        """Gets Vortal Information.

        Args:
            user (str): userid

        Returns:
            dict/Nonetype: returns data, unless user information does not exist
        """
        
        path = fr"{CACHEPATH}\{self.user}\login.pickle"
        if os.path.exists(path):
            with open(path, "rb") as file:
                data = pickle.load(file)
            
            return data
                
        else:
            print(f"[DATA] User {user} information does not exist.")
            return None
    
    def checkVortalLoginCredentials(self):
        #get and then check Vortal Login Credentials
        pass
    
    def getGoogleAPICredentials(self):
        """Checks for authentication & permissions. If not, generates a new API credential code and updates it under user cache.

        Returns:
            str: credentials to pass into Build
        """
        
        TOKEN_PATH = fr"{CACHEPATH}\{self.user}\gapi.pickle"
        
        creds = None
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, 'rb') as token:
                creds = pickle.load(token)
                
        if creds == None or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print(f"[DATA] Requesting a new token. | User {self.user}")
                creds.refresh(Request())
                
            else:
                print(f"[DATA] First time authentication & consent. | User {self.user}")
                flow = Flow.from_client_secrets_file(fr"{CREDSPATH}\bearlander.json", SCOPES, redirect_uri=self.redirect_uri)
                auth_uri = f"{flow.authorization_url(prompt='consent', client_type='web')[0]}"

                print(f"[DATA] {self.user} link authentication:")
                print(auth_uri + "\n")
            
                seconds = 0
                authed = False

                while (seconds) <= auth_timeout:
                    seconds += 0.5
                    sleep(0.5)
                    #check for auth uri
                    #print(f"\r[DEBUG] Waiting for cred: {api_gateway.auth_cred}")
                    if api_gateway.auth_cred != "":
                        code = api_gateway.auth_cred
                        print(f"[DATA] Auth Code: {api_gateway.auth_cred}")
                        flow.fetch_token(code=code)
                        creds = flow.credentials
                        api_gateway.clearAuthUri()
                        authed = True
                        
                        if os.path.exists(f"{CACHEPATH}/{self.user}") == False:
                            os.makedirs(f"{CACHEPATH}/{self.user}")
                        
                        with open(TOKEN_PATH, "wb") as token:
                            pickle.dump(creds, token)
                        
                        break
                    
                if not authed:
                    print("[DATA] Authentication Timeout.")
        
        return creds

if __name__ == "__main__": 
    user_instance = User("jaydsoh")
    print(user_instance.getGoogleAPICredentials())
                
                    
                    
     