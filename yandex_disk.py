from pathlib import Path

import requests


class YaUploader:
    def __init__(self, oauth_token):
        self.token = oauth_token

    def _get_headers(self):
        return {
            'Accept': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def upload(self, file_path):
        """
        Gets a link from the yandex disk api to upload the file located in the file_path and then
        uploads it on your yandex disk.
        Args:
            file_path: A path to the file to upload.

        Returns: None
        """
        headers = self._get_headers()
        params = {
            'path': Path(file_path),
            'overwrite': 'true'
        }
        response = requests.get('https://cloud-api.yandex.net/v1/disk/resources/upload', params=params,
                                headers=headers)
        upload_link = response.json().get('href')
        with open(file_path, 'rb') as file:
            uploading = requests.put(upload_link, data=file)
        if uploading.status_code == 201:
            print('File uploaded')
        else:
            print('Error! File not uploaded')

    def upload_from_internet(self, _url, _path):
        """
        Takes a link to a file and uploads it on yandex disk.
        Args:
            _url: Url to download the file
            _path: Path to the folder on the disk where  to upload the file,
            if the folder is at the disk's root, just write the folder's name.

        Returns (str): Operation's status.

        """
        headers = self._get_headers()
        params = {"url": _url,
                  "path": _path
                  }
        response = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload', headers=headers,
                                 params=params)
        if response.status_code == 202:
            return 'Successfully uploaded'
        elif response.status_code == 409:
            if response.json():
                print(response.json().get('description'), '\nDirectory not found!')
                response.raise_for_status()
        return "Something went wrong, your file has not been uploaded!"

    def create_a_directory(self, _path):
        """
        Creates a directory (folder) on yandex disk. Will return an error message if the directory exists.
        Args:
            _path: Path where to create the directory on the disk.

        Returns (str): Operation's status.

        """
        headers = self._get_headers()
        params = {"path": _path}
        response = requests.put('https://cloud-api.yandex.net/v1/disk/resources', headers=headers,
                                params=params)
        if response.status_code == 201:
            print('Directory created successfully')
        elif response.status_code == 409:
            if response.json():
                print(response.json().get('description'))
        else:
            response.raise_for_status()

    def delete_directory(self, _path):
        """
        Deletes a directory (folder) on yandex disk. Will return an error message if the directory doesn't exist.
        Args:
            _path: Path to the directory.

        Returns (str): Operation's status.

                """
        headers = self._get_headers()
        params = {"path": _path}
        response = requests.delete('https://cloud-api.yandex.net/v1/disk/resources', headers=headers,
                                   params=params)
        if response.status_code == 202:
            print('Directory deleted successfully!')
        elif response.status_code == 404:
            if response.json():
                print(response.json().get('description'))
        else:
            response.raise_for_status()
