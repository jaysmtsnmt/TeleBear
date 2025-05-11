# must check for data
# must be able to push data

import os
import pickle
from time import sleep
import api_gateway
import threading

from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request

FULL_PATH = r"C:\Users\delay\OneDrive\Documents\Code & Programs\Visual Studio Code\TeleBear"
CACHEPATH = fr"{FULL_PATH}\cache"
CREDSPATH = fr"{FULL_PATH}\dependencies\credentials"
SCOPES = ['https://www.googleapis.com/auth/calendar']

default_lessons = { #does not include Econs Program #if there are lessons that program does not understand, flag #check for H1
    "PW" : "Project Work",
    "EC" : "Economics",
    "PE" : "PE",
    "MA" : "Math", 
    "GP" : "General Paper",
    "CH" : "Chemistry",
    "CP" : "Computing",
    "CT" : 'Civics',
    "CONNECT 2" : 'Connect 2',
    "1TSD" : "TSD",
    "CL" : "Chinese", 
    "PH" : "Physics"
    #"ASSEMBLY" : "Assembly"
}

default_preferences = {
    'show_h1' : False,
    'show_prog' : True, 
    'lessons' : default_lessons
}

auth_timeout = 300
t1 = threading.Thread(target=api_gateway.host)
t1.start()

sleep(1)

class User():
    def __init__(self, user):
        self.user = user
        self.redirect_uri = "https://9a6c-119-234-64-53.ngrok-free.app"

    def clearCache(self): #unique id
        path = fr"{CACHEPATH}\{self.user}"
        
        if os.path.exists(path):
            os.remove(path) 
            print(f"[DATA] Cache Cleared. | id: {self.user} ")
            return True
        
        else:
            print(f"[DATA] Cache does not exist. | id: {self.user} ")
            return False
        
    def isExistingUser(self):
        """Checks for existing files in cache directory under userid. 
        
        Returns:
            tuple: exists, google_authenticated, portal_authenticated, tt_preferences_loaded
        """
        path = fr"{CACHEPATH}\{self.user}"
        
        exists = False
        google_authenticated = False
        portal_authenticated = False
        tt_preferences_loaded = False
        
        if os.path.exists(path):
            print(f'[DATA] user_{self.user} is an existing user. ')
            exists = True
            
            if os.path.exists(f"{path}\gapi.pickle"):
                google_authenticated = True
            
            if os.path.exists(f"{path}\login.pickle"):
                portal_authenticated = True
                
            if os.path.exists(f"{path}\preference_tt.pickle"):
                tt_preferences_loaded = True
                
        print(f"[DATA] user_{self.user} | Exists: {exists} | G: {google_authenticated} | P: {portal_authenticated} | TT: {tt_preferences_loaded}")
        
        return exists, google_authenticated, portal_authenticated, tt_preferences_loaded
        

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
        
        if os.path.exists(f"{CACHEPATH}\{self.user}") == False:
            os.makedirs(f"{CACHEPATH}\{self.user}")
        
        with open(path, "wb") as file:
            pickle.dump(data, file)    
    
    def getVortalInformation(self):
        """Gets Vortal Information.
        
        Returns:
            dict/Nonetype: returns data, unless user information does not exist
        """
        
        path = fr"{CACHEPATH}\{self.user}\login.pickle"
        if os.path.exists(path):
            with open(path, "rb") as file:
                data = pickle.load(file)
            
            return data
                
        else:
            print(f"[DATA] User {self.user} information does not exist.")
            return None
    
    def checkVortalLoginCredentials(self):
        #get and then check Vortal Login Credentials
        pass
    
    def updateTimetablePreferences(self, show_h1 = default_preferences.get('show_h1'), show_prog = default_preferences.get('show_prog'), lessons = {}):
        """Updates Timetable Preference for user. If no arguements are passed, it loads defaults

        Args:
            user (str): userid
            show_h1 (bool): Defaults to False
            show_prog (bool): Defaults to False
            exclude (list): Defaults to [].
            lessons (list): MUST GIVE FULL LIST OF LESSONS THAT WANT TO BE INCLUDED
        """
        global default_lessons
        final = lessons
            
        data = {
            'show_h1' : show_h1,
            'show_prog': show_prog,
            'lessons' : final
        }
        
        print(f"[DEBUG] {data}")

        if os.path.exists(f"{CACHEPATH}\{self.user}") == False:
            os.makedirs(f"{CACHEPATH}\{self.user}")
        
        path = fr"{CACHEPATH}\{self.user}\preference_tt.pickle"
        
        with open(path, "wb") as file:
            print(f"[DATA] Updating timetable preferences for {self.user}")
            pickle.dump(data, file)
        
        return True
        
    def getTimetablePreferences(self):
        global default_preferences
        path = fr"{CACHEPATH}\{self.user}\preference_tt.pickle"
        
        if os.path.exists(path) == False:
            print(f"[DATA] Timetable Preferences for {self.user} does not exist. Returning Empty Dictionary.")
            
            empty = {
                'show_h1' : False,
                'show_prog' : False,
                'lessons' : {}
            }
            
            return empty

        else:
            print(f"[DATA] Timetable Preferences for {self.user} does exist. Loading preferences.")

            with open(path, "rb") as file:
                data = pickle.load(file)
                
            return data

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
    
    def getGoogleAPIAuthURL(self):
        flow = Flow.from_client_secrets_file(fr"{CREDSPATH}\bearlander.json", SCOPES, redirect_uri=self.redirect_uri)
        auth_uri = f"{flow.authorization_url(prompt='consent', client_type='web')[0]}"
        
        return flow, auth_uri
        
    def completeGoogleAPIAuth(self, flow: Flow.from_client_secrets_file):
        seconds = 0
        authed = False
        TOKEN_PATH = fr"{CACHEPATH}\{self.user}\gapi.pickle"

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
            return "timeout"
        
        else:
            print("[DATA] Successful saving of authentication information.")
            return "success"

if __name__ == "__main__": 
    user_instance = User("jaydsoh")
    print(user_instance.getGoogleAPICredentials())
                
                    
                    
     