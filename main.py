import json
import os

import requests

from testpad import authentication
from testpad.user import User

PUBLIC_TESTPAD_URL = 'https://ontestpad.com/login'


def main():
    project = os.getenv('project')
    targetfolder = os.getenv('targetfolder')
    User.set(authentication.authenticate())

    scripts = load_scripts(user=User.get(), project=project, targetfolder=targetfolder)
    assert scripts
    print(json.dumps(scripts, indent=4))


def load_scripts(user=None, project=None, targetfolder=None):
    headers = {
        'x-csrftoken': user.csrf_token,
        'referer': "{url}/{project}/{folder}".format(url=user.testpad_url, project=project, folder=targetfolder),
        'cookie': "csrftoken={csrftoken}; sessionid={sessionid};".format(csrftoken=user.csrf_token,
                                                                         sessionid=user.session_id)
    }
    load_scripts_response = requests.post(
        '{url}/a/{project}/{folder}/loadScripts'.format(url=user.testpad_url, project=project, folder=targetfolder),
        headers=headers, json='{"data":null}')
    user = authentication.update_cookies(response=load_scripts_response, user=user)
    user.kwargs = {"new": "entry"}
    return load_scripts_response.json()


if __name__ == '__main__':
    main()
