from bs4 import BeautifulSoup

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
        for suite in suites:
            feature = self._find_feature(suite)
            print(feature.suite_name, feature.feature_name)  # , feature.scenarios)
            feature_text = feature.get_feature_text()
            print(feature_text)
        return suites

    @staticmethod
    def find_test_suites(html):
        return html.body.find_all('div', class_='scriptSection withoutBreaks')

    @staticmethod
    def _find_feature(suite):
        suite_name = suite.find('div', class_="heading").find('h3').text
        feature_name = suite.find('div', class_="heading").find('h1').text
        scenarios = suite.find('table', class_="scriptGrid")
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


class ExportableScenario(object):
    def __init__(self, scenario_title=None, steps=None):
        self.steps = steps
        self.scenario_title = scenario_title
