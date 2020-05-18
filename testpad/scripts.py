import requests

from testpad import authentication, statics
from testpad.tests import ScriptBuilder


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
    rename_script = _rename_script(user=user, project=project, new_name=name, script_id=new_script['data']['id'])
    assert rename_script['status'] == "OK"
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


def _rename_script(user=None, project=None, new_name=None, script_id=None, **kwargs):
    project, user = statics.set_project_user(project=project, user=user)
    if user is None or project is None or new_name is None or script_id is None:
        raise ValueError(
            "script_id, user, project and name must be specified. {locals}".format(locals=str(locals())))
    headers = authentication.testpad_headers(user=user,
                                             referer="{url}/project/{project}/".format(
                                                 url=user.testpad_url,
                                                 project=project))
    data = {"data": new_name}
    rename_response = requests.post(
        "{url}/a/script/{script_id}/editname".format(url=user.testpad_url, script_id=script_id), headers=headers,
        json=data)
    assert rename_response.status_code is 200
    authentication.update_cookies(response=rename_response, user=user, **kwargs)
    return rename_response.json()


def populate_script(user=None, project=None, script_id=None, text=None, **kwargs):
    project, user = statics.set_project_user(project=project, user=user)
    if user is None or project is None or script_id is None or text is None:
        raise ValueError(
            "script_id, user and project must be specified. {locals}".format(locals=str(locals())))

    headers = authentication.testpad_headers(user=user, referer=(
        "{url}/script/{script_id}/".format(url=user.testpad_url, script_id=script_id)))
    data = {"data": ScriptBuilder(text=text).build()}
    response = requests.post("{url}/a/script/{script_id}/insertMany".format(url=user.testpad_url, script_id=script_id),
                             headers=headers, json=data)
    assert response.status_code is 200
    return response.json()


if __name__ == '__main__':
    import os
    import json
    from testpad.statics import User, Project

    # example file from
    # https://github.com/cucumber/cucumber-jvm/blob/master/compatibility/src/test/resources/features/examples-tables/examples-tables.feature
    test_text = """Feature: Examples Tables
  Sometimes it can be desireable to run the same scenario multiple times
  with different data each time. This can be done by placing an Examples
  section with an Examples Table underneath a Scenario, and use <placeholders>
  in the Scenario, matching the table headers.

  Scenario Outline: eating cucumbers
    Given there are <start> cucumbers
    When I eat <eat> cucumbers
    Then I should have <left> cucumbers

    Examples: These are passing
      | start | eat | left |
      |    12 |   5 |    7 |
      |    20 |   5 |   15 |

    Examples: These are failing
      | start | eat | left |
      |    12 |  20 |    0 |
      |     0 |   1 |    0 |

    Examples: These are undefined because the value is not an {int}
      | start | eat    | left  |
      |    12 | banana |    12 |
      |     0 |      1 | apple |
    """

    target_folder = os.getenv('targetfolder')
    Project.set(os.getenv('project'))
    User.set(authentication.authenticate())

    script = create_script(user=User.get(), project=Project.get(), targetfolder=target_folder, name="create_me")
    assert script
    print(json.dumps(script, indent=4))
    script = populate_script(script_id=script['data']['id'], text=test_text)
    assert script
    print(json.dumps(script, indent=4))
