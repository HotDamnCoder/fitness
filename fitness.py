import PyPDF2
import requests
from bs4 import BeautifulSoup

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

login_response = session.post(MFP_LOGIN_URL, MFP_LOGIN_PAYLOAD)

nfp = session.get(MFP_NEW_FOOD_URL)
token = BeautifulSoup(nfp.text, features="html.parser").find('input', {'name': 'authenticity_token'}).attrs['value']
MFP_NEW_FOOD_SUBMIT_PAYLOAD['authenticity_token'] = token
new_food_submit_response = session.post(MFP_NEW_FOOD_SUBMIT_URL, MFP_NEW_FOOD_SUBMIT_PAYLOAD)

nfp = session.get(MFP_NEW_FOOD_URL)
token = BeautifulSoup(nfp.text, features="html.parser").find('input', {'name': 'authenticity_token'}).attrs['value']
MFP_NEW_FOOD_PAYLOAD['authenticity_token'] = token
new_food_response = session.post(MFP_NEW_FOOD_URL, MFP_NEW_FOOD_PAYLOAD)
