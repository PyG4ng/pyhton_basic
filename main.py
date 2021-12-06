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
    if pictures_links:
        if not directory_exists:
            _disk.create_a_directory(path_on_disk)

        files_uploaded = []
        for picture in tqdm(pictures_links, desc=f'Uploading files to {path_on_disk}: '):
            # If two files have the same name, upload date on vk is added to the second file.
            if picture.get("file") not in files_uploaded:
                _disk.upload_from_internet(picture.get('url'), f'{path_on_disk}/{picture.get("file")}')
            else:
                _disk.upload_from_internet(picture.get('url'),
                                           f'{path_on_disk}/{picture.get("date")}-{picture.get("file")}')
            files_uploaded.append(picture.get("file"))
        print('Successful')
    else:
        print("Nothing to upload!")


def get_photos_count():
    """
    Checks if the user enters a number between 1 and 100.
    Returns: Integer of entered value if check passed.

    """
    count = ''
    while not count.isdigit():
        count = input("How many pictures you want to get, 1 - 100: ")
        if count.isdigit() and (int(count) < 1 or int(count) > 100):
            return get_photos_count()
    return int(count)


def check_user_id_or_username():
    """
    Checks if the user enters alphanumeric characters, meaning alphabet letter (a-z) and numbers (0-9).
    Returns: Entered value if check passed.

    """
    user_got = ''
    while not user_got.isalnum():
        user_got = input("Enter a vk user (valid id/username): ")
    return user_got


if __name__ == '__main__':
    user_to_get = check_user_id_or_username()

    pictures_count = get_photos_count()

    vk_user = Vk(user_to_get)
    profile_pictures = vk_user.get_profile_pictures(pictures_count)

    disk = YaUploader(API_KEY_YANDEX)

    upload_vk_pictures_on_yandex_disk(profile_pictures, disk, 'vk_pictures', directory_exists=False)

    with open('pictures.json', 'w', encoding='utf-8') as file:
        json.dump(profile_pictures, file, indent=4)
