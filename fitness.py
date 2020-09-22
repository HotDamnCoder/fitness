import myfitnesspal
import PyPDF2
from urllib.request import urlretrieve
import datetime
from bs4 import BeautifulSoup
import bs4
import json
import re

now = datetime.datetime.now(datetime.timezone.utc)
now = str(now).split('.')[0] + 'Z'
now = now.replace(' ', 'T')
client = myfitnesspal.Client('***REMOVED***')
session = client.session
url_1 = 'https://nrg.edu.ee/et/toitlustamine'
url_2 = 'https://api.myfitnesspal.com/v2/diary'
header = {
    'authorization': 'Bearer ' + client._auth_data['access_token'],
    'mfp-client-id': 'mfp-main-js',
    'mfp-user-id': client.user_id,
    'content-type': 'application/json; charset=UTF-8'
    }
calories = 800
fat = 32
carbs = 14
sugar = 14
protein = 17
data_2 = {
    "items": [
        {
            "meal_name": "Lunch",
            "date": now.split('T')[0],
            "nutritional_contents":{
                "fat": fat,
                "carbohydrates": carbs,
                "sugar": sugar,
                "protein": protein,
                "energy": {
                    "value": calories, "unit": "calories"
                    }
            },
            "type": "quick_add"
        }

    ]
}
data_2 = json.dumps(data_2)
response = session.get(url_1)
html = BeautifulSoup(response.text, features="lxml")
a = html.find('strong')
links = [link for link in a.contents if type(link) == bs4.Tag]
links = [link for link in links if link.text != " " or link.text == ""]
links = [link.attrs['href'] for link in links]
names = [link.split('/')[-1] for link in links]
texts = []
for link, name in zip(links, names):
    urlretrieve(link, name)
for name in names:
    pdfFileObj = open(name, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    text = [pdfReader.getPage(i).extractText().replace('\n', '') for i in range(pdfReader.numPages-2)]
    pdfFileObj.close()
    texts.append(text)

pattern = r'Kokku.+?(?=\s{8})'
a = [[re.findall(pattern, a) for a in text] for text in texts]
calories = []
for x in a:
    cals = []
    for b in x:
        for y in b:
            y = y.split(',')[0]
            cals.append(re.split('\\s+?(?=\\d)', y)[1])
    calories.append(cals)
print(a)