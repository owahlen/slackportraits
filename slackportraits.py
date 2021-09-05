#!/usr/bin/env python3

import argparse
import logging
from os import makedirs, environ
from os.path import dirname, exists, splitext, join

import requests
from slack_sdk.errors import SlackApiError
from slack_sdk.web import WebClient


def create_portraits_dir_if_not_exists(portraits_dir: str):
    directory = dirname(portraits_dir)
    if not exists(directory):
        makedirs(directory)
    return directory


def get_all_slack_users(token: str):
    client = WebClient(token=token)
    all_users = []
    try:
        for paginated_response in client.users_list(limit=10000):
            all_users += paginated_response["members"]
    except SlackApiError as e:
        assert e.response["error"]
    return all_users


def download_portrait(user: dict, portraits_dir: str):
    email = user["profile"]["email"]
    email_user = email.split("@")[0]
    image_512_url = user["profile"]["image_512"]
    _, file_extension = splitext(image_512_url)
    filename = email_user + file_extension
    r = requests.get(image_512_url, allow_redirects=True)
    open(join(portraits_dir, filename), "wb").write(r.content)


def download_portraits(token: str, portraits_dir: str):
    directory = create_portraits_dir_if_not_exists(portraits_dir)
    logging.info("Downloading portrait images from slack to '{}'...\n".format(portraits_dir))
    all_users = get_all_slack_users(token)
    for user in all_users:
        download_portrait(user, directory)


def main():
    token=environ.get("SLACK_TOKEN")
    assert token, "The SLACK_TOKEN environment variable must be set"
    parser = argparse.ArgumentParser()
    parser.add_argument("portraits", nargs='?', type=str, default="portraits",
                        help="directory containing portrait images [default: 'portraits']")
    args = parser.parse_args()
    download_portraits(token=token, portraits_dir=args.portraits)


if __name__ == '__main__':
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    main()
