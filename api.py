import os
import requests
from dotenv import load_dotenv
from pprint import pprint


class VK:
    def __init__(self, access_token = '', owner_id = '', version = '5.131'):
        self.access_token = access_token
        self.version = version
        self.owner_id = owner_id
        self.user_id = ''

    def get_user_id(self):
        if self.user_id != '':
            return self.user_id
        url = r'https://api.vk.com/method/users.get'
        params = {
            'access_token': self.access_token,
            'v': self.version
        }
        response = requests.get(url, params)
        if response.status_code == 200:
            json = response.json()
            if 'response' in json:
                self.user_id = response.json()['response'][0]['id']
                return self.user_id
        return ''

    def get_images(self, album_id):
        url = r'https://api.vk.com/method/photos.get'
        params = {
            'access_token': self.access_token,
            'v': self.version,
            'album_id': album_id
        }
        if self.owner_id != '':
            params['owner_id'] = self.owner_id
        elif self.get_user_id() != '':
            params['user_id'] = self.user_id
        response = requests.get(url, params)
        if response.status_code == 200:
            json = response.json()
            if 'response' in json and json['response']['count'] > 0:
                return json['response']['items']
        return []

    def upload_image(self, url):
        params = {

        }


class YA:
    def __init__(self):
        ...

    def put_folder(self):
        ...

    def put_file(self):
        ...


def main():
    load_dotenv()
    vk = VK(access_token=os.getenv('VK_TOKEN'), owner_id='31562476')
    images = vk.get_images(album_id='247976091')
    pprint(images)


if __name__=='__main__':
    main()