from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
import threading as t
import asyncio
from dependencies import bearlander
from dependencies import vortal

TOKEN = '7727005144:AAH-xavS8MfnRfkm8zZyo_MDHYin1vgHOcQ'

#Files
LOGO_PATH = r"C:\Users\delay\OneDrive\Documents\Code & Programs\Visual Studio Code\telebot\Formatting Files\2022 29 Farewell Assemnly.jpg"

# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )

start_message = '''
Welcome to VJC LaBot! 🤖

List of Commands:
 /help - shows the help menu 
 /timetable - shows your timetable
 /homework - view your homework

Created by Ryan Lee & Jayden Soh, 25S64
'''

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

async def start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vjc_logo = open(LOGO_PATH, "rb")

    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=vjc_logo, caption=start_message)

    vjc_logo.close()
    
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    print(f"[QUERY] User: {query.from_user.first_name}: {query.from_user.id} | Packet: {query.data}")
    # query is similar to a dictionary
    # chat_instance, data, from_user, id(of query) ++++ 

    #will execute all functions, and only those with the correct query tag, eg (help)_t, then will execute
    await help_menu(update, context, callback=True, query=query)
    await timetable_menu(update, context, callback=True, query=query)
    await homework_menu(update, context, callback=True, query=query)

    return query    

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

async def timetable_save_gcal(update: Update, context: ContextTypes.DEFAULT_TYPE, callback = False, query=None):
    user = update.effective_user 
    

async def timetable_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, callback = False, query=None):
    global global_message_id
    if not callback:
        week_keyboard = [
            [InlineKeyboardButton("Week A", callback_data="timetable_week_A")],
            [InlineKeyboardButton("Week B", callback_data="timetable_week_B")]
        ]

        reply_markup1 = InlineKeyboardMarkup(week_keyboard)
        await update.message.reply_text("Choose which week to check", reply_markup = reply_markup1)
        
    elif "timetable" in query.data:
        query_data =(query.data).split("_")
        
        if query_data[1] == "week":
            if len(query_data) <= 3:
                if query_data[2] == "A":
                    print("[TIMETABLE] Week A choosen")
                    
                    keyboard = [ 
                        [InlineKeyboardButton("Monday", callback_data="timetable_week_A_day_monday")],
                        [InlineKeyboardButton("Tuesday", callback_data="timetable_week_B_day_tuesday")],
                        [InlineKeyboardButton("Wednesday", callback_data="3A")],
                        [InlineKeyboardButton("Thursday", callback_data="4A")],
                        [InlineKeyboardButton("Friday", callback_data="5A")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await query.edit_message_text("Choose which day you want to check: ", reply_markup=reply_markup)

                else:
                    print("[TIMETABLE] Week B choosen")
                
                    keyboard = [
                        [InlineKeyboardButton("Monday", callback_data="timetable_week_A_day_monday")],
                        [InlineKeyboardButton("Tuesday", callback_data="timetable_week_B_day_tuesday")],
                        [InlineKeyboardButton("Wednesday", callback_data="3")],
                        [InlineKeyboardButton("Thursday", callback_data="4")],
                        [InlineKeyboardButton("Friday", callback_data="5")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)   
                    
                    await query.edit_message_text("Choose which day you want to check: ", reply_markup=reply_markup)
                    
            else:
                if query_data[2] == "A":
                    print(timetable.a_timetable(query_data[4]))
                    lessons = timetable.a_timetable(query_data[4])
                    for lesson in lessons:
                        lesson.get("name")
                    
                elif query_data[2] == "B":
                    print(timetable.b_timetable(query_data[4]))
                    
                    
async def homework_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, callback = False, query=None):
    pass    

def main():   
    print("\n[LOG] Telegram Bot is live...")
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler("start", start_menu)
    help_handler = CommandHandler('help', help_menu)
    query_handler = CallbackQueryHandler(handler)
    timetable_handler = CommandHandler('timetable', timetable_menu)
    
    application.add_handler(help_handler)
    application.add_handler(query_handler)
    application.add_handler(timetable_handler)
    application.add_handler(start_handler)
    
    application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())