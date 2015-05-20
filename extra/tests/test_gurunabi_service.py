# -*- coding: utf-8 -*-
import unittest
from extra.gurunabi_service import GurunabiService, Restaurant


class TestGurunabiService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = GurunabiService()

    def test_search(self):
        restaurants = self.service.search("和食")
        self.assertTrue(len(restaurants) > 0)
        print(restaurants[0])

    def test_search_by_english(self):
        restaurants = self.service.search(["sushi", "dinner"])
        self.assertTrue(len(restaurants) > 0)
        print(restaurants[0])

    def test_search_with_prefecture(self):
        restaurants = self.service.search("日本酒", 12)  # 12: 千葉県
        self.assertTrue(len(restaurants) > 0)
        self.assertTrue("千葉県" in restaurants[0].address)
        print(str(restaurants[0]) + "@" + restaurants[0].address)

    def test_show_restaurants(self):
        restaurants = self.service.search("和食")
        Restaurant.show_restaurants_page(restaurants)
