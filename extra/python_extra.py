# -*- coding: utf-8 -*-
import os
import sys
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from extra.models import Restaurant
from extra.gurunabi_service import GurunabiService

PREFECTURES = """
01：北海道
02：青森県 03：岩手県 04：宮城県 05：秋田県 06：山形県 07：福島県
08：茨城県 09：栃木県 10：群馬県 11：埼玉県 12：千葉県 13：東京都 14：神奈川県
15：新潟県 16：富山県 17：石川県 18：福井県 19：山梨県 20：長野県
21：岐阜県 22：静岡県 23：愛知県 24：三重県
25：滋賀県 26：京都府 27：大阪府 28：兵庫県 29：奈良県 30：和歌山県
31：鳥取県 32：島根県 33：岡山県 34：広島県 35：山口県
36：徳島県 37：香川県 38：愛媛県 39：高知県
40：福岡県 41：佐賀県 42：長崎県 43：熊本県 44：大分県 45：宮崎県 46：鹿児島県 47：沖縄県
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="search restaurants from Gurunabi")
    parser.add_argument("keywords", type=str, nargs="*", help="search keywords")
    parser.add_argument("--pref", type=int, default=-1, help="prefecture code (JIS X0401)")
    parser.add_argument("--pref_list", action="store_const", const=True,
                        help="show prefecture codes (not execute program)")
    parser.add_argument("--web", action="store_const", const=True, help="show result on browser")
    args = parser.parse_args()

    if args.list_pref:
        print(PREFECTURES)
        sys.exit(0)

    service = GurunabiService()
    restaurants = service.search(args.keywords, args.pref)
    if args.web:
        Restaurant.show_restaurants_page(restaurants)
    else:
        for r in restaurants:
            print(r)
