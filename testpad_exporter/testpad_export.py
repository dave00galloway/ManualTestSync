import os
import pathlib
import tempfile

from bs4 import BeautifulSoup
from gherkin.parser import Parser
from gherkin.pickles import compiler
from gherkin.token_scanner import TokenScanner

from testpad.reports import report_with_steps


class TestpadExporter(object):
    def __init__(self, user=None, project=None, report_folder=None, out_dir=None):
        if out_dir is None or user is None or project is None or report_folder is None:
            raise ValueError(str(locals()))
        self.out_dir = out_dir

        pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
        self.report_folder = report_folder
        self.project = project
        self.user = user

    def export_tests(self):
        suites = self.parse_tests_to_gherkin(
            report_with_steps(user=self.user, project=self.project, report_folder=self.report_folder))
        for key, gherkin_feature in suites.items():
            suite_dir = "{out_dir}{p}{suite_name}".format(out_dir=self.out_dir, p=os.path.sep,
                                                          suite_name=str(key[0]).replace(' ', ''))
            pathlib.Path(suite_dir).mkdir(parents=True, exist_ok=True)
            feature_file_path = "{suite_dir}{p}{feature_name}.feature".format(suite_dir=suite_dir, p=os.path.sep,
                                                                              feature_name=str(key[1]).replace(' ', '')
                                                                              .replace(os.path.sep, '_'))
            with open(feature_file_path, 'wb') as feature_file:
                self.write_gherkin_file(feature_text=gherkin_feature.raw_text, out_file=feature_file)

        return suites

    def parse_tests_to_gherkin(self, content):
        suites = self.find_test_suites(BeautifulSoup(content, "html.parser"))
        gherkin_suites = {}
        for suite in suites:
            feature = self._find_feature(suite)
            # if feature.feature_name == "Upgrade Tests":
            #     pass
            feature_text = feature.get_feature_text()

            with tempfile.NamedTemporaryFile() as temp_file:
                self.write_gherkin_file(feature_text=feature_text, out_file=temp_file)
                temp_file.seek(0)
                try:
                    gherkin_feature = GherkinFeature(file=temp_file.name, raw_text=feature_text)
                except GherkinError as e:
                    raise GherkinError("unable to parse / pickle feature {feature} in suite {suite}".format(
                        feature=feature.feature_name, suite=feature.suite_name)) from e
            gherkin_suites[(feature.suite_name, feature.feature_name)] = gherkin_feature
        return gherkin_suites

    @staticmethod
    def write_gherkin_file(feature_text=None, out_file=None):
        for line in feature_text:
            split_lines = str(line).split(os.linesep)
            for i, split_line in enumerate(split_lines):
                if i > 0 and len(split_line.strip()) > 0:
                    if not split_line.startswith(("Given", "When", "Then", "And", "given", "when", "then", "and")):
                        split_line = "And {sl}".format(sl=split_line)
                    if split_line[0].islower():
                        split_line = split_line.capitalize()
                out_file.write(bytes(split_line, encoding='utf-8'))
                out_file.write(bytes(os.linesep, encoding='utf-8'))

    @staticmethod
    def find_test_suites(html):
        return html.body.find_all('div', class_='scriptSection withoutBreaks')

    @staticmethod
    def _find_feature(suite):
        heading = suite.find('div', class_="heading")
        suite_name = heading.find('h3').text
        if len(str(suite_name).strip()) == 0:
            suite_name = heading.find('h2').text
        feature_name = heading.find('h1').text
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
    def __init__(self, file=None, raw_text=None):
        self.raw_text = raw_text
        self.file = file
        parser = Parser()
        scanner = TokenScanner(self.file)
        try:
            self.gherkin_document = parser.parse(scanner)
            self.pickles = compiler.compile(self.gherkin_document)
            if len(self.pickles) < 1:
                raise GherkinError("no pickles found!")
        except Exception as e:
            raise GherkinError("unable to parse / pickle doc {doc}".format(doc=self.file)) from e
