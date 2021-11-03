import io
import requests
import re
from PyPDF2 import PdfFileReader
from bs4 import BeautifulSoup


class Catering:
    NUTRITION = {0: 'calories',
                 1: 'protein',
                 2: 'fat',
                 3: 'carbs'}

    CATERING_PAGE_URL = 'https://nrg.edu.ee/et/toitlustamine'

    def __getCateringPage(self) -> str:
        catering_session = requests.session()
        catering_page = catering_session.get(self.CATERING_PAGE_URL)
        catering_session.close()
        return catering_page.text

    def __getCateringPageLinks(self, catering_page: str) -> list:
        catering_page_links = BeautifulSoup(
            catering_page, features="html.parser").find_all('a')
        return catering_page_links

    def __getMenuPDF(self, menu_link: str) -> PdfFileReader:
        menu_session = requests.session()
        menu_pdf = PdfFileReader(io.BytesIO(
            menu_session.get(menu_link).content))
        menu_session.close()
        return menu_pdf

    def __extractLunchMenuText(self, menu_pdf: PdfFileReader) -> str:
        #! a fucky wucky one liner for getting lunch menu text. Dont touch it!
        #! Extracts the first two pdf pages text and joins them together.
        #! From each pages text newlines are replaced with whitespaces for easier regex use.

        return ''.join([menu_pdf.getPage(i).extractText().replace('\n', '') for i in range(2)])

    def __getDayNutrtionalValues(self, day_summary: str) -> dict[str, float]:
        day_nutritional_values = {}

        summary_values = [float(value.replace(',', '.'))
                          for value in re.findall(r'[\d,]{1,}', day_summary)]

        nutritional_index = 0

        # * Nutrional values are in this order 'kcal', 'protein', 'fat', 'carbs'
        for value in summary_values:
            day_nutritional_values[self.NUTRITION[nutritional_index]] = value
            nutritional_index += 1

        return day_nutritional_values

    def __getMenuSummary(self, menu: str) -> list[dict[str, float]]:
        # * Menus are ordered from Monday to Friday (Monday is index 0 and friday is 4)
        menu_summary = []

        for day_summary in re.findall(r'Kokku\s+.*?(?=\s{3,})', menu):
            menu_summary.append(self.__getDayNutrtionalValues(day_summary))

        return menu_summary

    def getMenus(self) -> dict[str, list[dict[str, float]]]:
        #! The catering site has two links for each menu - one hidden and one seen
        #! So to not get duplicates i put already used menu links in a list and check if its already there
        #! if it is then i know i have processed the menu
        used_menu_links = []
        weekly_menu_summaries = {}

        catering_page_links = self.__getCateringPageLinks(
            self.__getCateringPage())
        for link in catering_page_links:
            # * if links text matches format like: '20.09 - 24.09.2021'
            if re.match(r'[\d\.]* - [\d\.]*', link.text):
                menu_link = link.attrs['href']
                if menu_link not in used_menu_links:
                    menu_start_date = link.text.split(' - ')[0]
                    menu_summary = self.__getMenuSummary(
                        self.__extractLunchMenuText(self.__getMenuPDF(menu_link)))
                    weekly_menu_summaries[menu_start_date] = menu_summary
                    used_menu_links.append(menu_link)

        return weekly_menu_summaries
