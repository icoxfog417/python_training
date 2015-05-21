import webbrowser


class Restaurant():

    CHEERS_LIMIT = 3

    def __init__(self, restaurant_json):
        _get = lambda d, k: "" if k not in d else d[k]

        self.id = _get(restaurant_json, "id")
        self.address = _get(restaurant_json, "address")
        self.url = _get(restaurant_json, "url")
        self.images = []
        if "image_url" in restaurant_json:
            self.images.append(_get(restaurant_json["image_url"], "shop_image1"))
            self.images.append(_get(restaurant_json["image_url"], "shop_image2"))
            # when multi langu api, image_url name is  thumbnail
            self.images.append(_get(restaurant_json["image_url"], "thumbnail"))
            self.images = [im for im in self.images if im]

        self.name = ""
        self.name_kana = ""
        self.name_sub = ""

        if isinstance(restaurant_json["name"], str):
            self.name = restaurant_json["name"]
            self.name_kana = restaurant_json["name_kana"]
        else:
            names = restaurant_json["name"]
            self.name = names["name"]
            if "name_sub" in names:
                self.name_sub = names["name_sub"]
            else:
                self.name_kana = names["name_kana"]

        self.cheers = []

    def __str__(self):
        sub_text = self.name_kana
        if not sub_text:
            sub_text = self.name_sub

        return "{0}({1})".format(self.name, sub_text)

    @classmethod
    def show_restaurants_page(cls, restaurants):
        page_template = """
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <link rel="stylesheet" type="text/css" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css">
        </head>
        <body>
            <div class="container">{0}</div>
        </body>
        </html>"""

        item_template = """
        <div class="row">
            <h3><a href="{0}" target="_blank">{1}</a></h3>
            <div class="col-md-4">
                <img src="{2}" alt="shop_image" class="img-thumbnail" style="max-height: 200px;"/>
            </div>
            <div class="col-md-8">
                {3}
                <br style='clear:both'/>
            </div>
        </div>
        """

        cheer_image = """
        <div style="float:left"><img src="{0}" style="max-height: 100px; margin-left:10px"/></div>
        """

        item_descriptions = []
        for r in restaurants:
            cheers = [cheer_image.format(c.images[-1]) for c in r.cheers]
            desc = item_template.format(r.url, r.name, "" if len(r.images) == 0 else r.images[0], "".join(cheers))
            item_descriptions.append(desc)

        html = page_template.format("".join(item_descriptions))
        with open("restaurants.html", "w", encoding="utf-8") as page:
            page.write(html)
        webbrowser.open_new_tab("restaurants.html")

