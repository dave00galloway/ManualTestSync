import requests

from testpad import authentication
from testpad.statics import User, Project


def create_folder(user=User.get(), project=Project.get(), targetfolder=None, name=None, **kwargs):
    if user is None or project is None or targetfolder is None or name is None:
        raise ValueError(
            "user, project, targetfolder and name must be specified. {locals}".format(locals=str(locals())))

    new_folder = _create_new_folder(user=user, project=project, parent=targetfolder, **kwargs)

    return new_folder


def _create_new_folder(user=User.get(), project=Project.get(), parent=None, **kwargs):
    headers = {
        'x-csrftoken': user.csrf_token,
        'referer': "{url}/project/{project}/folder/{folder}/".format(url=user.testpad_url, project=project,
                                                                     folder=parent),
        'cookie': "csrftoken={csrftoken}; sessionid={sessionid};".format(csrftoken=user.csrf_token,
                                                                         sessionid=user.session_id)
    }
    # a/project/19/folder/f1/newFolder
    new_folder_response = requests.post(
        '{url}/a/project/{project}/folder/{folder}/newFolder'.format(url=user.testpad_url, project=project,
                                                                     folder=parent),
        headers=headers, json='{"data":null}')
    assert new_folder_response.status_code is 200
    authentication.update_cookies(response=new_folder_response, user=user, **kwargs)
    return new_folder_response.json()


if __name__ == '__main__':
    import os
    import json

    target_folder = os.getenv('targetfolder')
    Project.set(os.getenv('project'))
    User.set(authentication.authenticate())

    folder = create_folder(user=User.get(), project=Project.get(), targetfolder=target_folder, name="test_me")
    assert folder
    print(json.dumps(folder, indent=4))
