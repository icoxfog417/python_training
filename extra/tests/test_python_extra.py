# -*- coding: utf-8 -*-
import unittest
from extra.models import Restaurant
from extra.gurunabi_service import GurunabiService


class TestGurunabiService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = GurunabiService()

    def test_assignment1(self):
        print("1. search restaurants")
        restaurants = self.service.search("和食")
        self.assertTrue(len(restaurants) > 0)
        print(restaurants[0])

    def test_assignment2(self):
        print("2. search restaurants by multi language")
        restaurants = self.service.search(["sushi", "dinner"])
        self.assertTrue(len(restaurants) > 0)
        print(restaurants[0])

    def test_assignment3(self):
        print("3. filter the result by prefecture")
        restaurants = self.service.search("日本酒", 12)  # 12: 千葉県
        self.assertTrue(len(restaurants) > 0)
        self.assertTrue("千葉県" in restaurants[0].address)
        print(str(restaurants[0]) + "@" + restaurants[0].address)

    def test_assignment4(self):
        print("4. get shop's cheers by parallel")
        restaurants = self.service.search("洋食")
        cheers = []
        for r in restaurants:
            if len(r.cheers) > 0:
                cheers = r.cheers
        self.assertTrue(len(cheers) > 0)
        for c in cheers:
            print(c)

    def test_assignment5(self):
        print("5. show result on browser")
        restaurants = self.service.search("和食")
        Restaurant.show_restaurants_page(restaurants)
