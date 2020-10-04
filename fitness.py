import datetime
import io
import re

import PyPDF2
import requests
from bs4 import BeautifulSoup


def order_date(date):
    dates = date.split('-')
    return '.'.join([dates[-1], dates[1], dates[0]])


DAYS = {0: 'E',
        1: 'T',
        2: 'K',
        3: 'N',
        4: 'R'}
NUTRITION = {0: 'kcal',
             1: 'valgud',
             2: 'rasvad',
             3: 'süsivesikud'}

DATEFROM = (datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday()))
NEXTWEEKDATEFROM = DATEFROM + datetime.timedelta(days=7)

DATEFROM = order_date(str(DATEFROM))
NEXTWEEKDATEFROM = order_date(str(NEXTWEEKDATEFROM))

USERNAME = '***REMOVED***'
PASSWORD = '***REMOVED***'
MFP_LOGIN_URL = 'https://www.myfitnesspal.com/account/login'
MFP_LOGIN_PAYLOAD = {'utf8': '✓',
                     'username': USERNAME,
                     'password': PASSWORD}

MFP_NEW_FOOD_URL = 'https://www.myfitnesspal.com/food/new'
MFP_NEW_FOOD_PAYLOAD = {'utf8': '✓',
                        'authenticity_token': None,
                        'date': None,
                        'food[brand]': None,
                        'food[description]': None,
                        'weight[serving_size]': None,
                        'servingspercontainer': None,
                        'nutritional_content[calories]': '0',
                        'nutritional_content[sodium]': '0',
                        'nutritional_content[fat]': '0',
                        'nutritional_content[potassium]': '0',
                        'nutritional_content[saturated_fat]': '0',
                        'nutritional_content[carbs]': '0',
                        'nutritional_content[polyunsaturated_fat]': '0',
                        'nutritional_content[fiber]': '0',
                        'nutritional_content[monounsaturated_fat]': '0',
                        'nutritional_content[sugar]': '0',
                        'nutritional_content[trans_fat]': '0',
                        'nutritional_content[protein]': '0',
                        'nutritional_content[cholesterol]': '0',
                        'nutritional_content[vitamin_a]': '0',
                        'nutritional_content[calcium]': '0',
                        'nutritional_content[vitamin_c]': '0',
                        'nutritional_content[iron]': '0',
                        'addtodiary': 'yes',
                        'food_entry[quantity]': '1.0',
                        'food_entry[meal_id]': None,
                        'preserve_exact_description_and_brand': 'true',
                        'continue': 'Save'}

MFP_NEW_FOOD_SUBMIT_URL = 'https://www.myfitnesspal.com/food/duplicate'
MFP_NEW_FOOD_SUBMIT_PAYLOAD = {'utf8': '✓',
                               'authenticity_token': None,
                               'date': None,
                               'food[brand]': None,
                               'food[description]': None,
                               'meal': None
                               }
MENU_URL = 'https://nrg.edu.ee/et/toitlustamine'

session = requests.session()

menu_page_response = session.get(MENU_URL)
links = BeautifulSoup(menu_page_response.text, features="html.parser").find_all('a')

menu_links = []
menu_summaries = []
for link in links:
    if DATEFROM in link.text or NEXTWEEKDATEFROM in link.text:
        if link.attrs['href'] not in menu_links:
            pdfReader = PyPDF2.PdfFileReader(io.BytesIO(session.get(link.attrs['href']).content))
            text = ''.join([pdfReader.getPage(i).extractText().replace('\n', '') for i in range(2)])
            menu_summary = {}
            i = 0
            for summary in re.findall('Kokku\\s+.*?(?=\\s{2,})', text):
                values = [float(nr.replace(',', '.')) for nr in re.search('\\s+.+', summary).group(0).strip().split()]
                nutritional_values = {}
                j = 0
                for value in values:
                    nutritional_values[NUTRITION[j]] = value
                    j += 1
                menu_summary[DAYS[i]] = nutritional_values
                i += 1
            menu_summaries.append(menu_summary)
            menu_links.append(link.attrs['href'])

login_response = session.post(MFP_LOGIN_URL, MFP_LOGIN_PAYLOAD)

nfp = session.get(MFP_NEW_FOOD_URL)
token = BeautifulSoup(nfp.text, features="html.parser").find('input', {'name': 'authenticity_token'}).attrs['value']
MFP_NEW_FOOD_SUBMIT_PAYLOAD['authenticity_token'] = token
new_food_submit_response = session.post(MFP_NEW_FOOD_SUBMIT_URL, MFP_NEW_FOOD_SUBMIT_PAYLOAD)

nfp = session.get(MFP_NEW_FOOD_URL)
token = BeautifulSoup(nfp.text, features="html.parser").find('input', {'name': 'authenticity_token'}).attrs['value']
MFP_NEW_FOOD_PAYLOAD['authenticity_token'] = token
new_food_response = session.post(MFP_NEW_FOOD_URL, MFP_NEW_FOOD_PAYLOAD)
