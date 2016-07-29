import re
import scrapy

from ..import items
from lxml import html

import plotly.plotly as py
import plotly.graph_objs as go

from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher



class Mobile_Data(scrapy.Spider):
    items = []
    name = "games_rating"
    domain = 'https://play.google.com/store'
    start_urls = ['https://play.google.com/store/apps/top/category/GAME?hl=en']

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        """
        Visualizing the scraped data after spider has been closed
        :param spider:
        :return:
        """
        name_list = []
        rating = []
        for item in self.items:
            name_list.append(item['name'])
            rating.append(item['rating_percentage'])

        fig = {
              'data': [{'labels': name_list[:10],
              'values': rating[:10],
              'type': 'pie'}],
              'layout': {'title': 'Top rated games in Google playstore'}
               }

        py.plot(fig)


    def parse(self, response):
        """
        Parse and yields games rating of googe play store
        :param response:
        :return:
        """
        doc = html.fromstring(response.body)
        games_list = self.parse_games_list(doc)
        for game in games_list:
            rating = self.parse_game_rating(game)
            game_name = self.parse_games_name(game)
            item = items.GamesRatingItem()
            item['name'] = game_name
            item['rating_percentage'] = re.search(r'width: (.+?)%', rating).group(1)
            self.items.append(item)
            yield item

    def parse_games_list(self, doc):
        """
        parse whole games details from google play store
        :param doc:
        :return list of Games details:
        """
        games_list = doc.xpath('.//div[@class="card-content id-track-click id-track-impression"]')
        return games_list

    def parse_game_rating(self, game_data):
        """
        parse rating of each games
        :param game_data:
        :return games rating as list:
        """
        rating = game_data.xpath('.//div[@class="reason-set"]//div[@class="current-rating"]/@style')
        return rating[0]

    def parse_games_name(self, game_data):
        """
        Parse name of each game
        :param game_data:
        :return games name as list:
        """
        name = game_data.xpath('.//div[@class="details"]//a[@class="title"]/@title')
        return name[0]