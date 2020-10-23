from typing import List


class Section(object):
    def __init__(self, name=None, description="", **kwargs):
        super().__init__()
        if name is None:
            raise ValueError("Section name cannot be None. {locals}".format(locals=str(locals())))
        self.description = description
        self.name = name
        self.sections = []  # type: List[Section]
        self.cases = []  # type: List[Case]


class Case(object):
    def __init__(self, title=None, references=None, **kwargs):
        super().__init__()
        if title is None:
            raise ValueError("Case title cannot be None. {locals}".format(locals=str(locals())))
        if references is None:
            references = []
        self.references = references
        self.title = title
        self.custom = []
        self.steps = []  # type: List[Step]


class Step(object):
    def __init__(self, index=None, content=None, expected="", step_argument=None):
        super().__init__()
        if index is None or content is None:
            raise ValueError("Step index and content cannot be None. {locals}".format(locals=str(locals())))
        self.expected = expected
        self.content = content
        self.index = index
        self.step_argument = step_argument
