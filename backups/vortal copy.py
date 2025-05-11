import json
import datetime
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os

MY_ID = "b90412dca0f08d6b012eca44c4a09304"
TIMETABLE_A = r"C:\Users\delay\OneDrive\Documents\Code & Programs\Visual Studio Code\Python\The CT Project\Modules\Timetable\Timetables\Week A timetable.htm"
TIMETABLE_B = r"C:\Users\delay\OneDrive\Documents\Code & Programs\Visual Studio Code\Python\The CT Project\Modules\Timetable\Timetables\Week B Timetable.htm"
CACHE_PATH = r"cache"
FULL_PATH = r"C:\Users\delay\OneDrive\Documents\Code & Programs\Visual Studio Code\TeleBear"

class portalAgent():
    def __init__(self, username, password, save_path, user, waitTimeout = 5):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument("log-level=3")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://portal.vjc.edu.sg/")  # Replace with your target URL

        # Login using given information
        self.driver.find_element(By.XPATH, "/html/body/div[1]/form[4]/fieldset/section[2]/label[2]/input").send_keys(username)
        self.driver.find_element(By.XPATH, "/html/body/div[1]/form[4]/fieldset/section[3]/label[2]/input").send_keys(password)
        self.driver.find_element(By.XPATH, "/html/body/div[1]/form[4]/footer[1]/button").click()

        #Check for status of login
        try: 
            WebDriverWait(self.driver, waitTimeout).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/aside/div/span/a/img"))  # Replace with real ID
            )
            
            print("[SEL] Login Success")

        except selenium.common.exceptions.TimeoutException:
            try: 
                error_element = self.driver.find_element(By.XPATH, "/html/body/div[1]/form[4]/fieldset/div")
                
                if error_element:
                    print("[SEL] Incorrect Portal Login Information, please try again. ")
                    quit() #replace
                
                else:
                    print("[SEL] Unexpected Error, quitting. ")
                    quit()
                    
            except selenium.common.exceptions.NoSuchElementException:
                print("[SEL] Incorrect Portal Login Information, please try again. ")
                quit()
                
        self.username = username
        self.user = user

    def getTimetable(self, id, startdate):#"2025-04-27"
        """_summary_

        Args:
            id (__str__): depending on userid. need to investigate
            startdate (__list?__): _description_

        Returns:
            _type_: returns path of saved timetable file
        """
        
        url = f"https://portal.vjc.edu.sg/.report?id={id}&startdate={startdate}T16:00:00Z"
        
        # set cookies from selenium on requests
        session = requests.Session()
        for cookie in self.driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])

        headers = {
            "User-Agent": self.driver.execute_script("return navigator.userAgent;")
        }
    
        # get timetable
        response = session.get(url = url, headers=headers)
        print(f"[REQ] RESP {response.status_code} | URL {response.url}") #timetable stored as response.text

        try: 
            os.mkdir(f"{CACHE_PATH}\{self.user}") #see if user specific folder is found
            print(f"[CACHE] New User {self.user}")
            
        except FileExistsError:
            print(f"[CACHE] Existing User {self.user}")
        
        except PermissionError:
            print(f"[CACHE] Access Denied.")
            quit() #STOP PROGRAM, or return error to telegram
        
        filepath = f"{FULL_PATH}\{CACHE_PATH}\{self.user}\\tt_{startdate}.txt" #always overwrite the current timetable
        
        if "Access Denied" in response.text:
            print("[REQ] Access Denied")
            quit()
        
        with open(filepath, "w") as file:
            file.write(response.text)
            
        return filepath

class teleTimetable():
    def __init__(self, userid):
        pass #load user variables 
        # show_h1, show_prog, selected lessons (etc)

class timetable():
    def __init__(self):
        # here must load preferences !! 
        # timetable object will be user specific
        self.show_h1 = False
        self.show_prog = True
        self.starting_time = "7:40"

        self.lessons = { #does not include Econs Program #if there are lessons that program does not understand, flag #check for H1
            "PW" : "Project Work",
            "EC" : "Economics",
            "PE" : "PE",
            "MA" : "Math", 
            "GP" : "General Paper",
            "CH" : "Chemistry",
            "CP" : "Computing",
            "CT" : 'Civics',
            "CONNECT 2" : 'Civics'
            #"ASSEMBLY" : "Assembly"
        }

    def lesson_start(self, lesson_data, time="7:40"): #time can be passed as a list or as a string
        starting_time = self.starting_time
        lessons = self.lessons
        minutes = (int(lesson_data.get('fromslot')) - 1)*20
        repetitions = int(minutes/20)
        repetitions = repetitions * "-"
        
        if type(time) != list: 
            time = time.split(":") #splits the time into a list
        
        for repetition in repetitions:
            time[1] = int(time[1]) + 20 #add 20 to minutes
            if int(time[1]) == 60:
                time[1] = "00"
                time[0] = int(time[0]) + 1
                
        time[0] = int(time[0])
        time[1] = int(time[1])
        
        return time

    def lesson_end(self, lesson_data, time="7:40"): #time can be passed as a list or as a string
        starting_time = self.starting_time
        lessons = self.lessons
        minutes = (int(lesson_data.get('toslot')))*20
        repetitions = int(minutes/20)
        repetitions = repetitions * "-"
        
        if type(time) != list: 
            time = time.split(":") #splits the time into a list
        
        for repetition in repetitions:
            time[1] = int(time[1]) + 20 #add 20 to minutes
            if int(time[1]) == 60:
                time[1] = "00"
                time[0] = int(time[0]) + 1
                
        time[0] = int(time[0])
        time[1] = int(time[1])
        
        return time

    def dates(self):
        path = ""
        with open(path, "r") as jsfile:
            #print(jsfile.readlines())
            list = jsfile.readlines()
            #print(list[34])
            s_raw = str(list[34])
            s_raw = s_raw.split("var data = ")[1]
            s_raw = s_raw.split(";\n")[0]
            #print(s_raw)
            p_raw = json.loads(s_raw)

    def timetable(self, path, day):
        """_summary_

        Args:
            path (str): path to saved timetable (ab is delocalised)
            day (str): monday, tuesday...

        Returns:
            list: lessons (dict) in a list
        """
        
        lessons = self.lessons  
        
        with open(path, "r") as jsfile:
            #print(jsfile.readlines())
            list = jsfile.readlines()

            i = None
            for line in list:
                if "var data" in line:
                    i = list.index(line)
                    #print(f"[TT] Data found at index {i}")

            if i == None:
                print("[TT] Something Went Wrong. Var Data Index Error. :/")
                quit()
            
            s_raw = str(list[68]) #might have to code something to read lines and find when var data starts
            s_raw = s_raw.split("var data = ")[1]
            s_raw = s_raw.split(";\n")[0]
            #print(s_raw)
            p_raw = json.loads(s_raw)

        weekly_schedule = p_raw.get("lessons_cc07d65f28866a930d803e10c79ecf67") #weekly schedule
        processed_lessons = []
        processed_weekly_lessons = {}

        n_day = 0
        for daily_schedule in weekly_schedule:
            n_day += 1
            daily_schedule = daily_schedule.get("rows")[0].get("lessons") #list of lessons
            
            for lesson in daily_schedule:
                start_time = self.lesson_start(lesson)
                end_time = self.lesson_end(lesson)
                
                if start_time[1] == 0:
                    start_time[1] = "00"
                    
                if end_time[1] == 0:
                    end_time[1] = "00"
                    
                if len(str(start_time[0])) == 1:
                    start_time[0] = f"0{start_time[0]}"
                    
                if len(str(end_time[0])) == 1:
                    end_time[0] = f"0{end_time[0]}"
                
                name = lesson.get("line1")        
                location = lesson.get("line2")
                
                for lesson in lessons:      
                    if name.find(f"{lesson}") >= 0 and (name.find("PROG") == -1 or self.show_prog == True) and (name.find("H1") == -1 or self.show_h1 == True) and name.find("BREAK") == -1:
                        if name.find("PROG") >= 0:            
                            name = f"{lessons.get(lesson)} Program"
                            
                        else:
                            name = lessons.get(lesson)
                                                
                        write = {
                            "name" : name,
                            "start" : start_time,
                            "end" : end_time,
                            "location" : location
                        }
                        
                        processed_lessons.append(write)

            if n_day == 1:
                processed_weekly_lessons["monday"] = processed_lessons
            elif n_day == 2:
                processed_weekly_lessons["tuesday"] = processed_lessons
            elif n_day == 3:
                processed_weekly_lessons["wednesday"] = processed_lessons
            elif n_day == 4:
                processed_weekly_lessons["thursday"] = processed_lessons
            elif n_day == 5:
                processed_weekly_lessons["friday"] = processed_lessons
            processed_lessons = []
            
        for lesson in processed_weekly_lessons.get(day):
            pass
            #print(lesson)
            
        return processed_weekly_lessons.get(day)


    def timetable_old(self, ab, day):
        """_summary_

        Args:
            ab (str): week type: a / b
            day (str): monday, tuesday...

        Returns:
            list: lessons (dict) in a list
        """
        
        starting_time = self.starting_time
        lessons = self.lessons  
        
        if ab.lower() == "a":
            path = TIMETABLE_A
            
        else:
            path = TIMETABLE_B
        
        with open(path, "r") as jsfile:
            #print(jsfile.readlines())
            list = jsfile.readlines()
            #print(list[34])
            s_raw = str(list[34])
            s_raw = s_raw.split("var data = ")[1]
            s_raw = s_raw.split(";\n")[0]
            #print(s_raw)
            p_raw = json.loads(s_raw)
            
        #print(p_raw)

        weekly_schedule = p_raw.get("lessons_cc07d65f28866a930d803e10c79ecf67") #weekly schedule
        processed_lessons = []
        processed_weekly_lessons = {}

        n_day = 0
        for daily_schedule in weekly_schedule:
            n_day += 1
            daily_schedule = daily_schedule.get("rows")[0].get("lessons") #list of lessons
            
            for lesson in daily_schedule:
                start_time = self.lesson_start(lesson)
                end_time = self.lesson_end(lesson)
                
                if start_time[1] == 0:
                    start_time[1] = "00"
                    
                if end_time[1] == 0:
                    end_time[1] = "00"
                
                name = lesson.get("line1")        
                location = lesson.get("line2")
                
                for lesson in lessons:      
                    if name.find(f"{lesson}") >= 0 and (name.find("PROG") == -1 or self.show_prog == True) and (name.find("H1") == -1 or self.show_h1 == True) and name.find("BREAK") == -1:
                        if name.find("PROG") >= 0:            
                            name = f"{lessons.get(lesson)} Program"
                            
                        else:
                            name = lessons.get(lesson)
                                                
                        write = {
                            "name" : name,
                            "start" : start_time,
                            "end" : end_time,
                            "location" : location
                        }
                        
                        processed_lessons.append(write)

            if n_day == 1:
                processed_weekly_lessons["monday"] = processed_lessons
            elif n_day == 2:
                processed_weekly_lessons["tuesday"] = processed_lessons
            elif n_day == 3:
                processed_weekly_lessons["wednesday"] = processed_lessons
            elif n_day == 4:
                processed_weekly_lessons["thursday"] = processed_lessons
            elif n_day == 5:
                processed_weekly_lessons["friday"] = processed_lessons
            processed_lessons = []
            
        for lesson in processed_weekly_lessons.get(day):
            print(lesson)
            
        return processed_weekly_lessons.get(day)

    #Functions are discontinued
    def a_timetable(self, day):   
        starting_time = self.starting_time
        lessons = self.lessons  
        
        with open(TIMETABLE_A, "r") as jsfile:
            #print(jsfile.readlines())
            list = jsfile.readlines()
            #print(list[34])
            s_raw = str(list[34])
            s_raw = s_raw.split("var data = ")[1]
            s_raw = s_raw.split(";\n")[0]
            #print(s_raw)
            p_raw = json.loads(s_raw)

        weekly_schedule = p_raw.get("lessons_cc07d65f28866a930d803e10c79ecf67")[0].get("rows")
        monday = p_raw.get("lessons_cc07d65f28866a930d803e10c79ecf67")[0].get("rows")[0].get("lessons")

        weekly_schedule = p_raw.get("lessons_cc07d65f28866a930d803e10c79ecf67") #weekly schedule
        processed_lessons = []
        processed_weekly_lessons = {}

        n_day = 0
        for daily_schedule in weekly_schedule:
            n_day += 1
            daily_schedule = daily_schedule.get("rows")[0].get("lessons") #list of lessons
            
            for lesson in daily_schedule:
                start_time = self.lesson_start(lesson)
                end_time = self.lesson_end(lesson)
                
                if start_time[1] == 0:
                    start_time[1] = "00"
                    
                if end_time[1] == 0:
                    end_time[1] = "00"
                
                name = lesson.get("line1")        
                location = lesson.get("line2")
                
                for lesson in lessons:      
                    if name.find(f"{lesson}") >= 0 and (name.find("PROG") == -1 or self.show_prog == True) and (name.find("H1") == -1 or self.show_h1 == True):
                        if name.find("PROG") >= 0:            
                            name = f"{lessons.get(lesson)} Program"
                            
                        else:
                            name = lessons.get(lesson)
                                                
                        write = {
                            "name" : name,
                            "start" : start_time,
                            "end" : end_time,
                            "location" : location
                        }
                        
                        processed_lessons.append(write)
                        


            if n_day == 1:
                processed_weekly_lessons["monday"] = processed_lessons
            elif n_day == 2:
                processed_weekly_lessons["tuesday"] = processed_lessons
            elif n_day == 3:
                processed_weekly_lessons["wednesday"] = processed_lessons
            elif n_day == 4:
                processed_weekly_lessons["thursday"] = processed_lessons
            elif n_day == 5:
                processed_weekly_lessons["friday"] = processed_lessons
            processed_lessons = []
            
        for lesson in processed_weekly_lessons.get(day):
            print(lesson)
            
        return processed_weekly_lessons.get(day)

    def b_timetable(self, day):   
        starting_time = self.starting_time
        lessons = self.lessons  
        
        with open(TIMETABLE_B, "r") as jsfile:
            #print(jsfile.readlines())
            list = jsfile.readlines()
            #print(list[34])
            s_raw = str(list[34])
            s_raw = s_raw.split("var data = ")[1]
            s_raw = s_raw.split(";\n")[0]
            #print(s_raw)
            p_raw = json.loads(s_raw)

        weekly_schedule = p_raw.get("lessons_cc07d65f28866a930d803e10c79ecf67")[0].get("rows")
        monday = p_raw.get("lessons_cc07d65f28866a930d803e10c79ecf67")[0].get("rows")[0].get("lessons")

        weekly_schedule = p_raw.get("lessons_cc07d65f28866a930d803e10c79ecf67") #weekly schedule
        processed_lessons = []
        processed_weekly_lessons = {}

        n_day = 0
        for daily_schedule in weekly_schedule:
            n_day += 1
            daily_schedule = daily_schedule.get("rows")[0].get("lessons") #list of lessons
            
            for lesson in daily_schedule:
                start_time = self.lesson_start(lesson)
                end_time = self.lesson_end(lesson)
                
                if start_time[1] == 0:
                    start_time[1] = "00"
                    
                if end_time[1] == 0:
                    end_time[1] = "00"
                
                name = lesson.get("line1")        
                location = lesson.get("line2")
                
                for lesson in lessons:      
                    if name.find(f"{lesson}") >= 0 and (name.find("PROG") == -1 or self.show_prog == True) and (name.find("H1") == -1 or self.show_h1 == True) and name.find("BREAK") == -1:
                        if name.find("PROG") >= 0:            
                            name = f"{lessons.get(lesson)} Program"
                            
                        else:
                            name = lessons.get(lesson)
                                                
                        write = {
                            "name" : name,
                            "start" : start_time,
                            "end" : end_time,
                            "location" : location
                        }
                        
                        processed_lessons.append(write)
                        

            if n_day == 1:
                processed_weekly_lessons["monday"] = processed_lessons
            elif n_day == 2:
                processed_weekly_lessons["tuesday"] = processed_lessons
            elif n_day == 3:
                processed_weekly_lessons["wednesday"] = processed_lessons
            elif n_day == 4:
                processed_weekly_lessons["thursday"] = processed_lessons
            elif n_day == 5:
                processed_weekly_lessons["friday"] = processed_lessons
            processed_lessons = []
            
        for lesson in processed_weekly_lessons.get(day):
            #print(lesson)
            pass
            
        return processed_weekly_lessons.get(day)


# username, password = ["jaydsoh@gmail.com", "pYTHON101"]
# save_path = r"C:\Users\delay\OneDrive\Documents\Code & Programs\Visual Studio Code\Python\VJC Calendar\cache"
# agent = portalAgent(username, password, save_path)

# agent.getTimetable("s", "")