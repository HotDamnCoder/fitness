from ast import Try
import datetime
from datetime import datetime as dt
from MFP_API import MFP_API
from Menu import Catering


USERNAME = '***REMOVED***'
PASSWORD = '***REMOVED***'


catering = Catering()
mfp_api = MFP_API(USERNAME, PASSWORD)

weekly_menu_summaries = catering.getMenus()

for menu_start_date in weekly_menu_summaries:
    day_count = 0
    week_menu = weekly_menu_summaries[menu_start_date]

    for day_nutritions in week_menu:

        #! ik this is bad but im too lazy to implement a smarter way to do this
        try:
            date = dt.strptime(menu_start_date, '%d.%m')
        except ValueError:
            try:
                date = dt.strptime(menu_start_date, '%d.%m.%y')
            except ValueError:
                date = dt.strptime(menu_start_date, '%d.%m.%Y')

        date = date.replace(year=dt.today().year)
        date = (date + datetime.timedelta(days=day_count)).date()

        mfp_api.addFood(date, day_nutritions)
        day_count += 1

