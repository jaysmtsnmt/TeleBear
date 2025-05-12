from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import os.path
import pickle
from vortal import timetable as tt
from vortal import portalAgent
from user import User
from exceptions import *

FULL_PATH = r"C:\Users\delay\OneDrive\Documents\Code & Programs\Visual Studio Code\TeleBear"
CREDENTIALS_PATH = fr"{FULL_PATH}\dependencies\credentials"
cache = fr"{FULL_PATH}\cache"

SCOPES = ['https://www.googleapis.com/auth/calendar']

class bearlander():
    def __init__(self, user):
        print(f"[CAL] Instance Created | {user}")
        self.user_instance = User(user)
        
        try:
            creds = self.user_instance.getGoogleAPICredentials()
            
        except UserException.GoogleAPI.AuthenticationTimeout:
            raise UserException.GoogleAPI.AuthenticationTimeout("Authentication Timeout")

        self.service = build('calendar', 'v3', credentials=creds)
        calendars_data = self.service.calendarList().list().execute().get('items', [])
        calendars_name = [calendar["summary"] for calendar in calendars_data]
        
        print(f"[CAL] Number of existing calendars: {len(calendars_name)}")
        self.calendars_name = calendars_name
        self.calendars_data = calendars_data
        
        self.user = user

    def save_to_gcal(self, week=0): #week 0 = this week, week 1 = next week
        calendars_name = self.calendars_name
        calendars_data = self.calendars_data
        #self.user_instance.updateVortalInformation(["", ''], "25S64") 
        
        try:
            data = self.user_instance.getVortalInformation()
            
        except UserException.Cache.UserDoesNotExist:
            print(f"[CAL] User {self.user} needs to update Vortal Info!")
            raise UserException.Cache.UserDoesNotExist("User Does not Exist!")

        else:
            print(f"\n[CAL] Saving to calendar for {self.user}")
            class_ = data.get("class")
                
            if str(class_) not in calendars_name: #create a new calendar
                cal_class = {
                    'summary' : str(class_),
                    'timeZone' : 'Singapore'
                }
                
                cal_class = self.service.calendars().insert(body=cal_class).execute()
                cal_id = cal_class["id"]
                
                # print(f"[CAL] Calendar not found.")
                print(f"[CAL] {class_} created with id {cal_id}")
                
            else:
                i = calendars_name.index(str(class_))
                cal_id = calendars_data[i]["id"] #pull from saved data
                print(f"[CAL] Calendar {calendars_data[i]['summary']} found with id {cal_id}.")
            
            # check for existing events
            # from chatgpt - get the date of this week's monday
            date = datetime.now()
            t_monday = date-timedelta(days=date.weekday())
            t_monday = t_monday.date()
            
            l_monday = date-timedelta(days=(7-date.weekday()))
            l_monday = l_monday.date()
            
            #from chatgpt - get the date of next week's monday
            n_monday = date+timedelta(days=(7-date.weekday()))
            n_monday = n_monday.date()
            
            #print(f"{l_monday.isoformat()}T00:00:000Z")
            events = self.service.events().list(calendarId=cal_id, 
                                                timeMin=f"{t_monday.isoformat()}T00:00:00+08:00",
                                                maxResults=10, 
                                                singleEvents=True,
                                                orderBy="startTime").execute()
            
            events = events.get("items")
            
            if len(events) > 5 or week == 1:
                #print(f"[CAL] Saving to next week.") #save to next week instead
                start_date = n_monday
                
            else:
                start_date = t_monday
                
            print(f"[CAL] Events saved from {start_date} onwards.")
            
            try:
                agent = portalAgent(data.get("username"), data.get("password"), user=self.user)
                timetable = tt(self.user)
                path = agent.getTimetable(start_date)
                
            except Vortal.IncorrectLoginInformation:
                raise Vortal.IncorrectLoginInformation("Incorrect Vortal Login Information")
            
            except Vortal.PermissionError:
                raise Vortal.PermissionError("Cache Access Denied")
            
            except Vortal.Requests.AccessDenied:
                raise Vortal.Requests.AccessDenied("Requests Access Denied")
            
            except Vortal.Timetable.MissingLessonID:
                raise Vortal.Timetable.MissingLessonID("Missing Lesson ID")

            i = 0
            total = 0
            print(f"\n[CAL] Updating Calendar.")
            for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
                lessons = timetable.timetable(path, day)
                # print(f"[DEBUG] {lessons}")
                
                for lesson in lessons:
                    total += 1
                    #print(lesson)
                    if lesson.get('location') == '':
                        lesson['location'] = 'VJC'
                    
                    start_time = start_date + timedelta(days=i)
                    start_time = f"{start_time.isoformat()}T{lesson.get('start')[0]}:{lesson.get('start')[1]}:00+08:00"
                    end_time = start_date + timedelta(days=i)
                    end_time = f"{end_time.isoformat()}T{lesson.get('end')[0]}:{lesson.get('end')[1]}:00+08:00"
                    
                    name = (f'{lesson.get("name")}')
                    location = (f'{lesson.get("location")}')
                    
                    event = {
                        'summary': name,
                        'location': location,
                        'description': 'Sourced from Bearlander.',
                        'start': {
                            'dateTime': (start_time),
                        },
                        'end': {
                            'dateTime': (end_time),
                        },
                    }
                    
                    new_event = self.service.events().insert(calendarId=cal_id, body=event).execute()
                    print(f"[CAL] {new_event['summary']} | Start: {start_time} | End: {end_time} | id: {new_event['id']}")

                i+=1
                
            print(f"[CAL] {total} events updated for user {self.user}")
            
            return total
      
# if __name__ == "__main__":  
#     user_instance = User("jaydsoh")
#     # user_instance.updateVortalInformation(["", ""], "25S64")
#     # user_instance.updateTimetablePreferences()
    
#     bearlander_instance = bearlander('jaydsoh')
#     bearlander_instance.save_to_gcal()
