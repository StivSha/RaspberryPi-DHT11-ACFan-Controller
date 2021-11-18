from datetime import date, datetime
import time

date1 = 0


def sample_responses(input_text):
    user_message = str(input_text).lower()
    if user_message in ("hello", "hi", "sup", "ciao"):
        return "Welcome :)"

    if user_message in ("Who made this Project?", "Who made this project", "Who are the creators", "Who are the creators?", "creator"):
        return "Ettore Saggiorato & Stiven Sharra"

    if user_message in ("time", "Time?"):
        global date1
        date1 = datetime.now()
        return str(date1)

    if user_message in ("difference"):
        date2 = datetime.now()
        print(date2)
        datediff = date2-date1
        return str(datediff)

    return "Idk what are you saying"
