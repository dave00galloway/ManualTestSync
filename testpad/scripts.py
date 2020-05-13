import requests

from testpad import authentication, statics


def load_scripts(user=None, project=None, targetfolder=None, **kwargs):
    project, user = statics.set_project_user(project=project, user=user)
    headers = authentication.testpad_headers(user=user,
                                             referer="{url}/project/{project}/folder/{folder}".format(
                                                 url=user.testpad_url,
                                                 project=project,
                                                 folder=targetfolder))
    load_scripts_response = requests.post(
        '{url}/a/project/{project}/folder/{folder}/loadScripts'.format(url=user.testpad_url, project=project,
                                                                       folder=targetfolder),
        headers=headers, json='{"data":null}')
    authentication.update_cookies(response=load_scripts_response, user=user, **kwargs)
    return load_scripts_response.json()


def create_script(user=None, project=None, targetfolder=None, name=None, **kwargs):
    project, user = statics.set_project_user(project=project, user=user)
    if user is None or project is None or targetfolder is None or name is None:
        raise ValueError(
            "user, project, targetfolder and name must be specified. {locals}".format(locals=str(locals())))
    new_script = _create_new_script(user=user, project=project, folder=targetfolder, **kwargs)

    return new_script


def _create_new_script(user=None, project=None, folder=None, **kwargs):
    headers = authentication.testpad_headers(user=user,
                                             referer="{url}/project/{project}/folder/{folder}/".format(
                                                 url=user.testpad_url,
                                                 project=project,
                                                 folder=folder))

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
    from testpad.statics import User, Project

    target_folder = os.getenv('targetfolder')
    Project.set(os.getenv('project'))
    User.set(authentication.authenticate())

    script = create_script(user=User.get(), project=Project.get(), targetfolder=target_folder, name="create_me")
    assert script
    print(json.dumps(script, indent=4))
