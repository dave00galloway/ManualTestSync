import os

import xml.etree.ElementTree as ET


class TestRailXMLImporter(object):
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
            TestRailXMLImporter.add_examples_to_scenario(case=scenario_, examples=scenario["examples"],
                                                         step_no=len(scenario_.steps) + 1)
        feature_section.cases.append(scenario_)

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

    def create_xml_for_import(self):
        xml_root_section = ET.Element('sections')
        for section in self.sections:
            self.add_xml_section(section_object=section, parent=xml_root_section)

        with open("{out}{p}TestRailExport.xml".format(out=self.out_dir, p=os.path.sep), mode='wb') as export_file:
            export_file.write(ET.tostring(xml_root_section))

    def add_xml_section(self, section_object=None, parent=None):
        xml_section = ET.SubElement(parent, 'section')
        name = ET.SubElement(xml_section, "name")
        name.text = section_object.name
        description = ET.SubElement(xml_section, "description")
        description.text = section_object.description
        for child_section in section_object.sections:
            self.add_xml_section(section_object=child_section, parent=xml_section)
        self.add_xml_cases_to_section(section_object, xml_section)

    def add_xml_cases_to_section(self, section=None, xml_section=None):
        for case in section.cases:
            xml_case = ET.SubElement(xml_section, 'case')
            title = ET.SubElement(xml_case, "title")
            title.text = case.title
            references = ET.SubElement(xml_case, "references")
            references.text = case.references
            xml_custom = ET.SubElement(xml_case, 'custom')
            self.add_xml_steps_to_case(steps=case.steps, xml_custom=xml_custom)

    @staticmethod
    def add_xml_steps_to_case(steps=None, xml_custom=None):
        xml_steps = ET.SubElement(xml_custom, 'steps')
        for step in steps:
            xml_step = ET.SubElement(xml_steps, 'step')
            xml_index = ET.SubElement(xml_step, 'index')
            xml_index.text = str(step.index)
            xml_content = ET.SubElement(xml_step, 'content')
            xml_content.text = step.content
            xml_exp = ET.SubElement(xml_step, "expected")
            xml_exp.text = step.expected
            if step.step_argument:
                xml_exp.text = "{text}{s}{arg}".format(text=xml_exp.text, s=os.path.sep, arg=step.step_argument)


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
