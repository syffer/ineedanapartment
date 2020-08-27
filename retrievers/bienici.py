# coding: utf-8

import bs4
import dateparser
import re
import urllib.parse

import retrievers.retriever
import locs


import requests


class ApiBienIciLocationRetriever(retrievers.retriever.LocationRetriever):

    def retrieve(self, criteria):
        url = "https://www.bienici.com/realEstateAds.json"
        params = {
            "filter": {"size": 24, "from": 0, "filterType": "rent", "propertyType": ["house", "flat"], "maxPrice": 700,
                       "minRooms": 1, "maxRooms": 4, "minArea": 25, "hasParking": True, "page": 1, "resultsPerPage": 24,
                       "maxAuthorizedResults": 2400, "sortBy": "publicationDate", "sortOrder": "desc",
                       "onTheMarket": [True], "showAllModels": False, "zoneIdsByTypes": {"zoneIds": ["-59874"]}},
            "extensionType": "extendedIfNoResult",
            "leadingCount": "",
            "access_token": "jXUxozUjL5gc9zqN/DyGG/KNMd0Oz4pKQL0c7n44ySc=:5f3fbdfa2e1e6b00b5195aa9",
            "id": "5f3fbdfa2e1e6b00b5195aa9",
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        ads = data["realEstateAds"]
        nantes = [
            ad
            for ad in ads
            if ad.get("postalCode", None) == "44000"
        ]
        print(nantes)

        return set()


class BienIciLocationRetriever(retrievers.retriever.LocationRetriever):

    def __init__(self, browser):
        self.browser = browser

    def retrieve(self, criteria):
        url = "https://www.bienici.com/recherche/location/nantes-44000/de-1-a-4pieces"
        # ?prix-max=700&surface-min=25&parking=oui&tri=publication-desc&camera=13_-1.5637904_47.2292285_0.9_0

        params = {
            "prix-min": criteria.min_price,
            "prix-max": criteria.max_price,
            "surface-min": criteria.min_surface,
            "surface-max": criteria.max_surface,
            "parking": "oui" if criteria.with_parking_spot else None,
            "tri": "publication-desc",
        }
        params = {key: value for key, value in params.items() if value is not None}

        self.browser.load_page(url=url, params=params)
        print("page loaded")

        # wait for the web page to be loaded
        # .. warning:: some times the web page will take way too much time to load
        self.browser.wait_for("#searchResultsContainerList", timeout=10)
        self.browser.click_on_element("div.listResults")
        self.browser.wait_for("article.sideListItem", timeout=10)

        # parsing the items
        html = self.browser.get_page()

        soup = bs4.BeautifulSoup(html, features="html.parser")
        tags = soup.find_all("article", class_="sideListItem")

        parsed_url = urllib.parse.urlparse(url)
        base_url = "{uri.scheme}://{uri.netloc}".format(uri=parsed_url)

        print(len(tags))
        return [create_location(base_url, tag) for tag in tags]


def create_location(base_url, tag):
    _id = tag.attrs["data-id"]

    formatted_title = tag.find(class_="descriptionTitle").find(text=True, recursive=False)
    formatted_title = formatted_title.replace(u'\xa0', u' ').strip()
    match = re.match(r"(?P<title>.* )(?P<surface>\d+)\s?m²", formatted_title)

    surface = match.group("surface") if match else "unknown"

    title = match.group("title") if match else formatted_title
    localisation = tag.find(class_="descriptionTitleAddress").text.strip()
    title = "{} {}".format(title, localisation)

    link = "{}{}".format(base_url, tag.find(class_="detailedSheetLink").get("href"))

    price = tag.find(class_="thePrice").text.strip().replace("€", "").strip()

    formatted_date = tag.find(class_="photoPublicationDate").get("title")
    date = dateparser.parse(formatted_date)

    website = "bienici"
    return locs.Location(
        _id="bienici-{}".format(_id),
        title=title,
        date=date,
        link=link,
        price=price,
        surface=surface,
        website=website
    )
