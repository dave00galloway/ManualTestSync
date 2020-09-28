class TestRailXMLImporter(object):
    def __init__(self, out_dir=None, suites=None, **kwargs):
        if out_dir is None or suites is None:
            raise ValueError("out_dir and suites cannot be None. {locals}".format(locals=str(locals())))
        self.suites = suites
        self.out_dir = out_dir

    def create_sections(self):
        current_section = None
        for key, gherkin_feature in self.suites.items():
            section_name = key[0]
            if current_section is None or section_name is not current_section.name:
                current_section = Section(name=key[0])


class Section(object):
    def __init__(self, name=None, description=None, **kwargs):
        if name is None:
            raise ValueError("Section name cannot be None. {locals}".format(locals=str(locals())))
        self.description = description
        self.name = name
        self.sections = []
        self.cases = []


class Case(object):
    def __init__(self, title=None, references=None, **kwargs):
        if title is None:
            raise ValueError("Case title cannot be None. {locals}".format(locals=str(locals())))
        self.references = references
        self.title = title
        self.custom = []
        self.steps = []


class Step(object):
    def __init__(self, index=None, content=None, expected=None, **kwargs):
        if index is None or content is None:
            raise ValueError("Step index and content cannot be None. {locals}".format(locals=str(locals())))
        self.expected = expected
        self.content = content
        self.index = index
