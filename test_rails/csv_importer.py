import csv
import dataclasses
from dataclasses import dataclass
from enum import Enum, auto

from test_rails.importer import TestRailImporter


class TestRailCSVImporter(TestRailImporter):
    pass


class AutoPriority(Enum):
    def _generate_next_value_(self, start, count, last_values):
        return self


class Priority(AutoPriority):
    Low = auto()
    Medium = auto()
    High = auto()


class AutoType(Enum):
    def _generate_next_value_(self, start, count, last_values):
        return self


class Type(AutoType):
    Acceptance = auto()
    Accessibility = auto()
    Destructive = auto()
    Functional = auto()
    Other = auto()
    Performance = auto()
    Regression = auto()
    Security = auto()
    Smoke_Sanity = auto()
    Usability = auto()


class AutoTypeOfTest(Enum):
    def _generate_next_value_(self, start, count, last_values):
        return self


class TypeOfTest(AutoTypeOfTest):
    Manual = auto()
    Automated = auto()
    # None=auto()


@dataclass
class CsvColumn(object):
    test_rails_name: str
    csv_name: str
    value: object


@dataclass
class CsvRow(object):

    def __init__(self, title=None, automation_status=None, automation_type=None, preconds=None, estimate=None,
                 expected=None, platform=None, priority_id=Priority.Medium, refs=None, scenario=None, section_id=None,
                 section_desc=None, type_id=Type.Regression, test_type=TypeOfTest.Manual):
        self.cases_title = CsvColumn(
            test_rails_name="cases_title",
            csv_name="Title",
            value=title)
        self.cases_custom_automation_status = CsvColumn(
            test_rails_name="cases_custom_automation_status",
            csv_name="Automation Status",
            value=automation_status)
        self.cases_custom_automation_type = CsvColumn(
            test_rails_name="cases_custom_automation_type",
            csv_name="Automation Type",
            value=automation_type)
        self.cases_custom_preconds = CsvColumn(
            test_rails_name="cases_custom_preconds",
            csv_name="Background",
            value=preconds)
        self.cases_estimate = CsvColumn(
            test_rails_name="cases_estimate",
            csv_name="Estimate",
            value=estimate)
        self.cases_custom_expected = CsvColumn(
            test_rails_name="cases_custom_expected",
            csv_name="Expected Result",
            value=expected)
        self.cases_custom_platform = CsvColumn(
            test_rails_name="cases_custom_platform",
            csv_name="Platform",
            value=platform)
        self.cases_priority_id = CsvColumn(
            test_rails_name="cases_priority_id",
            csv_name="Priority"
            , value=priority_id)
        self.cases_refs = CsvColumn(
            test_rails_name="cases_refs",
            csv_name="References",
            value=refs)
        self.cases_custom_scenario = CsvColumn(
            test_rails_name="cases_custom_scenario",
            csv_name="Scenario",
            value="<gherkin>{scenario}</gherkin>".format(scenario=scenario))
        self.cases_section_id = CsvColumn(
            test_rails_name="cases_section_id",
            csv_name="Section",
            value=section_id)
        self.cases_section_desc = CsvColumn(
            test_rails_name="cases_section_desc",
            csv_name="Section Description",
            value=section_desc)
        self.cases_type_id = CsvColumn(
            test_rails_name="cases_type_id",
            csv_name="Type",
            value=type_id)
        self.cases_custom_test_type = CsvColumn(
            test_rails_name="cases_custom_test_type",
            csv_name="Type of Test",
            value=test_type)

    cases_title: CsvColumn
    cases_custom_automation_status: CsvColumn
    cases_custom_automation_type: CsvColumn
    cases_custom_preconds: CsvColumn
    cases_estimate: CsvColumn
    cases_custom_expected: CsvColumn
    cases_custom_platform: CsvColumn
    cases_priority_id: CsvColumn
    cases_refs: CsvColumn
    cases_custom_scenario: CsvColumn
    cases_section_id: CsvColumn
    cases_section_desc: CsvColumn
    cases_type_id: CsvColumn
    cases_custom_test_type: CsvColumn


if __name__ == '__main__':
    print(list(Priority))
    print(list(Type))
    row = CsvRow(title="test", automation_status="", automation_type=None, preconds="Some Background", estimate="",
                 expected="", platform="", priority_id=Priority.Medium, refs="@JIRA-544",
                 scenario="all the scenario text", section_id="MySection",
                 section_desc="feature stuff and the background", type_id=Type.Regression, test_type=TypeOfTest.Manual)
    print(row)
    # row.cases_title.value = "n ew tile"
    print(dataclasses.asdict(row).keys())
    with open("/Users/dave/tmp/export.csv", 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file,
                                fieldnames=[csv_column["csv_name"] for csv_column in dataclasses.asdict(row).values()])
        writer.writeheader()
        rowdict = {
            row.cases_title.csv_name: row.cases_title.value,
            row.cases_custom_automation_status.csv_name: row.cases_custom_automation_status.value,
            row.cases_custom_automation_type.csv_name: row.cases_custom_automation_type.value,
            row.cases_custom_preconds.csv_name: row.cases_custom_preconds.value,
            row.cases_estimate.csv_name: row.cases_estimate.value,
            row.cases_custom_expected.csv_name: row.cases_custom_expected.value,
            row.cases_custom_platform.csv_name: row.cases_custom_platform.value,
            row.cases_priority_id.csv_name: row.cases_priority_id.value,
            row.cases_refs.csv_name: row.cases_refs.value,
            row.cases_custom_scenario.csv_name: row.cases_custom_scenario.value,
            row.cases_section_id.csv_name: row.cases_section_id.value,
            row.cases_section_desc.csv_name: row.cases_section_desc.value,
            row.cases_type_id.csv_name: row.cases_type_id.value,
            row.cases_custom_test_type.csv_name: row.cases_custom_test_type.value
        }
        writer.writerow(rowdict)
