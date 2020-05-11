import requests

from testpad import authentication
from testpad.statics import User, Project


def load_scripts(user=None, project=None, targetfolder=None, **kwargs):
    headers = {
        'x-csrftoken': user.csrf_token,
        'referer': "{url}/project/{project}/folder/{folder}".format(url=user.testpad_url, project=project,
                                                                    folder=targetfolder),
        'cookie': "csrftoken={csrftoken}; sessionid={sessionid};".format(csrftoken=user.csrf_token,
                                                                         sessionid=user.session_id)
    }
    load_scripts_response = requests.post(
        '{url}/a/project/{project}/folder/{folder}/loadScripts'.format(url=user.testpad_url, project=project,
                                                                       folder=targetfolder),
        headers=headers, json='{"data":null}')
    authentication.update_cookies(response=load_scripts_response, user=user, **kwargs)
    return load_scripts_response.json()


def create_script(user=User.get(), project=Project.get(), targetfolder=None, name=None, **kwargs):
    if user is None or project is None or targetfolder is None or name is None:
        raise ValueError(
            "user, project, targetfolder and name must be specified. {locals}".format(locals=str(locals())))
    new_script = _create_new_script(user=user, project=project, folder=targetfolder, **kwargs)

    return new_script


def _create_new_script(user=User.get(), project=Project.get(), folder=None, **kwargs):
    headers = {
        'x-csrftoken': user.csrf_token,
        'x-requested-with': 'XMLHttpRequest',
        'referer': "{url}/project/{project}/folder/{folder}/".format(url=user.testpad_url, project=project,
                                                                     folder=folder),
        'cookie': "csrftoken={csrftoken}; sessionid={sessionid};".format(csrftoken=user.csrf_token,
                                                                         sessionid=user.session_id)
    }

    data = '{"data":null}'

    new_script = requests.post(
        "{url}/a/project/{project}/folder/{folder}/newScript".format(url=user.testpad_url, project=project,
                                                                     folder=folder), headers=headers, data=data)

    assert new_script.status_code is 200
    authentication.update_cookies(response=new_script, user=user, **kwargs)
    return new_script.json()


if __name__ == '__main__':
    import os
    import json

    target_folder = os.getenv('targetfolder')
    Project.set(os.getenv('project'))
    User.set(authentication.authenticate())

    script = create_script(user=User.get(), project=Project.get(), targetfolder=target_folder, name="create_me")
    assert script
    print(json.dumps(script, indent=4))
