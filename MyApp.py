import os, json, requests, time
from pprint import pprint

# ЗАГРУЖАЕМ В ПЕРЕМЕННЫЕ ТОКЕНы из файла token
# в формате 
# 1 строка токен VK
# 2 строка токен YA
with open('token', 'r') as file_tok:
    vk_access_token = file_tok.readline()
    ya_token = file_tok.readline()
    # user_id = id.replace('\n','')
user_id = 689086032
# user_id = 10277654
# user_id = 9297810
# user_id = str(input('Введите id пользователя VK \nфото которого вы хотелибы загрузить например 689086032:\n'))
album_id = 'profile'
# id_album = int(input('Введите идентификатор альбома VK пользователя\n1. profile — фотографии профиля (по умолчанию)\n2. wall — фотографии со стены,\n3. saved — сохраненные фотографии\n'))
# if id_album == 2:
#     album_id = 'wall'
# elif id_album == 3:
#     album_id = 'saved'
# elif id_album != 1:
#     print('неправильный идентификатор альбома, загружаем фото из профиля')  

def my_progress_bar(step: bytes, symvol: str ='-', max_length: int = 64, pause: float = 0.02) -> None:
    """ рисуем прогресс бар по переменной 'step' в качестве движка использеутся символв symvol по умолчанию символ - """
    step_size = step / max_length
    graf_string = ''
    for i in range(1, max_length + 1):
        print(f'\r[{int(i*step_size / step * 100)}] % {graf_string}', end='')
        graf_string += symvol
        time.sleep(pause)
    print('')
    return None

def write_json(full_path, data):
    ''' серилизация данных в файл *.json'''
    with open(full_path, 'w') as file:#photos.json
        json.dump(data, file, indent=2, ensure_ascii=False)

def get_large(size_dict):
    '''Функция нахождения фото по максимальному размеру или высоте или ширине'''
    if size_dict['width'] >= size_dict['height']:
        return size_dict['width']
    else:
        return size_dict['height']

class VKdownload:
    def __init__(self, vk_access_token, user_id, album_id, version='5.131'):
        self.token = vk_access_token
        self.id = user_id
        self.album = album_id
        self.version = version
        self.params = {'access_token': vk_access_token,
                       'v': self.version
                       }
  
    def get_photos(self):
        ''' обработка запроса'''
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.id,
                  'album_id': self.album,
                  'extended': True,
                  'photo_sizes': True,
                    }
        res = requests.get(url=url, params={**self.params, **params})
        
        #создаем временну папку TMP для проверки json
        if not os.path.exists('TMP'):
                os.mkdir('TMP') 
        write_json('TMP/data.json', res.json())
        data = res.json()['response']
        # Список всех загруженных фото
        photos = []
        max_size_photo = {}
        for photo in data['items']:
            # max_size = 0
            sizes = photo['sizes']            
            photos_info = {}
            # Выбираем фото максимального разрешения и добавляем в словарь max_size_photo
            for size in photo['sizes']:
                max_size_url = max(sizes, key=get_large)['url']
            if photo['likes']['count'] not in max_size_photo.keys():
                max_size_photo[photo['likes']['count']] = max_size_url
                photos_info['file_name'] = f"{photo['likes']['count']}.jpg"
            else:
                max_size_photo[f"{photo['likes']['count']} + {photo['date']}"] = max_size_url
                photos_info['file_name'] = f"{photo['likes']['count']}+{photo['date']}.jpg"

            # Формируем список всех фотографий для дальнейшей упаковки в .json
            photos_info['size'] = size['type']
            photos.append(photos_info)
            
        # Загрузка фотографий в пвпку на диске
        if not os.path.exists('OutVK'):
            os.mkdir('OutVK')      
        num_count = 0
        for photo_name, url in max_size_photo.items():
            with open('OutVK/%s' % f'{photo_name}.jpg', 'wb') as file:
                res = requests.get(url)
                file.write(res.content)
            num_count += 1
            num_photo = len(max_size_photo)
            my_progress_bar(num_count)
            print(f'скачено {num_count} из {num_photo}') 
        print(f'Всего загружено {num_photo} картинок')

        # Вызов функции серилизация данных photos.json
        write_json('photos.json', photos)

class YaUploader:
    def __init__(self, token: str, folder_ya):
        self.token = token
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': self.token
            }

    def upload(self, file_path: str):
        url = 'https://cloud-api.yandex.net/v1/disk/resources/'
        params = {
            'path': folder_ya,
            'overwrite': False}
        response = requests.put(url=url, headers=self.headers, params=params)
        
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        params = {
            'path': f'{folder_ya}/{file_name}',
            'overwrite': True}
        response = requests.get(url=url, headers=self.headers, params=params)

        url1 = response.json().get('href')
        # Загрузка файла
        uploader = requests.put(url1, data=open(files_path, 'rb'))

# Загрузка token vk и ya из файла token


# # ЗАГРУЗКА с VKontakt
# download = VKdownload(vk_access_token,user_id,album_id)
# download.get_photos()

# ВЫГРУЗКА НА YANDEX РЕСУРС
folder_ya = 'ARXIVE/'

uploader = YaUploader(ya_token, folder_ya)

photos_list = os.listdir('OutVK')
count = 0
for photo in photos_list:
    file_name = photo
    files_path = os.getcwd() + '\OutVK\\' + photo
    result = uploader.upload(files_path)
    count += 1
    my_progress_bar(count)
    print(f'\rНа ЯндексДиск в папку {folder_ya} загружено {count} фото')