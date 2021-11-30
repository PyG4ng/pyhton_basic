import json

from tqdm import tqdm

from vk import Vk
from yandex_disk import YaUploader
from constants import API_KEY_YANDEX


def upload_vk_pictures_on_yandex_disk(pictures_links: list, _disk: YaUploader,
                                      path_on_disk: str = '', directory_exists: bool = True):
    """
    Takes a list of pictures from Vk class methods get_profile_pictures() or get_wall_pictures() and
    uploads the pictures on yandex disk.
    Args:
        pictures_links: List of pictures from Vk class methods get_profile_pictures() or get_wall_pictures().
        _disk: Instance of YaUploader class.
        path_on_disk: Path to the directory where to upload the pictures. Will upload the pictures at
        the disk's root if no value is passed.
        directory_exists: Creates the directory where to upload the pictures if False is passed.

    Returns: 'Successful' if no error.

    """
    files_uploaded = []
    if not directory_exists:
        _disk.create_a_directory(path_on_disk)
    for picture in tqdm(pictures_links, desc=f'Uploading files to {path_on_disk}: '):
        # If two files have the same name, upload date on vk is added to the second file.
        if picture.get("file") not in files_uploaded:
            _disk.upload_from_internet(picture.get('url'), f'{path_on_disk}/{picture.get("file")}')
        else:
            _disk.upload_from_internet(picture.get('url'),
                                       f'{path_on_disk}/{picture.get("date")}-{picture.get("file")}')
        files_uploaded.append(picture.get("file"))
    print('Successful')


vk_user = Vk()
# print(vk_user)
# print(vk_user.get_friends_list())
profile_pictures = vk_user.get_profile_pictures()
# # profile_pictures = vk_user.get_wall_pictures()
#
disk = YaUploader(API_KEY_YANDEX)

upload_vk_pictures_on_yandex_disk(profile_pictures, disk, 'vk_pictures', directory_exists=False)

with open('pictures.json', 'w', encoding='utf-8') as file:
    json.dump(profile_pictures, file, indent=4)
