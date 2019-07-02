import requests

from django.conf import settings


def get_vk_avatar(url):
    if url in settings.VK_NO_AVATAR:
        return None
    return url


def get_access_token(client_id, client_secret):
    try:
        response = requests.get(
            f'https://oauth.vk.com/token?grant_type=password&client_id={client_id}&client_secret={client_secret}'
        ).json()

    except requests.exceptions.ConnectionError:
        raise
        raise Exception('Could not get vk access token')
    try:
        print(response)
        return response['access_token']
    except KeyError:
        raise Exception('Could not get vk access token')
