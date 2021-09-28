import datetime
from bs4 import BeautifulSoup
from requests import Session, session


class MFP_API:
    LOGIN_URL = 'https://www.myfitnesspal.com/account/login'
    NEW_FOOD_URL = 'https://www.myfitnesspal.com/food/new'
    NEW_FOOD_DUPLICATE_SUBMIT_URL = 'https://www.myfitnesspal.com/food/duplicate'

    NEW_FOOD_PAYLOAD = {'utf8': '✓',
                        'authenticity_token': None,  # * Placeholder
                        'date': None,  # * Placeholder
                        'food[brand]': 'NRG',  # * Sets the food brand
                        'food[description]': None,  # * Placeholder
                        'weight[serving_size]': None,  # * Placeholder
                        'servingspercontainer': '1',
                        'nutritional_content[calories]': '0',  # * Placeholder
                        'nutritional_content[sodium]': '0',
                        'nutritional_content[fat]': '0',  # * Placeholder
                        'nutritional_content[potassium]': '0',
                        'nutritional_content[saturated_fat]': '0',
                        'nutritional_content[carbs]': '0',  # * Placeholder
                        'nutritional_content[polyunsaturated_fat]': '0',
                        'nutritional_content[fiber]': '0',
                        'nutritional_content[monounsaturated_fat]': '0',
                        'nutritional_content[sugar]': '0',
                        'nutritional_content[trans_fat]': '0',
                        'nutritional_content[protein]': '0',  # * Placeholder
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

    NEW_FOOD_DUPLICATE_SUBMIT_PAYLOAD = {'utf8': '✓',
                                         'authenticity_token': None,  # * Placeholder
                                         'date': None,  # * Placeholder
                                         # * Sets the food brand
                                         'food[brand]': 'NRG',
                                         # * Placeholder
                                         'food[description]': None,
                                         'meal': '0'  # * Sets the meal to lunch
                                         }

    def __init__(self, username: str, password: str) -> None:
        self.LOGIN_PAYLOAD = {'utf8': '✓',
                              'username': username,
                              'password': password,
                              'authenticity_token': None}

    def __login(self) -> Session:
        mfp_session = session()
        mfp_session.headers['user-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
        self.__setAuthToken(mfp_session)
        login_response = mfp_session.post(self.LOGIN_URL, self.LOGIN_PAYLOAD)

        if (login_response.status_code != 200):
            raise Exception("Failed to log in!")

        return mfp_session

    def __setFoodDate(self, date: datetime.date) -> None:
        date_str = date.strftime('%Y-%m-%d')
        self.NEW_FOOD_DUPLICATE_SUBMIT_PAYLOAD['date'] = date_str
        self.NEW_FOOD_PAYLOAD['date'] = date_str

    def __setFoodDescription(self, date: datetime.date) -> None:
        date_str = date.strftime('%Y-%m-%d')
        self.NEW_FOOD_DUPLICATE_SUBMIT_PAYLOAD['food[description]'] = date_str
        self.NEW_FOOD_PAYLOAD['food[description]'] = date_str

    def __setFoodNutrtitons(self, food_nutritions: dict[str, float]) -> None:
        calories = round(food_nutritions['calories'])
        proteins = round(food_nutritions['protein'])
        fats = round(food_nutritions['fat'])
        carbs = round(food_nutritions['carbs'])

        # ! yes i know this is wrong and idc
        weight = round(calories + proteins + fats + carbs)

        self.NEW_FOOD_PAYLOAD['nutritional_content[calories]'] = str(calories)
        self.NEW_FOOD_PAYLOAD['nutritional_content[protein]'] = str(proteins)
        self.NEW_FOOD_PAYLOAD['nutritional_content[fat]'] = str(fats)
        self.NEW_FOOD_PAYLOAD['nutritional_content[carbs]'] = str(carbs)
        self.NEW_FOOD_PAYLOAD['weight[serving_size]'] = str(weight) + 'g'

    def __setAuthToken(self, open_session: Session) -> str:
        new_food_response = open_session.get(self.LOGIN_URL)
        token = BeautifulSoup(new_food_response.text, features="html.parser").find(
            'meta', {'name': 'csrf-token'}).attrs['content']
        self.LOGIN_PAYLOAD['authenticity_token'] = token
        self.NEW_FOOD_PAYLOAD['authenticity_token'] = token
        self.NEW_FOOD_DUPLICATE_SUBMIT_PAYLOAD['authenticity_token'] = token
        return token

    def __submitNewFood(self, logged_in_session: Session) -> None:
        logged_in_session.post(self.NEW_FOOD_DUPLICATE_SUBMIT_URL,
                               self.NEW_FOOD_DUPLICATE_SUBMIT_PAYLOAD)

    def __addNewFood(self, logged_in_session: Session) -> None:
        logged_in_session.post(self.NEW_FOOD_URL, self.NEW_FOOD_PAYLOAD)

    def addFood(self, date: datetime.date, food_nutritions: dict[str, float]) -> None:
        logged_in_session = self.__login()
        self.__setFoodDate(date)
        self.__setFoodDescription(date)
        self.__setFoodNutrtitons(food_nutritions)
        self.__submitNewFood(logged_in_session)
        self.__addNewFood(logged_in_session)
        logged_in_session.close()
