from collections.abc import Sequence

import six

ROOT_TEXT = "(root)"


def coerce_text_to_lines(text=None):
    if isinstance(text, six.string_types):
        text = text.splitlines()
    if not text:
        raise ValueError("text should not be empty. locals: {locals}".format(locals=str(locals())))
    assert isinstance(text, Sequence), "text should be a list or string"
    return text


class TestLine(object):
    def __init__(self, parent=None, id_=None, cid=0, pid=None, pcid=None, off=-1, text=None, tags="", notes=""):
        if parent is None and text is not ROOT_TEXT:
            parent = TestLine.get_root()
            # should make this the "(root)" parent for correctness.
            #  root will contain next level down parents,
            # which will all be empty lines containing the next level down parents. (except for the very first line)
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

    @classmethod
    def get_root(cls):
        root = TestLine(parent=None, pid=None, pcid=None, cid=0, id_=0, text=ROOT_TEXT)
        return root


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
        self.root = TestLine.get_root()
        self.tests = [self.root]
        self.cid = 0
        self.previousTestLine = self.root
        self.parents = [ParentStackItem(test_line=self.root, indent=-1)]
        self.last_indent = 0
        self.inserts = []
        # self.new_case_roots = []

    def build(self):
        for line in self.text:
            self.cid += 1
            test = self._build_test_line(line=line)
            self.tests.append(test)
        self._prep_for_export()
        return self.inserts

    def _prep_for_export(self):
        case_info_list = []
        for test in self.tests:
            if test.text is ROOT_TEXT:
                self.tests.remove(test)
                break
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
        self.last_indent = indent
        _parent = self._current_parent()  # .test_line
        if _parent:
            _parent = _parent.test_line
        test = TestLine(parent=_parent, text=trimmed_line, cid=self.previousTestLine.cid + 1, off=-1)
        # self.tests.append(test)
        self.previousTestLine = test
        return test


if __name__ == '__main__':
    import json

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

    sb = ScriptBuilder(text=test_text)
    res = sb.build()
    print(json.dumps(res, indent=4))
