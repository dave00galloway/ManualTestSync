from collections.abc import Sequence

import requests
import six

from testpad import authentication, statics

ROOT_TEXT = "(root)"


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
    text = coerce_text_to_lines(text=text)
    headers = authentication.testpad_headers(user=user, referer=(
        "{url}/script/{script_id}/".format(url=user.testpad_url, script_id=script_id)))
    data = {"data": ScriptBuilder(text=text).build()}
    response = requests.post("{url}/a/script/{script_id}/insertMany".format(url=user.testpad_url, script_id=script_id),
                             headers=headers, json=data)
    assert response.status_code is 200
    return response.json()


def coerce_text_to_lines(text=None):
    if isinstance(text, six.string_types):
        text = text.splitlines()
    if not text:
        raise ValueError("text should not be empty. locals: {locals}".format(locals=str(locals())))
    assert isinstance(text, Sequence), "text should be a list or string"
    return text


class TestLine(object):
    def __init__(self, parent=None, id_=None, cid=0, pid=None, pcid=0, off=-1, text=None, tags="", notes=""):
        if parent is None and text is not ROOT_TEXT:
            parent = root
            # should make this the "(root)" parent for correctness.
            #  root will contain next level down parents,
            # which will all be empty lines containing the next level down parents.
            # root will  have text "(root)"
            # root does not get posted to testpad
            # the first line of the script (the feature here) is NOT related tot he other parents except as siblings
        self.parent = parent
        self.notes = notes
        self.tags = tags
        self.text = text
        self.off = off  # this item's place in it's parent list
        self.pcid = pcid
        self.pid = pid
        self.cid = cid
        self.id = id_
        self.children = []
        if self.parent:
            self.parent.children.append(self)

    def data(self):
        return {
            "id": self.id,
            "cid": self.cid,
            "pid": self.pid,
            "pcid": self.pcid,
            "off": self.off,
            "text": self.text,
            "tags": self.tags,
            "notes": self.notes
        }


root = TestLine(parent=None, pid=0, text=ROOT_TEXT)


class ParentStackItem(object):
    def __init__(self, test_line=None, indent=-1):
        if test_line is None:
            test_line = TestLine()
        self.indent = indent
        self.test_line = test_line


class CaseInfoListItem(object):
    def __init__(self, case_item=None, parent=None, offset=0):
        # if case_item is None:
        #     case_item = TestLine(cid=-1)
        # if parent is None:
        #     parent = TestLine(cid=-1)
        # if parent.cid is -1 or case_item.cid is 1:
        #     raise ValueError("parent and case item must be specified. locals: {locals}".format(locals=str(locals())))
        self.offset = offset
        self.parent = parent
        self.case_item = case_item


class ScriptBuilder(object):
    def __init__(self, text=None):
        self.text = coerce_text_to_lines(text=text)
        self.tests = [root]
        self.cid = 0
        self.previousTestLine = root
        self.parents = []
        self.last_indent = 0
        self.inserts = []
        # self.new_case_roots = []

    def build(self):
        for line in self.text:
            self.cid += 1
            # test = TestLine(text=line, cid=self.cid)
            test = self._build_test_line(line=line)
            self.tests.append(test)
        # self.tests.reverse()
        self._prep_for_export()
        return self.inserts

    def _prep_for_export(self):
        case_info_list = []
        self.tests.remove(root)
        for test in self.tests:
            case_info_list.append(
                CaseInfoListItem(case_item=test, parent=test.parent, offset=test.parent.children.index(test)))

        for case in case_info_list:
            case.case_item.pid = case.parent.id
            case.case_item.pcid = case.parent.cid
            case.case_item.off = case.offset
            self.inserts.append(case.case_item.data())

    def _current_parent(self):
        try:
            return self.parents[-1]
        except IndexError:
            return None

    def _build_test_line(self, line=None):
        trimmed_line = line.lstrip()
        trim_length = len(line) - len(trimmed_line)
        # offset = trim_length % 4  # this is wrong, but works. ish

        indent = trim_length
        if indent > self.last_indent:
            self.parents.append(ParentStackItem(test_line=self.previousTestLine, indent=self.last_indent))
        elif indent < self.last_indent:
            while True:
                if indent > self._current_parent().indent:
                    break
                self.parents.pop()
        _parent = self._current_parent()  # .test_line
        if _parent:
            _parent = _parent.test_line
        test = TestLine(parent=_parent, text=trimmed_line, cid=self.previousTestLine.cid + 1, off=-1)
        self.tests.append(test)
        # if not _parent:
        #     self.new_case_roots.append(test)

        # _current_parent = self._current_parent()
        # if _current_parent is None:
        #     self.parents.append(test)
        # elif trimmed_line.startswith("Feature") or trimmed_line.startswith("Scenario"):
        #     if _current_parent.text.startswith("Scenario"):
        #         self.parents.pop()
        #     self.parents.append(test)
        # _current_parent = self._current_parent()
        # if test is not _current_parent:
        #     test.pcid = _current_parent.cid
        #     test.pid = _current_parent.cid
        self.previousTestLine = test
        return test


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
