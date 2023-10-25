import time
import dateparser
import random

# -------------------------------------------------------------
# remove 'k'(kilo) and 'm'(million) from Quora numbers
# -------------------------------------------------------------
def convert_number(number):
    if 'K' in number:
        n = float(number.lower().replace('k', '').replace(' ', '')) * 1000
    elif 'M' in number:
        n = float(number.lower().replace('m', '').replace(' ', '')) * 1000000
    else:
        n = number
    return int(n)


# -------------------------------------------------------------
# convert Quora dates (such as 2 months ago) to DD-MM-YYYY format
# -------------------------------------------------------------
def convert_date_format(date_text):
    try:
        if "Updated" in date_text:
            date = date_text[8:]
        else:
            date = date_text[9:]
        date = dateparser.parse(date_text).strftime("%Y-%m-%d")
    except:  # when updated or answered in the same week (ex: Updated Sat)
        date = dateparser.parse("7 days ago").strftime("%Y-%m-%d")
    return date


# -------------------------------------------------------------
# scroll up
# -------------------------------------------------------------
def scroll_up(self, nb_times):
    for iii in range(0, nb_times):
        self.execute_script("window.scrollBy(0,-200)")
        time.sleep(1)


# -------------------------------------------------------------
# method for loading  quora dynamic content
# -------------------------------------------------------------

def scroll_down(self, type_of_page='users'):
    last_height = self.page_source
    loop_scroll = True
    attempt = 0
    # we generate a random waiting time between 2 and 4
    waiting_scroll_time = round(random.uniform(2, 4), 1)
    max_waiting_time = round(random.uniform(5, 7), 1)
    # we increase waiting time when we look for questions urls
    if type_of_page == 'questions': max_waiting_time = round(random.uniform(20, 30), 1)
    # scroll down loop until page not changing
    while loop_scroll:
        self.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        if type_of_page == 'answers':
            scroll_up(self, 2)
        new_height = self.page_source
        if new_height == last_height:
            # in case of not change, we increase the waiting time
            waiting_scroll_time = max_waiting_time
            attempt += 1
            if attempt == 3:  # in the third attempt we end the scrolling
                loop_scroll = False
        # print('attempt',attempt)
        else:
            attempt = 0
            waiting_scroll_time = round(random.uniform(2, 4), 1)
        last_height = new_height