import requests

from testpad import authentication, statics


def create_folder(user=None, project=None, targetfolder=None, name=None, **kwargs):
    project, user = statics.set_project_user(project=project, user=user)
    if targetfolder is None or name is None:
        raise ValueError(
            "user, project, targetfolder and name must be specified. {locals}".format(locals=str(locals())))

    new_folder = _create_new_folder(user=user, project=project, parent=targetfolder, **kwargs)
    folder_id = new_folder["data"]["id"]

    new_folder = _rename_folder(user=user, project=project, parent=targetfolder, folder_id=folder_id,
                                name=name,
                                **kwargs)

    return new_folder


def _rename_folder(user=None, project=None, folder_id=None, name=None, **kwargs):
    headers = authentication.testpad_headers(user=user,
                                             referer="{url}/project/{project}/".format(url=user.testpad_url,
                                                                                       project=project))
    rename_folder_response = requests.post(
        '{url}/a/project/{project}/folder/{folder}/name'.format(url=user.testpad_url, project=project,
                                                                folder=folder_id),
        headers=headers, json={"data": name})
    assert rename_folder_response.status_code is 200
    authentication.update_cookies(response=rename_folder_response, user=user, **kwargs)
    return rename_folder_response.json()


def _create_new_folder(user=None, project=None, parent=None, **kwargs):
    headers = authentication.testpad_headers(user=user,
                                             referer="{url}/project/{project}/folder/{folder}/".format(
                                                 url=user.testpad_url,
                                                 project=project,
                                                 folder=parent))
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
    from testpad.statics import User, Project

    target_folder = os.getenv('targetfolder')
    Project.set(os.getenv('project'))
    User.set(authentication.authenticate())

    folder = create_folder(user=User.get(), project=Project.get(), targetfolder=target_folder, name="refactor_me")
    assert folder
    print(json.dumps(folder, indent=4))
