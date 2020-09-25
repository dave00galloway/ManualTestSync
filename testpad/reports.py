import requests

from testpad import statics, authentication


def report_with_steps(user=None, project=None, report_folder=None, name=None, auth_token=None, **kwargs):
    project, user = statics.set_project_user(project=project, user=user)
    if user is None and auth_token is None:
        raise ValueError(
            "user or auth_token must be specified. {locals}".format(locals=str(locals())))
    if project is None or report_folder is None:
        raise ValueError("project and targetfolder must be specified. {locals}".format(locals=str(locals())))

    # https://recordsure.ontestpad.com/project/11/folder/f277/report/S
    headers = authentication.testpad_headers(user=user,
                                             referer="{url}/project/{project}/".format(url=user.testpad_url,
                                                                                       project=project))
    response = requests.get(
        '{url}/project/{project}/folder/{folder}/report/Sb'.format(url=user.testpad_url, project=project,
                                                                   folder=report_folder), headers=headers)
    assert response.status_code is 200
    return response.content
