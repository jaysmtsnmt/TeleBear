from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler
import threading as t
import asyncio
import user
from vortal import timetable as tt
from vortal import portalAgent
from bearlander import bearlander
import vortal
import os

TOKEN = '7727005144:AAH-xavS8MfnRfkm8zZyo_MDHYin1vgHOcQ'

#Files
LOGO_PATH = r"C:\Users\delay\OneDrive\Documents\Code & Programs\Visual Studio Code\TeleBear\dependencies\Formatting Files\2022 29 Farewell Assemnly.jpg"
FULL_PATH = r"C:\Users\delay\OneDrive\Documents\Code & Programs\Visual Studio Code\TeleBear"
CREDENTIALS_PATH = fr"{FULL_PATH}\dependencies\credentials"
cache = fr"{FULL_PATH}\cache"

timetable_message = '''
VJC Labot > Timetable

Please choose which week you want to check!
'''

help_message = '''
VJC Labot > Help


'''

timetable_help_message = '''
VJC Labot > Help > 
'''

h_called = t.Event()
handler_called = asyncio.Event()
handler_called.clear()
global_message_id = ""

#/register stage for users
# saves as [1, username]
# then [1, username], [2, password] etc etc
register_cache = {
    
}

timetable_display_settings_cache = {
    
}

async def start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vjc_logo = open(LOGO_PATH, "rb")
    
    start_message = '''
Welcome to VJC LaBot! 🤖

List of Commands:
/help - shows the help menu 
/timetable - shows your timetable
/homework - view your homework

Created by Ryan Lee & Jayden Soh, 25S64
'''

    user_instance = user.User(update.effective_user.id)
    exists, gapi_connected, portal_connected, tt_preferences_loaded =  user_instance.isExistingUser()
    
    if exists:
        vjc_logo = open(LOGO_PATH, "rb")

        tasks = []
        
        if not portal_connected:
            tasks.append("Connect your VJC Portal account using /portal!")    
            
        if not gapi_connected:
            tasks.append("Connect your google account using /google!")
            
        if not tt_preferences_loaded:
            tasks.append("Update your timetable preferences using /settings")
        
        string_tasks = ""
        for task in tasks:
            string_tasks = string_tasks + f"{tasks.index(task) + 1}. {task}\n"
        
        if string_tasks != "": #user has tasks
            start_message = f'''
User {update.effective_user.id}, 
Welcome back to VJC LaBot! 🤖
            
List of Commands:
/help - shows the help menu 
/timetable - shows your timetable
/homework - view your homework

Tasks:
{string_tasks}

Created by Ryan Lee & Jayden Soh, 25S64
'''
        
        else:
            start_message = f'''
User {update.effective_user.id}, 
Welcome back to VJC LaBot! 🤖

List of Commands:
/help - shows the help menu 
/timetable - shows your timetable
/homework - view your homework

Created by Ryan Lee & Jayden Soh, 25S64
'''
            
    else:
        start_message = f'''
Welcome to VJC LaBot! 🤖

Created by Ryan Lee & Jayden Soh, 25S64

To start using LaBot, you will have to link your VJC Portal Account and Google Account. 
/register
'''
        
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=vjc_logo, caption=start_message)

    vjc_logo.close()
    
async def handler_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    print(f"[QUERY] user_{query.from_user.first_name}: {query.from_user.id} | Packet: {query.data}")
    # query is similar to a dictionary
    # chat_instance, data, from_user, id(of query) ++++ 

    #will execute all functions, and only those with the correct query tag, eg (help)_t, then will execute
    await help_menu(update, context, callback=True, query=query)
    await timetable(update, context, callback=True, query=query)
    await settings(update, context, callback=True, query=query)
    #await timetable_menu(update, context, callback=True, query=query)

    return query    

async def handler_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    print(f"[MSG] user_{update.effective_user.id} | Packet: {message.text}")
    
    await register(update, context, callback=True, payload=message)

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, callback=False, query=None):
    #if it isn't a callback
    if not callback:
        print("[HELP] Entering the help menu.")
        
        options = [
            [InlineKeyboardButton("/Timetable", callback_data="help_t")],
            [InlineKeyboardButton("/Homework", callback_data="help_h")]
        ]
        
        reply_markup = InlineKeyboardMarkup(options)

        await context.bot.send_message(update.effective_chat.id, text=help_message, reply_markup=reply_markup)

    #If it is a callback
    elif "help" in query.data: #check for correct tag
        query_data = (query.data).split("_") #split help_h into [help, h]
        
        if query_data[1] == "t": #timetable help menu
            print("[HELP] Entering the timetable help menu.")
            #timetable()
            
            await context.bot.send_message(update.effective_chat.id, text="timetable")
                    
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE, callback = False, payload = None):
    global register_cache
    user_instance = user.User(update.effective_user.id)
    if not callback and register_cache.get(f"{update.effective_user.id}") == None:
        exists, gapi_connected, portal_connected, tt_preferences_loaded =  user_instance.isExistingUser()
        
        if not exists:
            m = f"New User Profile Created."
            await context.bot.send_message(chat_id=update.effective_chat.id, text=m)
            register_cache[f"{update.effective_user.id}"] = ["1"]   
            
            m = f"""
            You are now linking your VJC Portal Account.\n    Please enter your VJC Portal Username below:
            """
            await context.bot.send_message(chat_id=update.effective_chat.id, text=m)
        
        else: #dont run
            message = f"You are already a registered user!"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            message = f"""
            If you would like to edit your registered information, please run the following commands below.\n    /portal - Update VJC Portal Login Information.\n    /google - Link your google account.\n    /reset - Reset your registered information.\n    /settings - Change how LaBot functions.
            """
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        try:    
            print(len(register_cache.get(f"{update.effective_user.id}")) >= 1)
            if payload != None:
                if len(register_cache.get(f"{update.effective_user.id}")) == 1: #completed stage 1, username, saving
                    register_cache[f"{update.effective_user.id}"].append(f"{payload.text}")
                    #print(f"Before Password {register_cache}")
                    m = f"""
                    You are now linking your VJC Portal Account.\n    Please enter your VJC Portal Password below:
                    """
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=m)            
                
                elif len(register_cache[f"{update.effective_user.id}"]) == 2: #completed stage 2, password, saving
                    #print(f"Before Class {register_cache}")
                    register_cache[f"{update.effective_user.id}"].append(f"{payload.text}")
                    #print(f"Class {register_cache}")
                    m = f"""
                    You are now linking your VJC Portal Account.\n    Please enter your class below: eg. 25S64
                    """
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=m)          
                    
                elif len(register_cache[f"{update.effective_user.id}"]) == 3: 
                    print(register_cache)
                    username = register_cache[f"{update.effective_user.id}"][1]
                    password = register_cache[f"{update.effective_user.id}"][2]
                    class_ = payload.text
                    
                    m = f"""
                    You have linked your VJC Portal Account:\n    Username: {username}\n    Password: {password}\n    Class: {class_}
                    """
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=m)     

                    user_instance.updateVortalInformation([username, password], class_)
                    
                    m = f"""
                    You are now linking your Google Calendar Account!\n    Your school timetable will be saved to this google calendar.\n\n    Please click the link below to give LaBot permissions to write to your google calendar.
                    """
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=m)      
                    
                    flow, auth_url = user_instance.getGoogleAPIAuthURL()
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=auth_url)
                    
                    m = "Waiting for authentication response..."
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=m)  
                    
                    status = user_instance.completeGoogleAPIAuth(flow)
                    
                    if status == "timeout":
                        m = "Authentication Timeout. Please retry with /google!"
                        await context.bot.send_message(chat_id=update.effective_chat.id, text=m)  
                        
                    else:
                        m = "You have successfully linked your Google Calendar Account."
                        await context.bot.send_message(chat_id=update.effective_chat.id, text=m)  
                    
                    m = "Your LaBot Account is ready for use!"
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=m)         
                    
                    del register_cache[f"{update.effective_user.id}"]               
                
            else:
                print("[REG] Unexpected Error occured, empty callback payload")
                    
        except TypeError:
            pass

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE, callback = False, query = None, repeat_data = None):
    if not callback:
        m = f"LaBot Settings Menu | user_{update.effective_user.id}\n\n    Please select an option below:"
        
        options = [
            [InlineKeyboardButton("Timetable Settings", callback_data="settings_timetable")],
        ]
        
        reply_markup = InlineKeyboardMarkup(options)

        await context.bot.send_message(update.effective_chat.id, text=m, reply_markup=reply_markup)
        
    else:
        if repeat_data != None or "settings" in query.data:
            if query != None:
                query = str(query.data).split("_")
                
            else:
                query = repeat_data.split("_")
            
            if query[1] == 'timetable': #enter the timetable menu
                if len(query) == 2:
                    m = f"LaBot Timetable Settings Menu | user_{update.effective_user.id}\n\n    1. Update Shown Lessons\n    Please select an option below:"
                    
                    options = [
                        [InlineKeyboardButton("Update Shown Lessons", callback_data="settings_timetable_shownlessons")],
                    ]
                    
                    reply_markup = InlineKeyboardMarkup(options)

                    await context.bot.send_message(update.effective_chat.id, text=m, reply_markup=reply_markup)
                    
                if len(query) == 3:
                    if query[2] == "shownlessons":
                        user_instance = user.User(update.effective_user.id)
                        data = user_instance.getTimetablePreferences()
        
                        show_h1 = data.get('show_h1')
                        show_prog = data.get('show_prog')
                        lessons = data.get('lessons')
                        
                        if show_h1:
                            display_h1 = f"Show H1 Lessons ✅"
                            
                        else:
                            display_h1 = f"Show H1 Lessons ❌"
                            
                        if show_prog:
                            display_prog = f"Show Programs/Remidials ✅"
                            
                        else:
                            display_prog = f"Show Programs/Remidials ❌"
                        
                        #select those that you would like to display
                        default_lessons = user.default_lessons
                        
                        # display_lessons = ""
                        # for item in default_lessons.items():
                        #     if item in lessons.items(): #if previously configured, and the lesson is selected to be displayed
                        #         display_lessons = display_lessons + "\n    " + f"{item[1]} ✅"
        
                        #     else:
                        #         display_lessons = display_lessons + "\n    " + f"{item[1]} ❌"
                        
                        options = [[InlineKeyboardButton(f"{display_h1.replace('Show ', '')}", callback_data=f"settings_timetable_shownlessons_showh1")],
                                   [InlineKeyboardButton(f"{display_prog.replace('Show ', '')}", callback_data=f"settings_timetable_shownlessons_showprog")]]
                        
                        for item in default_lessons.items():
                            if item in lessons.items():
                                options.append([InlineKeyboardButton(f"{item[1]} ✅", callback_data=f"settings_timetable_shownlessons_{item[0]}")])
                                
                            else:
                                options.append([InlineKeyboardButton(f"{item[1]} ❌", callback_data=f"settings_timetable_shownlessons_{item[0]}")])
                                
                        options.append([InlineKeyboardButton(f"Save Settings", callback_data=f"settings_timetable_shownlessons_save")])
                        
                        m = f"LaBot Timetable Settings Menu | user_{update.effective_user.id}\n\n    You are now updating your shown lessons.\n    \n    ✅ - Lessons will be shown in your timetable.\n    ❌ - Lessons will not be shown in your timetable.\n\n    You may toggle on and off a lesson by selecting an option below."
                        reply_markup = InlineKeyboardMarkup(options)
                        await context.bot.send_message(update.effective_chat.id, text=m, reply_markup=reply_markup)
                       
                elif len(query) == 4:
                    arg = query[3]
                    
                    if arg == "save":
                        m = "Your preferences are saved. You may now run /timetable to view your timetable."
                        await context.bot.send_message(update.effective_chat.id, text=m)
                        
                        # await settings(update=update, context=context) idk should user go back to settings?
                        
                        return True
                    
                    user_instance = user.User(update.effective_user.id)
                    data = user_instance.getTimetablePreferences()

                    show_h1 = data.get('show_h1')
                    show_prog = data.get('show_prog')
                    lessons = data.get('lessons')
                    
                    if arg == "showh1":
                        if show_h1: #toggle
                            show_h1 = False
                            
                        else:
                            show_h1 = True
                    
                    elif arg == "showprog":
                        if show_prog:
                            show_prog = False
                            
                        else:
                            show_prog = True         
                              
                    else: #it is a lesson that needs to be toggled
                        # if lessons == user.default_lessons: #reset default
                        #     lessons = {}
                        
                        if lessons.get(arg) != None: #lesson is toggled
                            del lessons[arg]
                            
                        else:
                            lessons[arg] = user.default_lessons.get(arg)
                        
                    user_instance.updateTimetablePreferences(show_h1=show_h1, show_prog=show_prog, lessons=lessons)

                    await settings(update, context, True, repeat_data="settings_timetable_shownlessons")
                    

async def timetable(update: Update, context: ContextTypes.DEFAULT_TYPE, callback = False, query = None):
    user_instance = user.User(update.effective_user.id)
    
    if not callback:
        exists, gapi_connected, portal_connected, tt_preferences_loaded =  user_instance.isExistingUser()
        
        if not exists:
            m = "Your LaBot account is not registered! Please start by using /register!"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=m)  
            
            return False
            
        else:
            run = True
            if not portal_connected:
                m = "Please update your VJC Portal Information by using /portal!"
                await context.bot.send_message(chat_id=update.effective_chat.id, text=m)  
                run = False
            
            if not tt_preferences_loaded:
                m = "Please update your timetable display settings by using /settings!"
                await context.bot.send_message(chat_id=update.effective_chat.id, text=m)  
                run = False
                
            if run:
                m = "LaBot Timetable Menu\n    Please choose an action below:"
                await context.bot.send_message(chat_id=update.effective_chat.id, text=m)
                
                options = [
                    [InlineKeyboardButton("Show this week's timetable", callback_data="tt_show_thisweek")],
                    [InlineKeyboardButton("Show next week's timetable", callback_data="tt_show_nextweek")],
                    [InlineKeyboardButton("Save this week's timetable (GCAL)", callback_data="tt_save_thisweek")],
                    [InlineKeyboardButton("Save next week's timetable (GCAL)", callback_data="tt_save_nextweek")]
                ]
                
                reply_markup = InlineKeyboardMarkup(options)

                await context.bot.send_message(update.effective_chat.id, text=m, reply_markup=reply_markup)

    else:
        if query != None:
            if "tt" in query.data:
                query = str(query.data).split("_")
                tt_instance = tt(update.effective_user.id)
                
                if query[1] == "show": #entering show menu
                    if query[2] == "thisweek":
                        t_monday = tt_instance.getDateThisMonday()
                            
                        if len(query) == 3:
                            path = fr"{cache}\{update.effective_user.id}\tt_{t_monday}.txt"
                            if not os.path.exists(path): #if existing week does not already exist, load from portal
                                m = "LaBot Timetable Menu\n    Loading your timetable from the VJC Portal now."
                                data = user_instance.getVortalInformation()
                                
                                username = data.get('username')
                                password = data.get('password')
                                class_ = data.get('class')
                                
                                try:
                                    agent = portalAgent(username, password, update.effective_user.id)
                                    _, path = agent.getTimetable(str(t_monday))
                                    
                                    if _ == False:
                                        print(f"[TT] Something Went Wrong, getTimetable error {path}")
                                        return False
                                    
                                except vortal.VortalIncorrectLoginInformation:
                                    m = "Incorrect VJC Portal Login Information. \n    Please re-key in your credentials using /portal."
                                    return False
                                
                            m = "LaBot Timetable Menu\n    You are showing this week's timetable.\n    Please choose an option below:"
                            #check which day they want to check
                            options = [
                                [InlineKeyboardButton("Monday", callback_data="tt_show_thisweek_monday")],
                                [InlineKeyboardButton("Tuesday", callback_data="tt_show_thisweek_tuesday")],
                                [InlineKeyboardButton("Wednesday", callback_data="tt_show_thisweek_wednesday")],
                                [InlineKeyboardButton("Thursday", callback_data="tt_show_thisweek_thursday")],
                                [InlineKeyboardButton("Friday", callback_data="tt_show_thisweek_friday")]
                            ]
                            
                            reply_markup = InlineKeyboardMarkup(options)

                            await context.bot.send_message(update.effective_chat.id, text=m, reply_markup=reply_markup)
                        
                        elif len(query) == 4: #if callbackdata contains a day in it
                            day = query[3]
                            
                            path = fr"{cache}\{update.effective_user.id}\tt_{t_monday}.txt"
                            lessons = tt_instance.timetable(path=path, day=day)
                            
                            if lessons == []:
                                m = f"No lessons on {day}."
                                
                            else:
                                m = f"Showing Lessons on {day}:"
                                
                                for lesson in lessons:
                                    location = lesson.get("location")
                                    if location == None or location == '':
                                        location = "VJC"
                                    m = m + '\n' + f'{lesson.get("start")[0]}:{lesson.get("start")[1]} - {lesson.get("end")[0]}:{lesson.get("end")[1]} {lesson.get("name")} | {location}'
                            
                            #m = str(lessons)
                            await context.bot.send_message(update.effective_user.id, text=m)
                        
                    elif query[2] == "nextweek":
                        n_monday = tt_instance.getDateNextMonday()
                        if len(query) == 3:
                            
                            path = fr"{cache}\{update.effective_user.id}\tt_{n_monday}.txt"
                            if not os.path.exists(path): #if existing week does not already exist, load from portal
                                m = "LaBot Timetable Menu\n    Loading your timetable from the VJC Portal now."
                                data = user_instance.getVortalInformation()
                                
                                username = data.get('username')
                                password = data.get('password')
                                class_ = data.get('class')
                                
                                try:
                                    agent = portalAgent(username, password, update.effective_user.id)
                                    _, path = agent.getTimetable(str(n_monday))
                                    
                                    if _ == False:
                                        print(f"[TT] Something Went Wrong, getTimetable error {path}")
                                        return False
                                    
                                except vortal.VortalIncorrectLoginInformation:
                                    m = "Incorrect VJC Portal Login Information. \n    Please re-key in your credentials using /portal."
                                    return False
                                
                            m = "LaBot Timetable Menu\n    You are showing next week's timetable.\n    Please choose an option below:"
                            #check which day they want to check
                            options = [
                                [InlineKeyboardButton("Monday", callback_data="tt_show_nextweek_monday")],
                                [InlineKeyboardButton("Tuesday", callback_data="tt_show_nextweek_tuesday")],
                                [InlineKeyboardButton("Wednesday", callback_data="tt_show_nextweek_wednesday")],
                                [InlineKeyboardButton("Thursday", callback_data="tt_show_nextweek_thursday")],
                                [InlineKeyboardButton("Friday", callback_data="tt_show_nextweek_friday")]
                            ]
                            
                            reply_markup = InlineKeyboardMarkup(options)

                            await context.bot.send_message(update.effective_chat.id, text=m, reply_markup=reply_markup)
                        
                        elif len(query) == 4: #if callbackdata contains a day in it
                            day = query[3]
                            
                            path = fr"{cache}\{update.effective_user.id}\tt_{n_monday}.txt"
                            lessons = tt_instance.timetable(path=path, day=day)
                            
                            if lessons == []:
                                m = f"No lessons on {day}."
                                
                            else:
                                m = f"Showing Lessons on {day}:"
                                
                                for lesson in lessons:
                                    location = lesson.get("location")
                                    if location == None or location == '':
                                        location = "VJC"
                                    m = m + '\n' + f'{lesson.get("start")[0]}:{lesson.get("start")[1]} - {lesson.get("end")[0]}:{lesson.get("end")[1]} {lesson.get("name")} | {location}'
                            
                            #m = str(lessons)
                            await context.bot.send_message(update.effective_user.id, text=m)
                        
                if query[1] == "save": #enter save menu
                    if query[2] == "thisweek":
                        t_monday = tt_instance.getDateThisMonday()
                        
                        m = "Saving this week's timetable to your Google Calendar...\n\nPlease Wait!"
                        await context.bot.send_message(chat_id=update.effective_chat.id, text=m)
                        
                        bearlander_instance = bearlander(update.effective_user.id)
                        bearlander_instance.save_to_gcal(0)
                        
                        m = f"Successfully saved {total} events to your calendar."
                        await context.bot.send_message(chat_id=update.effective_user.id, text=m)
                        
                    elif query[2] == "nextweek":
                        n_monday = tt_instance.getDateNextMonday()
                        
                        m = "Saving next week's timetable to your Google Calendar...\n\nPlease Wait!"
                        await context.bot.send_message(chat_id=update.effective_chat.id, text=m)
                        
                        bearlander_instance = bearlander(update.effective_user.id)
                        _, total = bearlander_instance.save_to_gcal(1)
                        
                        m = f"Successfully saved {total} events to your calendar."
                        await context.bot.send_message(chat_id=update.effective_chat.id, text=m)
def main():   
    print("\n[LOG] Telegram Bot is live...")
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler("start", start_menu)
    help_handler = CommandHandler('help', help_menu)
    timetable_handler = CommandHandler('timetable', timetable)
    settings_handler = CommandHandler('settings', settings)
    query_handler = CallbackQueryHandler(handler_query)
    register_handler = CommandHandler("register", register)
    message_handler = MessageHandler(callback=handler_message, filters=None)

    
    application.add_handler(help_handler)
    application.add_handler(timetable_handler)
    application.add_handler(query_handler)
    application.add_handler(settings_handler)
    application.add_handler(start_handler)
    application.add_handler(register_handler)
    application.add_handler(message_handler)
    application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())