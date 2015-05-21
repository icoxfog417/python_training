class Cheer():

    def __init__(self, cheer_json):
        _get = lambda d, k: "" if k not in d else d[k]

        photo = cheer_json["photo"]

        self.id = _get(photo, "vote_id")
        self.menu_id = _get(photo, "menu_id")
        self.menu_name = _get(photo, "menu_name")
        self.menu_finish_flag = True if _get(photo, "menu_finish_flag") == 0 else False
        self.images = []
        if "image_url" in photo:
            for im in photo["image_url"].values():
                self.images.append(im)

    def __str__(self):
        text = "{0}:{1} {2}".format(self.id, self.menu_id, self.menu_name)
        return text
