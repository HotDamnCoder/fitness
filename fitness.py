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
                        'food[brand]': 'NRG',
                        'food[description]': None,
                        'weight[serving_size]': None,
                        'servingspercontainer': '1',
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
                        'food_entry[meal_id]': '1',
                        'preserve_exact_description_and_brand': 'true',
                        'continue': 'Save'}

MFP_NEW_FOOD_SUBMIT_URL = 'https://www.myfitnesspal.com/food/duplicate'
MFP_NEW_FOOD_SUBMIT_PAYLOAD = {'utf8': '✓',
                               'authenticity_token': None,
                               'date': None,
                               'food[brand]': 'NRG',
                               'food[description]': None,
                               'meal': '0'
                               }
CATERING_PAGE_URL = 'https://nrg.edu.ee/et/toitlustamine'

session = requests.session()

catering_page = session.get(CATERING_PAGE_URL)
links_from_catering_page = BeautifulSoup(catering_page.text, features="html.parser").find_all('a')

menu_links = []
weekly_menu_summaries = {}
for link in links_from_catering_page:
    if DATEFROM in link.text or NEXTWEEKDATEFROM in link.text:
        link_url = link.attrs['href']
        if link_url not in menu_links:
            menuPDFReader = PyPDF2.PdfFileReader(io.BytesIO(session.get(link_url).content))
            menu_text = ''.join([menuPDFReader.getPage(i).extractText().replace('\n', '') for i in range(2)])
            week_menu_summary = {}
            day_count = 0
            for summary in re.findall('Kokku\\s+.*?(?=\\s{2,})', menu_text):
                nuts = [float(nr.replace(',', '.')) for nr in re.search('\\s+.+', summary).group(0).strip().split()]
                menu_nutritional_values = {}
                nut_count = 0
                for value in nuts:
                    menu_nutritional_values[NUTRITION[nut_count]] = value
                    nut_count += 1
                week_menu_summary[DAYS[day_count]] = menu_nutritional_values
                day_count += 1
            weekly_menu_summaries[link.text] = week_menu_summary
            menu_links.append(link_url)

session.post(MFP_LOGIN_URL, MFP_LOGIN_PAYLOAD)

for week_menu_summary in weekly_menu_summaries:
    day_count = 0
    for day in weekly_menu_summaries[week_menu_summary]:
        link_start_date = week_menu_summary.split('-')[0].strip()
        date = (datetime.datetime.strptime(link_start_date, '%d.%m.%Y') + datetime.timedelta(days=day_count)).date()

        day_menu = weekly_menu_summaries[week_menu_summary][day]
        kcal = round(day_menu['kcal'])
        protein = round(day_menu['valgud'])
        fat = round(day_menu['rasvad'])
        carbohydrates = round(day_menu['süsivesikud'])
        weight = round(kcal + protein + fat + carbohydrates)

        MFP_NEW_FOOD_SUBMIT_PAYLOAD['food[description]'] = str(date)
        MFP_NEW_FOOD_SUBMIT_PAYLOAD['date'] = str(date)
        MFP_NEW_FOOD_PAYLOAD['date'] = str(date)
        MFP_NEW_FOOD_PAYLOAD['nutritional_content[calories]'] = str(kcal)
        MFP_NEW_FOOD_PAYLOAD['nutritional_content[protein]'] = str(protein)
        MFP_NEW_FOOD_PAYLOAD['nutritional_content[fat]'] = str(fat)  # yes
        MFP_NEW_FOOD_PAYLOAD['nutritional_content[carbs]'] = str(carbohydrates)
        MFP_NEW_FOOD_PAYLOAD['weight[serving_size]'] = str(weight) + 'g'
        MFP_NEW_FOOD_PAYLOAD['food[description]'] = str(date)

        nfp = session.get(MFP_NEW_FOOD_URL)
        token = BeautifulSoup(nfp.text, features="html.parser").find('input', {'name': 'authenticity_token'}).attrs['value']
        MFP_NEW_FOOD_SUBMIT_PAYLOAD['authenticity_token'] = token
        new_food_submit_response = session.post(MFP_NEW_FOOD_SUBMIT_URL, MFP_NEW_FOOD_SUBMIT_PAYLOAD)

        nfp = session.get(MFP_NEW_FOOD_URL)
        token = BeautifulSoup(nfp.text, features="html.parser").find('input', {'name': 'authenticity_token'}).attrs['value']
        MFP_NEW_FOOD_PAYLOAD['authenticity_token'] = token
        new_food_response = session.post(MFP_NEW_FOOD_URL, MFP_NEW_FOOD_PAYLOAD)

        day_count += 1


