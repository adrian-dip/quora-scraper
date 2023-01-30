import time
import random
import dateparser
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import re
import pandas as pd
import pickle
import time
import multiprocessing
from auxiliary_functions import *

# -------------------------------------------------------------
# Basic webdriver options
# -------------------------------------------------------------
def connect_chrome():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('log-level=3')
    options.add_argument("--incognito")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    time.sleep(2)
    return driver

# -------------------------------------------------------------
# question url crawler 
# -------------------------------------------------------------	

def questions(topics_list):
    url_bag = set()
    browser = connect_chrome()
    topic_index = -1
    loop_limit = len(topics_list)
    print('Starting the questions crawling')
    while True:
        print('--------------------------------------------------')
        topic_index += 1
        if topic_index >= loop_limit:
            print('Crawling completed')
            browser.quit()
            break
        topic_term = topics_list[topic_index].strip()
        # Looking if the topic has an existing Quora url
        print('#########################################################')
        print('Looking for topic number : ', topic_index, ' | ', topic_term)
        try:
            url = topic_term
            browser.get(url)
            time.sleep(5)
        except Exception as e0:
            print('topic does not exist in Quora')
            continue

        # get browser source
        time.sleep(5)
        html_source = browser.page_source
        question_count_soup = BeautifulSoup(html_source, 'html.parser')
        all_question_htmls = question_count_soup.find_all('a', {'class': 'q-box qu-display--block qu-cursor--pointer qu-hover--textDecoration--underline Link___StyledBox-t2xg9c-0 dxHfBI'}, href=True)

        #  get total number of questions
        question_count = len(all_question_htmls)
        if question_count is None:
            print('topic does not have questions...')
            continue
        if question_count == 0:
            print('topic does not have questions...')
            continue

        # Get scroll height
        last_height = browser.execute_script("return document.body.scrollHeight")

        # infinite while loop, break it when you reach the end of the page or not able to scroll further.
        # Note that Quora
        # if there is only 10 questions, we need to scroll down the profile to load more questions
        if question_count == 10:
            scroll_down(browser, 'questions')

        # next we harvest all questions URLs that exists in the Quora topic's page
        # get html page source
        html_source = browser.page_source
        soup = BeautifulSoup(html_source, 'html.parser')

        all_htmls = soup.find_all('a', {'class': 'q-box qu-display--block qu-cursor--pointer qu-hover--textDecoration--underline Link___StyledBox-t2xg9c-0 dxHfBI'}, href=True)
        question_count_after_scroll = len(all_htmls)
        print(f'number of questions for this topic : {question_count_after_scroll}')

        # add questions to a set for uniqueness
        for html in all_htmls:
            url_bag.add(html['href'])

        sleep_time = (round(random.uniform(15, 32), 1))
        time.sleep(sleep_time)
        
    browser.quit()
    return list(url_bag)

# -------------------------------------------------------------
# answers crawler 
# -------------------------------------------------------------

def get_answers(list_of_links, n_save=0, save_frequency=100, save_dir=''):

    # initialize data structures

    all_answers_dict = {}
    new_qs = []

    # loop through question links

    for link in list_of_links:

        # start chrome

        browser = connect_chrome()
        browser.get(link)
        time.sleep(random.randint(2,6))

        # scroll down and parse html

        scroll_down(browser, type_of_page='answers')
        browser.execute_script("window.scrollTo(0, 0);")
        html_source = browser.page_source
        answer_soup = BeautifulSoup(html_source, "html.parser")

        # Get answers from page

        answer_dict = {}
        all_qboxes = answer_soup.find_all('div', {'class':'q-box qu-hover--bg--darken'})
        for box in all_qboxes:
            linkst = box.findAll('a')
            for linkt in linkst:

                # class and container type are randomized by Quora as an anti-scraping measure, but finding the divs with profile info
                # point to the answers regardless of their html tag properties

                if 'profile/' in linkt['href']:
                    answer_spans = box.find_all('span', {'class':'CssComponent__CssInlineComponent-sc-1oskqb9-1 UserSelectableText___StyledCssInlineComponent-lsmoq4-0'})
                    answer_burner = []
                    for d in answer_spans:
                        for p in d.findAll('p'):
                            answer_burner.append(p.text)
                answer_joined = "".join(answer_burner)

                # Quora repeats and hides the answer text as an anti-scraping measure, so we have to go through loops to a) reconstitute the answer from random
                # segments and b) make sure the answer is not repeated

                if answer_joined not in answer_dict:
                    answer_dict[answer_joined] = 0

                    # get the number of [votes, comments, shares]

                    all_engagements = box.find_all('div', {'class':'q-flex qu-alignItems--center'})
                    for engagement in all_engagements:
                        iterator_burner = engagement.findAll('span', {'class':'q-text qu-whiteSpace--nowrap qu-display--inline-flex qu-alignItems--center qu-justifyContent--center'})
                        engagement_burner = []
                        if iterator_burner:
                            for element in iterator_burner:
                                engagement_burner.append(convert_number(element.text))
                        if len(engagement_burner) > 0:
                            answer_dict[answer_joined] = engagement_burner


        # get new question links from "Related to this question"
                            
        relevant_qs = answer_soup.find_all('div', {'class':'q-box dom_annotate_related_questions qu-borderAll qu-borderRadius--small qu-borderColor--raised qu-boxShadow--small qu-mb--small qu-bg--raised'})
        for dq in relevant_qs:
            qs = dq.find_all('a')
            q_burner = []
            for q in qs:
                q_burner.append(q['href'])
            new_qs.extend(list(set(q_burner)))
            
        # get the questions that prompted the answer
        try:
            title = browser.find_element(By.XPATH, "//*[@id=\"mainContent\"]/div[1]/div/div/div/div/span/span/div/div/div/span/span")
        except:
            continue
        all_answers_dict[title.text] = answer_dict

        # we sleep so we don't get banned

        time.sleep(random.randint(5,12))
        
        # we save to disk

        if len(all_answers_dict) > save_frequency:
            titledf = []
            answerdf = []
            engagementdf = []

            for k,v in all_answers_dict.items():
                titledf.extend([k] * len(v))
                for k,v in v.items():
                    answerdf.append(k)
                    engagementdf.append(v)

            df = pd.DataFrame(data={'title':titledf, 'answer':answerdf,'engagement':engagementdf})
            df.to_csv(save_dir + str(n_save) + '.csv')

            with open(save_dir + str(n_save) + '.pkl', 'wb') as handle:
                pickle.dump(new_qs, handle, protocol=pickle.HIGHEST_PROTOCOL)

            new_qs = []
            n_save = n_save + save_frequency
            all_answers_dict = {}
            print('#########################################################')
            print(' ')
            print('Saved ' + str(save_frequency) + ' answers successfully')
            time.sleep(random.randint(3,6))


def engine(link, save_dir):
    all_answers_dict = {}
    new_qs = []
    browser = connect_chrome()
    browser.get(link)
    time.sleep(random.randint(2,5))

    ### get title
    try:
        title = browser.find_element(By.XPATH, "//*[@id=\"mainContent\"]/div[1]/div/div/div/div/span/span/div/div/div/span/span")
    except:
        return

    scroll_down(browser, type_of_page='answers')
    browser.execute_script("window.scrollTo(0, 0);")

    html_source = browser.page_source
    answer_soup = BeautifulSoup(html_source, "html.parser")

    ### Get answers from page
    answer_dict = {}
    all_qboxes = answer_soup.find_all('div', {'class':'q-box qu-hover--bg--darken'})

    for box in all_qboxes:
        linkst = box.findAll('a')
        for linkt in linkst:

                # class and container type are randomized by Quora as an anti-scraping measure, but finding the divs with profile info
                # point to the answers regardless of their html tag properties

            if 'profile/' in linkt['href']:
                answer_spans = box.find_all('span', {'class':'CssComponent__CssInlineComponent-sc-1oskqb9-1 UserSelectableText___StyledCssInlineComponent-lsmoq4-0'})
                answer_burner = []
                for d in answer_spans:
                    for p in d.findAll('p'):
                        answer_burner.append(p.text)
            answer_joined = "".join(answer_burner)

                # Quora repeats and hides the answer text as an anti-scraping measure, so we have to go through loops to a) reconstitute the answer from random
                # segments and b) make sure the answer is not repeated

            if answer_joined not in answer_dict:
                answer_dict[answer_joined] = [0,0]
                all_engagements = box.find_all('div', {'class':'q-flex qu-alignItems--center'})

                # get the number of [votes, comments, shares]

                for engagement in all_engagements:
                    iterator_burner = engagement.findAll('span', {'class':'q-text qu-whiteSpace--nowrap qu-display--inline-flex qu-alignItems--center qu-justifyContent--center'})
                    engagement_burner = []
                    if iterator_burner:
                        for element in iterator_burner:
                            engagement_burner.append(convert_number(element.text))
                    if len(engagement_burner) > 0:
                        answer_dict[answer_joined] = [engagement_burner, 0]

    # get views
    
    clickable = browser.find_elements(By.XPATH, "//div/div/button/div/div/div[text()='Continue Reading']")
    print('Found elements')

    #############################################

    # Unfortunately, due to Quora's anti-scraping stance, we have to go through horrible verbose loops to prevent the website from stopping to
    # respond or start randomizing element position, attributes, and class names. 
    # After a week of testing, this is the script that worked the best.

    ############################################

    for i in range(len(clickable)):
        try:
            read_more = browser.find_element(By.XPATH, "//div/div/button/div/div/div[text()='Continue Reading']")
            ActionChains(browser).move_to_element(read_more).perform()
            time.sleep(0.5)
            browser.execute_script("window.scrollBy(0, 120);")
            time.sleep(0.75)
            read_more.click()
            time.sleep(0.75)
            browser.execute_script("window.scrollBy(0, 300);")
            time.sleep(0.5)
        except:
            pass
        try:
            browser.execute_script("window.scrollBy(0, 1000);")
            time.sleep(0.5)
            read_more = browser.find_element(By.XPATH, "//div/div/button/div/div/div[text()='Continue Reading']")
            browser.execute_script("window.scrollBy(0, 120);")
            time.sleep(0.75)
            ActionChains(browser).move_to_element(read_more).perform()
            time.sleep(0.75)
            read_more.click()
            time.sleep(0.5)
            browser.execute_script("window.scrollBy(0, 300);")
            time.sleep(0.5)
        except:
            pass
        try:
            browser.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
            read_more = browser.find_element(By.XPATH, "//div/div/button/div/div/div[text()='Continue Reading']")
            ActionChains(browser).move_to_element(read_more).perform()
            time.sleep(0.5)
            browser.execute_script("window.scrollBy(0, 120);")
            time.sleep(0.5)
            read_more.click()
            time.sleep(0.5)
            browser.execute_script("window.scrollBy(0, 300);")
            time.sleep(0.5)
        except:
            break

    html_source = browser.page_source
    answs = list(answer_dict.keys())

    # we get [votes, comments, shares, and views]

    for i, a in enumerate(answs):
        if i <= len(clickable):
            re1 = re.escape(a[:20])
            re2 = r'.*'
            try:
                re3 = re.escape(answs[i + 1][:20])
                generic_re = re.compile("(%s%s%s)" % (re1, re2,re3)).findall(html_source)
                generic_re = max(generic_re, key=len)
                score = re.search(r'\d+(\.\d+(K|M)?)?\sviews', generic_re)
                if score:
                    answer_dict[a][1] = convert_number(score[0][:-6])
            except:
                generic_re = re.compile("(%s%s)" % (re1, re2)).findall(html_source)
                try:
                    generic_re = max(generic_re, key=len)
                    score = re.search(r'\d+(\.\d+(K|M)?)?\sviews', generic_re)
                    if score:
                        answer_dict[a][1] = convert_number(score[0][:-6]) 
                except:
                    continue

    # we get links to relevant questions
                        
    relevant_qs = answer_soup.find_all('div', {'class':'q-box dom_annotate_related_questions qu-borderAll qu-borderRadius--small qu-borderColor--raised qu-boxShadow--small qu-mb--small qu-bg--raised'})
    for dq in relevant_qs:
        qs = dq.find_all('a')
        q_burner = []
        for q in qs:
            q_burner.append(q['href'])
        new_qs.extend(list(set(q_burner)))
        
    all_answers_dict[title.text] = answer_dict
    
    # we save 
    titledf = []
    answerdf = []
    engagementdf = []
    for k,v in all_answers_dict.items():
        titledf.extend([k] * len(v))
        for k,v in v.items():
            answerdf.append(k)
            engagementdf.append(v)
    df = pd.DataFrame(data={'title':titledf, 'answer':answerdf,'engagement':engagementdf})
    df.to_csv(save_dir + str(n_save) + '.csv')
    with open(save_dir + str(n_save) + '.pkl', 'wb') as handle:
        pickle.dump(new_qs, handle, protocol=pickle.HIGHEST_PROTOCOL)
    new_qs = []
    n_save = n_save + 1
    all_answers_dict = {}
    all_answers_dict = {}
    new_qs = []
    time.sleep(random.randint(2,5))  

def get_answers_w_views(list_of_links, n_save=0, save_frequency=100, save_dir=''):

    for link in list_of_links:
        print('start')
        # Start process
        p = multiprocessing.Process(target=engine, name="engine", args=(link, save_dir,))
        p.start()

        # Wait n seconds
        time.sleep(240)

        # Terminate 
        p.terminate()

        # Cleanup
        p.join()
        print('end')