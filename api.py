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

    def get_profile_images(self):
        return self.get_images('profile')

    def get_wall_images(self):
        return self.get_images('wall')


class YA:
    def __init__(self, access_token = ''):
        self.access_token = access_token
        self.folders = ['']
        self.files = []

    def put_folder(self, path):
        if path in self.folders:
            return True
        headers = {
            'Accept': 'Application/json',
            'Authorization': ' '.join(['OAuth', self.access_token])
        }
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': path}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            self.folders.append(path)
            return True
        elif response.status_code == 404:
            response = requests.put(url, headers=headers, params=params)
            if response.status_code == 201:
                self.folders.append(path)
                return True
            else:
                return False
        else:
            return False

    def put_file(self, url_source, path, overwrite=True):
        if not overwrite and path in self.files:
            return False
        if not self.put_folder('/'.join(path.split('/')[-1])):
            return False
        headers = {
            'Accept': 'Application/json',
            'Authorization': ' '.join(['OAuth', self.access_token])
        }
        response = requests.get(url_source)
        if response.status_code != 200:
            return False
        content = response.content
        params = {
            'path': path,
            'overwrite': overwrite
        }
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            url = response.json()['href']
            response = requests.put(url, headers=headers, files={'file': content})
            if response.status_code != 201:
                return False
        else:
            return False
        self.files.append(path)
        return True


def main():
    load_dotenv()
    vk = VK(access_token=os.getenv('VK_TOKEN'), owner_id='31562476')
    images = vk.get_images(album_id='247976091')
    pprint(images)
    ya = YA(access_token=os.getenv('YA_TOKEN'))
    if ya.put_folder('vk images/123/'):
        ya.put_file(images[0]['orig_photo']['url'],'vk images/123/1.jpeg')


if __name__=='__main__':
    main()