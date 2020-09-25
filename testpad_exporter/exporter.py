import os
import tempfile

from bs4 import BeautifulSoup
from gherkin.parser import Parser
from gherkin.pickles import compiler
from gherkin.token_scanner import TokenScanner

from testpad.reports import report_with_steps


class Exporter(object):
    def __init__(self, user=None, project=None, report_folder=None, checkout_dir=None):
        self.checkout_dir = checkout_dir
        self.report_folder = report_folder
        self.project = project
        self.user = user

    def export_tests(self):
        content = report_with_steps(user=self.user, project=self.project, report_folder=self.report_folder)
        suites = self.parse_tests_to_gherkin(content)
        return suites

    def parse_tests_to_gherkin(self, content):
        html = BeautifulSoup(content, "html.parser")
        suites = self.find_test_suites(html)
        gherkin_suites = {}
        for suite in suites:
            gherkin_files = {}
            feature = self._find_feature(suite)
            # print(feature.suite_name, feature.feature_name)  # , feature.scenarios)
            feature_text = feature.get_feature_text()
            # print(feature_text)
            with tempfile.NamedTemporaryFile() as temp_file:
                for line in feature_text:
                    temp_file.write(bytes(str(line).replace(os.linesep, ' '), encoding='utf-8'))
                    temp_file.write(bytes(os.linesep, encoding='utf-8'))
                temp_file.seek(0)
                try:
                    gherkin_file = GherkinFeature(file=temp_file.name)
                except GherkinError as e:
                    raise GherkinError("unable to parse / pickle feature {feature} in suite {suite}".format(
                        feature=feature.feature_name, suite=feature.suite_name)) from e
                gherkin_files[feature.feature_name] = gherkin_file
            gherkin_suites[feature.suite_name] = gherkin_files
        return gherkin_suites

    @staticmethod
    def find_test_suites(html):
        return html.body.find_all('div', class_='scriptSection withoutBreaks')

    @staticmethod
    def _find_feature(suite):
        suite_name = suite.find('div', class_="heading").find('h3').text
        feature_name = suite.find('div', class_="heading").find('h1').text
        scenarios = suite.find('table', class_="scriptGrid").tbody
        return GherkinFeatureCandidate(suite_name=suite_name, feature_name=feature_name, scenarios=scenarios)


class GherkinFeatureCandidate(object):
    def __init__(self, suite_name=None, feature_name=None, scenarios=None):
        self.scenarios = scenarios
        self.feature_name = feature_name
        self.suite_name = suite_name
        self.feature_text = []

    def get_feature_text(self):
        rows = self.scenarios.find_all('tr')
        for row in rows:
            try:
                case = row.find(class_="case")
                if case is not None:
                    self.feature_text.append(case.text)
            except Exception as e:
                print(e)
        return self.feature_text


class GherkinError(Exception):
    pass


class GherkinFeature(object):
    def __init__(self, file=None):
        super().__init__()

        self.file = file
        parser = Parser()
        scanner = TokenScanner(self.file)
        try:
            self.gherkin_document = parser.parse(scanner)
            self.pickles = compiler.compile(self.gherkin_document)
        except Exception as e:
            raise GherkinError("unable to parse / pickle doc {doc}".format(doc=self.file)) from e

# class ExportableScenario(object):
#     def __init__(self, scenario_title=None, steps=None):
#         self.steps = steps
#         self.scenario_title = scenario_title
