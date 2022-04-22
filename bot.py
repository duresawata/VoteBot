from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    ReplyKeyboardRemove,
    Update,
    Bot
)
from telegram.ext import (
    Updater,
    CommandHandler,
    PollAnswerHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler,
    CallbackQueryHandler
)
import logging
import os
import csv


admin = ["admin_chatid1", "admin_chatid2"]


A, B = range(2)

BOT = Bot("TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

id_number = None

def start(update: Update, context: CallbackContext) -> None:
    """Inform user about what this bot can do"""
    if str(update.message.chat_id) in admin:
        chatid = update.message.chat_id
        keyboard = [
            [
                InlineKeyboardButton("Vote Statistics🌐", callback_data="senddata"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard, one_time_keyboard=True)
        BOT.send_message(
            chat_id = chatid,
            text = "🅰🅳🅼🅸🅽 ⛨",
            reply_markup= reply_markup,
        )

        BOT.send_message(
            chat_id = chatid,
            text = 'Please Vote. Enter Your ID: ',
        )
        
    else:
        update.message.reply_text(
            'Welcome. Vote for T-shirt!\n\nPlease Enter Your ID: '
        )
    return A



def send_data(update, context):
    data = makeAnalysis()
    text = "Total <b>" + str(data['tot']) + "</b> Votes \t\t\t ⌚Status\n\n"
    text += "<code>    Design 1 ↣ " + str(data['1']) + " Votes\n"
    text += "    Design 2 ↣ " + str(data['2']) + " Votes\n"
    text += "    Design 3 ↣ " + str(data['3']) + " Votes\n"
    text += "    Design 4 ↣ " + str(data['4']) + "</code> Votes\n\n"

    standing = data['leading_key']
    
    text += "⭐Leading: <b>Design " +  standing + "</b> With <b>" + str(data[standing]) +"</b> Votes!\n\n"
    text += "/Show_all_Votes"
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = text,
        parse_mode = ParseMode.HTML,
    )

    return B

def show_all_vote(update, context):
    filename = "Users.csv"
    text = "/Download_CSV ✅\n\n"
    count = 1
    if os.path.isfile(filename):
        with open(filename, "r") as csvfile:
            csvreader = csv.reader(csvfile)
            fields = next(csvreader)

            for row in csvreader:
                text += (str(count) +". "+ row[0] + " Vote for design " + str(row[1]) + "\n")
                count += 1
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = text
        )
        
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = "There is no vote history."
        )
def send_CSV(update, context):
    context.bot.send_document(
            chat_id=update.effective_chat.id,
            document = open('Users.csv', 'rb')
        )

def receive_id(update, context):
    """Sends a predefined poll"""
    student_id = update.message.text.strip().lower()
    questions = ["1", "2", "3", "4"]
    
    if readCSV(student_id) == 1:
        BOT.send_photo(update.effective_chat.id, open("pack1.jpg", "rb"))
        BOT.send_photo(update.effective_chat.id, open("pack2.jpg", "rb"))
        message = context.bot.send_poll(
            update.effective_chat.id,
            "Which is your choosen design?",
            questions,
            is_anonymous=False,
            allows_multiple_answers=False,
        )
         # Save some info about the poll the bot_data for later use in receive_poll_answer
        payload = {
            message.poll.id: {
                "student_id": student_id,
                "questions": questions,
                "message_id": message.message_id,
                "chat_id": update.effective_chat.id,
                "answers": 0,
            }
        }
        context.bot_data.update(payload)
    else:
        update.message.reply_text(
        'Failed. Student with this ID number has already Voted. try again'
        )

def readCSV(studentID):
    ids = []
    filename = "Users.csv"
    if os.path.isfile(filename):
        with open(filename, "r") as csvfile:
            csvreader = csv.reader(csvfile)
            fields = next(csvreader)

            for row in csvreader:
                ids.append(row[0])

            if not str(studentID) in ids:
                return 1
            else:
                return 0
    else:
        return 1

def makeAnalysis():
    filename = "Users.csv"
    tot = 0
    dic = {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0
    }
    

    if os.path.isfile(filename):
        with open(filename, "r") as csvfile:
            csvreader = csv.reader(csvfile)
            fields = next(csvreader)

            for row in csvreader:
                tot += 1
                if int(row[1]) == 1:
                    dic["1"] += 1
                elif int(row[1]) == 2:
                    dic["2"] += 1
                elif int(row[1]) == 3:
                    dic["3"] += 1
                elif int(row[1]) == 4:
                    dic["4"] += 1

    mydic = dict(sorted(dic.items(), key=lambda item: item[1]))

    leading_key = list(mydic)[-1]

    dic['leading_key'] = leading_key
    dic['tot'] = tot
    return dic

def writeCSV(studentID, voteresult):
    headers = ["ID_Number", "Vote"]
    myDict = {"ID_Number": studentID, "Vote": voteresult}
    filename = "Users.csv"
    if os.path.isfile(filename):
        with open(filename, "a", newline="") as my_file:
            w = csv.DictWriter(my_file, fieldnames=headers)
            w.writerow(myDict)
    else:
        with open(filename, "w", newline="") as my_file:
            w = csv.DictWriter(my_file, fieldnames=headers)
            w.writeheader()
            w.writerow(myDict)

def receive_poll_answer(update: Update, context: CallbackContext) -> None:
    """Summarize a users poll vote"""
    answer = update.poll_answer
    poll_id = answer.poll_id
    try:
        questions = context.bot_data[poll_id]["questions"]
    # this means this poll answer update is from an old poll, we can't do our answering then
    except KeyError:
        return
    selected_options = answer.option_ids

    answer_string = questions[selected_options[0]]

    st_id = context.bot_data[poll_id]["student_id"]
    writeCSV(st_id, answer_string)

    context.bot.send_message(
        context.bot_data[poll_id]["chat_id"],
        f"Congratulations! You Voted for design {answer_string}!\n\nYour ID:\t{st_id}\n\nVote result:\tDesign {answer_string}",
        parse_mode=ParseMode.HTML,
    )
    
    context.bot_data[poll_id]["answers"] += 1


def receive_poll(update: Update, context: CallbackContext) -> None:
    """On receiving polls, reply to it by a closed poll copying the received poll"""
    actual_poll = update.effective_message.poll
    # Only need to set the question and options, since all other parameters don't matter for
    # a closed poll
    update.effective_message.reply_poll(
        question=actual_poll.question,
        options=[o.text for o in actual_poll.options],
        # with is_closed true, the poll/quiz is immediately closed
        is_closed=True,
        reply_markup=ReplyKeyboardRemove(),
    )


def help_handler(update: Update, context: CallbackContext) -> None:
    """Display a help message"""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = 
        """
Help Menu
Instructions to Vote:

1. start a bot
2. Enter your student Id number.

⚠ Notice: if you have already voted so far you can't vote again with the same id number twice.

3. choose your preferred design 
   from alternatives and touch it.
4. you're done!

<code>If you need addional help contact </code> @Jahbreezy
        Happy voting!
        
        """,
        parse_mode = ParseMode.HTML
        )

def myfall(u, c):
    print("fall")


def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("TOKEN")
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            A: [
                CallbackQueryHandler(send_data, pattern="^senddata$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", myfall),
        ],
    )
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(PollAnswerHandler(receive_poll_answer))
    dispatcher.add_handler(MessageHandler(Filters.poll, receive_poll))
    dispatcher.add_handler(MessageHandler(Filters.text and ~Filters.command, receive_id))
    dispatcher.add_handler(CommandHandler('help', help_handler))
    dispatcher.add_handler(CommandHandler('Show_all_Votes', show_all_vote))
    dispatcher.add_handler(CommandHandler('Download_CSV', send_CSV))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()