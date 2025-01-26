import os
import sys
import argparse
import logging
import requests
import json
from dotenv import load_dotenv
from logging import DEBUG
import exceptions

DEFAULT_IMAGES_COUNT = 5
DEFAULT_YADISK_PATH = 'vk images'
DEFAULT_OWNER_ID = ''
DEFAULT_VERSION_API = '5.131'
DEFAULT_ALBUM_ID = ['profile']
DEFAULT_RESULT = 'result.txt'

class VK:
    def __init__(
            self,
            access_token,
            owner_id = DEFAULT_OWNER_ID,
            version = DEFAULT_VERSION_API
    ):
        self.access_token = access_token
        self.version = version
        self.owner_id = owner_id
        self.user_id = ''

    def get_user_id(self):
        """Получает id текущего пользователя"""
        if self.user_id != '':
            return self.user_id
        url = r'https://api.vk.com/method/users.get'
        params = {
            'access_token': self.access_token,
            'v': self.version
        }
        response = requests.get(url, params)
        if response.status_code != 200:
            raise exceptions.ExeptionEndpointAccessable(
                f'{url} вернул статус ответа {response.status_code}'
            )
        json = response.json()
        if type(json) != dict:
            raise exceptions.ExeptionFormatAnswer(
                f'{url} в ответе не получен словарь'
            )
        if 'response' not in json:
            raise exceptions.ExeptionValueFound(
                f'{url} в ответе не обнаружено поле response'
            )
        if type(json['response']) != list:
            raise exceptions.ExeptionFormatAnswer(
                f'{json["response"]} не является списком'
            )
        if len(json['response'])==0:
            raise exceptions.ExeptionValueFound(
                f'{json} содержит пустой список response'
            )
        if type(json['response'][0]) != dict:
            raise exceptions.ExeptionFormatAnswer(
                f'{json["response"][0]} не является словарем'
            )
        if 'id' not in json['response'][0]:
            raise exceptions.ExeptionValueFound(
                f'{json["response"][0]} не обнаружено поле id'
            )

        self.user_id = response.json()['response'][0]['id']
        return self.user_id

    def get_images(self, album_id):
        """Получает фотографии альбома по его id"""
        url = r'https://api.vk.com/method/photos.get'
        params = {
            'access_token': self.access_token,
            'v': self.version,
            'album_id': album_id,
            'extended': '1'
        }
        if self.owner_id != '':
            params['owner_id'] = self.owner_id
        elif self.get_user_id() != '':
            params['user_id'] = self.user_id
        response = requests.get(url, params)
        if response.status_code != 200:
            raise exceptions.ExeptionEndpointAccessable(
                f'{url} вернул статус ответа {response.status_code}'
            )
        json = response.json()
        if type(json) != dict:
            raise exceptions.ExeptionFormatAnswer(
                f'{url} в ответе не получен словарь'
            )
        if 'response' not in json:
            raise exceptions.ExeptionValueFound(
                f'{url} в ответе не обнаружено поле response'
            )
        if type(json['response']) != dict:
            raise exceptions.ExeptionFormatAnswer(
                f'{json["response"]} не является словарем'
            )
        if 'items' not in json['response']:
            raise exceptions.ExeptionValueFound(
                f'{json["response"]} не обнаружено поле items'
            )
        if type(json['response']['items']) != list:
            raise exceptions.ExeptionFormatAnswer(
                f'{json["response"]["items"]} не является списком'
            )
        return json['response']['items']

    def get_profile_images(self):
        """Получает фотографии профайла"""
        return self.get_images('profile')

    def get_wall_images(self):
        """Получает фотографии стены"""
        return self.get_images('wall')


class YA:
    def __init__(self, access_token):
        self.access_token = access_token
        self.folders = ['']
        self.files = []

    def put_folder(self, path):
        """Находит или создает папку по указанному пути"""
        if path in self.folders:
            return
        headers = {
            'Accept': 'Application/json',
            'Authorization': ' '.join(['OAuth', self.access_token])
        }
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': path}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            self.folders.append(path)
            return
        elif response.status_code == 404:
            response = requests.put(url, headers=headers, params=params)
            if response.status_code == 201:
                self.folders.append(path)
                return
        raise exceptions.ExeptionEndpointAccessable(
            f'Не удалось получить ресурс {path} параметры {params} статус ответа {response.status_code}'
        )

    def put_file(self, url_source, path, overwrite=True):
        """Записывает изображение по указанному пути"""
        if not overwrite and path in self.files:
            return False
        self.put_folder('/'.join(path.split('/')[:-1]))

        headers = {
            'Accept': 'Application/json',
            'Authorization': ' '.join(['OAuth', self.access_token])
        }
        response = requests.get(url_source)
        if response.status_code != 200:
            raise exceptions.ExeptionEndpointAccessable(
                f'Не удалось получить ресурс {url_source} статус ответа {response.status_code}'
            )
        content = response.content
        params = {
            'path': path,
            'overwrite': overwrite
        }
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise exceptions.ExeptionEndpointAccessable(
                f'Не удалось получить ресурс {url} параметры {params} статус ответа {response.status_code}'
            )
        json = response.json()
        if type(json) != dict:
            raise exceptions.ExeptionFormatAnswer(
                f'Ответ {json} не является словарем'
            )
        if 'href' not in json:
            raise exceptions.ExeptionValueFound(
                f'В словаре {json} не найдено поле href'
            )
        url = response.json()['href']
        response = requests.put(url, headers=headers, files={'file': content})
        if response.status_code != 201:
            raise exceptions.ExeptionEndpointAccessable(
                f'Не удалось записать ресурс {url} статус ответа {response.status_code}'
            )

        self.files.append(path)
        return True


def main():
    # Обрабатываем параметры командной строки
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--owner', default=DEFAULT_OWNER_ID)
    parser.add_argument('-c', '--count', default=DEFAULT_IMAGES_COUNT, type=int)
    parser.add_argument('-p', '--path', default=DEFAULT_YADISK_PATH)
    parser.add_argument('-a', '--album', nargs='+', default=DEFAULT_ALBUM_ID)
    parser.add_argument('-v', '--version', default=DEFAULT_VERSION_API)
    namespace = parser.parse_args(sys.argv[1:])

    # Загружаем токены в переменные окружения из файла .env
    load_dotenv()

    # Подготавливаем логирование
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] >> %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=DEBUG
    )
    logger = logging.getLogger(__name__)

    # Получаем токены
    vk_token = os.getenv('VK_TOKEN')
    if vk_token is None:
        logger.critical(
            msg='Не найдент токен для доступа ВКонтакте'
        )
    ya_token = os.getenv('YA_TOKEN')
    if ya_token is None:
        logger.critical(
            msg='Не найдент токен для доступа к Яндекс диску'
        )
    if vk_token is None or ya_token is None:
        raise exceptions.ExeptionProgramInit('Программа принудительно остановлена.')

    # Получаем список фотографий
    vk = VK(access_token=vk_token, owner_id=namespace.owner, version=namespace.version)
    images = []
    for album_id in namespace.album:
        try:
            if album_id == 'profile':
                images.extend(vk.get_profile_images())
            elif album_id == 'wall':
                images.extend(vk.get_wall_images())
            else:
                images.extend(vk.get_images(album_id))
        except Exception as error:
            logger.error(
                msg = (
                    'Ошибка при получении списка изображений'
                    f' из альбома {album_id} {error}'
                )
            )
    len_images = len(images)
    logger.info(
        msg = f'Получено {len_images} фотографий'
    )

    # pprint(images)
    if len_images == 0:
        logger.warning(
            'Фотографии для записи не найдены'
        )
        return

    try:
        images_for_save = [
            {
                'url': image['orig_photo']['url'],
                'name': f'{image["likes"]["count"]}_{image["date"]}.jpeg',
                'size': image['orig_photo']['height']*image['orig_photo']['width']
            }
            for image in sorted(
                images, key=lambda x: x['orig_photo']['height']*x['orig_photo']['width'], reverse=True
            )[:namespace.count]
        ]
    except Exception as error:
        logger.error(
            msg = f'Ошибка при обработке списка фотографий {error}'
        )
        return

    # Запись фотографий на яндекс диск
    ya = YA(access_token=ya_token)
    if namespace.path[-1] != '/':
        namespace.path += '/'
    for image in images_for_save:
        try:
            if ya.put_file(
                image['url'],
                namespace.path + image['name']
            ):
                logger.info(
                    msg = f'Загружена фотография {image["name"]}'
                )
        except Exception as error:
            logger.error(
                msg = f'Ошибка при загрузке фотографии {image} {error}'
            )
    image_for_save = [
        {
            'file_name': image['name'],
            'size': image['size']
        }
        for image in images_for_save
    ]
    with open(DEFAULT_RESULT, 'w', encoding='utf-8') as f:
        json.dump(
            fp=f, obj=image_for_save, ensure_ascii=True, indent=2
        )


if __name__=='__main__':
    main()
