import csv
import dataclasses
import os
from typing import List

from test_rails.csv_import_classes import CsvRow, Priority, Type, TypeOfTest
from test_rails.importer import TestRailImporter, Section


class TestRailCSVImporter(TestRailImporter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.csv_cases = []  # type: List[CsvRow]
        self.writer = None

    def create_csv_for_import(self):
        for section in self.sections:
            self.parse_section(section_object=section, parent=None)
        with open("{out}{p}TestRailExport.csv".format(out=self.out_dir, p=os.path.sep), 'w', newline='') as csv_file:
            self.writer = self.setup_csv_file(csv_file=csv_file)
            for case in self.csv_cases:
                self.add_case_to_csv(case=case)

    def add_case_to_csv(self, case: CsvRow = None):
        row_dict = {
            case.cases_title.csv_name: case.cases_title.value,
            case.cases_custom_automation_status.csv_name: case.cases_custom_automation_status.value,
            case.cases_custom_automation_type.csv_name: case.cases_custom_automation_type.value,
            case.cases_custom_preconds.csv_name: case.cases_custom_preconds.value,
            case.cases_estimate.csv_name: case.cases_estimate.value,
            case.cases_custom_expected.csv_name: case.cases_custom_expected.value,
            case.cases_custom_platform.csv_name: case.cases_custom_platform.value,
            case.cases_priority_id.csv_name: case.cases_priority_id.value,
            case.cases_refs.csv_name: case.cases_refs.value,
            case.cases_custom_scenario.csv_name: case.cases_custom_scenario.value,
            case.cases_section_id.csv_name: case.cases_section_id.value,
            case.cases_section_desc.csv_name: case.cases_section_desc.value,
            case.cases_type_id.csv_name: case.cases_type_id.value,
            case.cases_custom_test_type.csv_name: case.cases_custom_test_type.value
        }
        self.writer.writerow(row_dict)

    def setup_csv_file(self, csv_file=None):
        writer = csv.DictWriter(csv_file,
                                fieldnames=[csv_column["csv_name"] for csv_column in
                                            dataclasses.asdict(self.csv_cases[0]).values()])
        writer.writeheader()
        return writer

    def parse_section(self, section_object: Section = None, parent: Section = None):
        for child_section in section_object.sections:
            self.parse_section(section_object=child_section, parent=section_object)
        self.add_csv_cases(section_object=section_object, parent_section=parent)

    def add_csv_cases(self, section_object: Section = None, parent_section: Section = None):
        for case in section_object.cases:
            steps = self.squish_steps(case)
            row = CsvRow(title=case.title, automation_status="", automation_type=None,
                         preconds=section_object.description,
                         estimate="",
                         expected="", platform="", priority_id=Priority.Medium, refs=case.references,
                         scenario=steps,
                         section_id=section_object.name if parent_section is None else "{parent_name} / {name}".format(
                             parent_name=parent_section.name, name=section_object.name),
                         section_desc=section_object.description,
                         type_id=Type.Regression,
                         test_type=TypeOfTest.Manual)
            self.csv_cases.append(row)


if __name__ == '__main__':
    print(list(Priority))
    print(list(Type))
    test_row = CsvRow(title="test", automation_status="", automation_type=None, preconds="Some Background", estimate="",
                      expected="", platform="", priority_id=Priority.Medium, refs="@JIRA-544",
                      scenario="all the scenario text", section_id="MySection",
                      section_desc="feature stuff and the background", type_id=Type.Regression,
                      test_type=TypeOfTest.Manual)
    print(test_row)
    print(dataclasses.asdict(test_row).keys())
