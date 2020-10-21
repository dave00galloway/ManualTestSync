import os
import xml.etree.ElementTree as ET

from test_rails.importer import TestRailImporter, UnsupportedStepArgument


class TestRailXMLImporter(TestRailImporter):

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
            TestRailXMLImporter.add_step_argument(step=step, xml_content=xml_content, xml_step=xml_step,
                                                  xml_exp=xml_exp)

    @staticmethod
    def add_step_argument(step=None, xml_step=None, xml_content=None, xml_exp=None):
        if step.step_argument:
            if step.step_argument["type"] is 'DocString':
                xml_exp.text = "{text}{s}{arg}".format(text=xml_exp.text, s=os.linesep,
                                                       arg=step.step_argument["content"])
                return
            if step.step_argument["type"] is 'DataTable':
                table_text = "||"
                for row in step.step_argument["rows"]:
                    table_row = "|".join([cell["value"] for cell in row["cells"]])
                    table_text = "{table_text}|{table_row}{s}".format(table_text=table_text, table_row=table_row,
                                                                      s=os.linesep)
                xml_content.text = "{text}{s}{table_text}".format(text=xml_content.text, s=os.linesep,
                                                                  table_text=table_text)
                return
            raise UnsupportedStepArgument(step.step_argument)


