import os


class TestRailImporter(object):
    def __init__(self, out_dir=None, suites=None, **kwargs):
        if out_dir is None or suites is None:
            raise ValueError("out_dir and suites cannot be None. {locals}".format(locals=str(locals())))
        self.suites = suites
        self.out_dir = out_dir
        self.sections = []

    def create_sections(self):
        current_section = None
        for key, gherkin_feature in self.suites.items():
            section_name = key[0]
            feature_section_name = key[1]
            if current_section is None or section_name != current_section.name:
                current_section = Section(name=key[0])
                self.sections.append(current_section)
            feature_section = Section(name=feature_section_name)
            current_section.sections.append(feature_section)
            gherkin_document = gherkin_feature.gherkin_document
            feature_dict = gherkin_document["feature"]
            feature_section.description = "{keyword}: {title}".format(keyword=feature_dict["keyword"],
                                                                      title=feature_dict["name"])
            for child in feature_dict["children"]:
                if child["keyword"] == 'Background':
                    self.add_background_to_feature_description(background=child,
                                                               feature_section=feature_section)
                    continue
                if child["keyword"] == 'Scenario':
                    self.add_scenario_to_feature(scenario=child, feature_section=feature_section)
                    continue
                if child["keyword"] == "Scenario Outline":
                    self.add_scenario_to_feature(scenario=child, feature_section=feature_section, outline=True)
                    continue
                raise GherkinElementException("element {child} is not a gherkin element".format(child=child))

    @staticmethod
    def add_background_to_feature_description(background=None, feature_section=None):
        feature_section.description = "{description}{s}{s}{keyword}: {name}{s}".format(
            description=feature_section.description, s=os.linesep, keyword=background["keyword"],
            name=background["name"])
        for step in background["steps"]:
            feature_section.description = "{description}{keyword} {text}{s}".format(
                description=feature_section.description, s=os.linesep, keyword=step["keyword"], text=step["text"])

    @staticmethod
    def add_examples_to_scenario(case=None, examples=None, step_no=None):
        content_ = ""
        for example in examples:
            content_ = "{content}Examples:".format(content=content_)
            if len(example["tags"]) > 0:
                content_ = "{tags}{s}{content}{s}".format(content=content_, s=os.linesep,
                                                          tags=", ".join([t["name"] for t in example["tags"]]))
            content_ = "{content}{s}|||{headers}".format(content=content_, s=os.linesep, headers="|".join(
                [cell["value"] for cell in example["tableHeader"]["cells"]]))
            for row in example["tableBody"]:
                content_ = "{content}{s}||{values}".format(content=content_, s=os.linesep,
                                                           values="|".join([cell["value"] for cell in row["cells"]]))
        step_ = Step(index=step_no, content=content_)
        case.steps.append(step_)

    @staticmethod
    def add_scenario_to_feature(scenario=None, feature_section=None, outline=False):
        scenario_type = "Scenario Outline" if outline else "Scenario"
        scenario_ = Case(title=": ".join([scenario_type, scenario["name"]]),
                         references=", ".join([t["name"] for t in scenario["tags"]]))
        for i, step in enumerate(scenario["steps"]):
            step_argument = step["argument"] if "argument" in dict(step).keys() else None
            step_ = Step(index=i + 1, content="{keyword} {text}".format(keyword=step["keyword"], text=step['text']),
                         step_argument=step_argument)
            scenario_.steps.append(step_)
        if outline:
            TestRailImporter.add_examples_to_scenario(case=scenario_, examples=scenario["examples"],
                                                      step_no=len(scenario_.steps) + 1)
        feature_section.cases.append(scenario_)


class Section(object):
    def __init__(self, name=None, description="", **kwargs):
        super().__init__()
        if name is None:
            raise ValueError("Section name cannot be None. {locals}".format(locals=str(locals())))
        self.description = description
        self.name = name
        self.sections = []
        self.cases = []


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
        self.steps = []


class Step(object):
    def __init__(self, index=None, content=None, expected="", step_argument=None):
        super().__init__()
        if index is None or content is None:
            raise ValueError("Step index and content cannot be None. {locals}".format(locals=str(locals())))
        self.expected = expected
        self.content = content
        self.index = index
        self.step_argument = step_argument


class GherkinElementException(Exception):
    pass


class UnsupportedStepArgument(Exception):
    pass