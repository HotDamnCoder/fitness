import PyPDF2
import requests
from bs4 import BeautifulSoup

MFP_LOGIN_URL = 'https://www.myfitnesspal.com/account/login'
MFP_LOGIN_PAYLOAD = {'utf8': '✓',
                     'authenticity_token': '',
                     'username': '***REMOVED***',
                     'password': '***REMOVED***',
                     'remember_me': '1'}
MFP_NEW_FOOD_URL = 'https://www.myfitnesspal.com/food/new'
MFP_NEW_FOOD_PAYLOAD = {'utf8': '✓',
                        'authenticity_token': '',
                        'date': '2020-10-03',
                        'food[brand]': 'Generic',
                        'food[description]': 'sssasa',
                        'weight[serving_size]': '100g',
                        'servingspercontainer': '1',
                        'nutritional_content[calories]': '750',
                        'nutritional_content[sodium]': '',
                        'nutritional_content[fat]'':'','
                        'nutritional_content[potassium]': '',
                        'nutritional_content[saturated_fat]': '',
                        'nutritional_content[carbs]': '',
                        'nutritional_content[polyunsaturated_fat]': '',
                        'nutritional_content[fiber]': '',
                        'nutritional_content[monounsaturated_fat]': '',
                        'nutritional_content[sugar]': '',
                        'nutritional_content[trans_fat]': '',
                        'nutritional_content[protein]': '',
                        'nutritional_content[cholesterol]': '',
                        'nutritional_content[vitamin_a]': '',
                        'nutritional_content[calcium]': '',
                        'nutritional_content[vitamin_c]': '',
                        'nutritional_content[iron]': '',
                        'addtodiary': 'yes',
                        'food_entry[quantity]': '1.0',
                        'food_entry[meal_id]': '1',
                        'preserve_exact_description_and_brand': 'true',
                        'continue': 'Save'}
MENU_URL = 'https://nrg.edu.ee/et/toitlustamine'

session = requests.session()

login_page = session.get(MFP_LOGIN_URL)
auth_token = BeautifulSoup(login_page.text, features="html.parser").find('input', {'name': 'authenticity_token'}).attrs[
    'value']
MFP_LOGIN_PAYLOAD['authenticity_token'] = auth_token
login_response = session.post(MFP_LOGIN_URL, MFP_LOGIN_PAYLOAD)
new_food_page = session.get(MFP_NEW_FOOD_URL)
auth_token = BeautifulSoup(new_food_page.text, features="html.parser").find('input', {'name': 'authenticity_token'}).attrs['value']
MFP_NEW_FOOD_PAYLOAD['authenticity_token'] = auth_token
new_food_response = session.post(MFP_NEW_FOOD_URL, MFP_NEW_FOOD_PAYLOAD)
"""
url_2 = 'https://api.myfitnesspal.com/v2/diary'
header = {
    'authorization': 'Bearer ' + client._auth_data['access_token'],
    'mfp-client-id': 'mfp-main-js',
    'mfp-user-id': client.user_id,
    'content-type': 'application/json; charset=UTF-8'
    }
"""
