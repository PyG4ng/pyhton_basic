from datetime import datetime

import requests
from tqdm import tqdm

VERSION = 5.131
URI = 'https://api.vk.com/method/'
API_KEY = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'


class Vk:
    def __init__(self, user_id=None):
        response = self._send_request_to_api(user_id)
        self.name = response.get("first_name")
        self.last_name = response.get("last_name")
        self.birthdate = response.get("bdate")
        self.id = response.get("id")
        self.domain = response.get("domain")
        self.picture = response.get("photo_max_orig")

    def __str__(self):
        return f'Name: {self.name} {self.last_name}\nBirth Date: {self.birthdate}\nId: {self.id}\n' \
               f'Ссылка: https://vk.com/{self.domain}\nProfile picture: {self.picture}'

    @staticmethod
    def _get_parameters():
        return {
            'access_token': API_KEY,
            'v': VERSION
        }

    def _send_request_to_api(self, user_id):
        """
        Sends a request to the sever to get user's information on vk.com
        Args:
            user_id: user id on vk, default value will be None

        Returns: The first result

        """
        method = 'users.get'
        parameters = self._get_parameters()
        parameters['user_ids'] = user_id
        parameters['fields'] = 'domain, bdate, photo_max_orig'
        response = requests.get(f'{URI}{method}', params=parameters)
        response.raise_for_status()
        if response.status_code == 200:
            return response.json().get("response")[0]
        return 'Ошибка!'

    def get_friends_list(self):
        """
        Gets user's friend's list on vk if access granted
        Returns: A set of users id

        """
        method = 'friends.get'
        parameters = self._get_parameters()
        parameters['user_id'] = self.id
        parameters['fields'] = 'domain, lists'
        response = requests.get(f'{URI}{method}', params=parameters)
        response.raise_for_status()
        if response.status_code == 200:
            friends_id = []
            if response.json().get('response'):
                for item in tqdm(response.json().get('response').get('items'),
                                 desc=f'Getting {self.name} friends list'):
                    friends_id.append(item.get('id'))
                return set(friends_id)
            elif response.json().get('error'):
                return f"{response.json().get('error').get('error_msg')}. Can't access {self.name}'s friends list."
        return 'Error!'

    def __and__(self, other):
        if isinstance(other, Vk):
            friends_list = self.get_friends_list()
            other_friends_list = other.get_friends_list()
            if not isinstance(friends_list, set):
                return f"Error! Can't access {self.name} friend's list"
            elif not isinstance(other_friends_list, set):
                return f"Error! Can't access {other.name} friend's list"
            else:
                if friends_list & other_friends_list == set():
                    return 'No common friends'
                return friends_list & other_friends_list
        return f'Error! "{other}" is not instance of class Vk'

    def _get_photos_requests(self, album, count):
        """
        Sends a request to get user's album pictures
        Args:
            album (str): 'profile' or 'wall'
            count (int):  Positive number, number of picture to get, max 100

        Returns: Server response in json format

        """
        method = 'photos.get'
        parameters = self._get_parameters()
        parameters = {**parameters,
                      "album_id": album,
                      "photo_sizes": 1,
                      "extended": 1,
                      "owner_id": self.id,
                      "rev": 1,
                      "count": count}
        response = requests.get(f'{URI}{method}', params=parameters)
        response.raise_for_status()
        if response.status_code == 200:
            return response.json()
        return 'Error!'

    @staticmethod
    def _get_extension(url):
        """Gets file's extension from his url"""
        r = requests.get(url)
        r.raise_for_status()
        if r.status_code == 200:
            return r.headers.get("content-type").split("/")[1]
        return 'jpg'

    def _images_characteristics(self, size, _item):
        return {"file": f'{_item.get("likes").get("count")}.{self._get_extension(size.get("url"))}',
                "ype": size.get("type"),
                "date": datetime.utcfromtimestamp(_item.get("date")).strftime('%d-%b-%Y_%H_%M_%S'),
                "likes": _item.get("likes").get("count"),
                "comments": _item.get("comments").get("count"),
                "url": size.get("url")}

    def _get_biggest_picture_size(self, _sizes, _item):
        """Method to help get the picture with the highest width and height """

        for size in _sizes:
            if size.get("type") == 'w':
                return self._images_characteristics(size, _item)

        for size in _sizes:
            if size.get("type") == 'z':
                return self._images_characteristics(size, _item)

        for size in _sizes:
            if size.get("type") == 'y':
                return self._images_characteristics(size, _item)

        for size in _sizes:
            if size.get("type") == 'x':
                return self._images_characteristics(size, _item)

    def _get_pictures(self, album, count):
        """
        Takes the server's response to get user's album pictures, find the pictures with highest
        resolution ( width x height) and returns a list of pictures
        Args:
            album (str): 'profile' or 'wall'
            count (int): Positive number, number of picture to get, max 100

        Returns:  a list of pictures

        """
        pictures = []
        r = self._get_photos_requests(album, count)
        if r.get("response"):
            items = r.get("response").get("items")
            for item in tqdm(items, desc=f'Getting {self.name} {album} pictures: '):
                sizes = item.get("sizes")
                pictures.append(self._get_biggest_picture_size(sizes, item))
            return pictures
        elif r.get("error"):
            print(r.get("error").get('error_msg'), f".You don't have access to {album} pictures!")
            return []
        elif r == 'Error!':
            return r

    def get_profile_pictures(self, album="profile", count=5):
        """
        Gets user's profile pictures.
        Args:
            album (str): 'profile'
            count (int): Positive number, number of picture to get, default value 5, max 100

        Returns: A list of user's profile pictures.

        """
        profile_pictures = []
        profile_pictures.extend(self._get_pictures(album, count))
        return profile_pictures

    def get_wall_pictures(self, album="wall", count=5):
        """
        Gets user's wall pictures.
        Args:
            album (str): 'wall'
            count (int): Positive number, number of picture to get, default value 5, max 100

        Returns: A list of user's wall pictures.

        """
        wall_pictures = []
        wall_pictures.extend(self._get_pictures(album, count))
        return wall_pictures
