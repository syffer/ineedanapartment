# coding: utf-8

import bs4
import datetime
import requests
import urllib.parse

import retrievers.retriever
import locs


class OuestFranceLocationRetriever(retrievers.retriever.LocationRetriever):
    def retrieve(self, criteria):
        # TODO rebuild url using some arguments
        # url = "https://www.ouestfrance-immo.com/louer/appartement--2-pieces/?lieux=18998,100177,18895,100028,100038,100150,100179,100049,100178,100053,100047,100180,100350,100353,100036,100030,100046,100042,100025,100151,100187,100033,100043,100052,19118,100045,100144,100037,19092,100156&rayon=5&prix=0_700&surface=25_0&garage=1"

        url = "https://www.ouestfrance-immo.com/louer/appartement--2-pieces/"
        params = {
            "lieux": "18998,100177,18895,100028,100038,100150,100179,100049,100178,100053,100047,100180,100350,100353,100036,100030,100046,100042,100025,100151,100187,100033,100043,100052,19118,100045,100144,100037,19092,100156",
            "rayon": "5",
        }

        if criteria.with_parking_spot:
            params["garage"] = "1"

        if criteria.max_price or criteria.min_price:
            min_price = criteria.min_price or "0"
            max_price = criteria.max_price or "0"
            params["prix"] = "{}_{}".format(min_price, max_price)

        if criteria.max_surface or criteria.min_surface:
            min_surface = criteria.min_surface or "0"
            max_surface = criteria.max_surface or "0"
            params["surface"] = "{}_{}".format(min_surface, max_surface)

        result = requests.get(url, params=params)

        soup = bs4.BeautifulSoup(result.text, features="html.parser")
        tags = soup.find_all("a", class_="annLink")

        parsed_url = urllib.parse.urlparse(url)
        base_url = "{uri.scheme}://{uri.netloc}".format(uri=parsed_url)

        locations = [create_location(base_url, tag) for tag in tags]
        locations.sort(key=lambda location: location.date, reverse=True)
        return locations


def create_location(base_url, tag):
    _id = tag.find("div", attrs={"data-id": True}).attrs["data-id"]
    title = tag.get("title")
    link = "{}{}".format(base_url, tag.get("href"))
    price = float(tag.find(class_="annPrix").text.strip().replace("€", "").replace(" ", ""))

    criteria = tag.find(class_="annCriteres").text.strip().split("|")
    surface = criteria[0].strip() if criteria else None
    others = " | ".join(criteria[1:])

    formatted_date = tag.find(class_="annDebAff").text.strip()
    date = datetime.datetime.strptime(formatted_date, "%d/%m/%y")

    return locs.Location(
        _id="ouestfrance-{}".format(_id),
        title=title,
        link=link,
        price=price,
        date=date,
        surface=surface,
        others=others,
        website="Ouest France"
    )
