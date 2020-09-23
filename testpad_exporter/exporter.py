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
        html = BeautifulSoup(content, "html.parser")
        suites = self.find_test_suites(html)
        for suite in suites:
            feature = self._find_feature(suite)
            print(feature.suite_name, feature.feature_name, feature.scenarios)
        return suites

    @staticmethod
    def find_test_suites(html):
        return html.body.find_all('div', class_='scriptSection withBreaks page')

    def _find_feature(self, suite):
        suite_name = suite.find('div', class_="heading").find('h2').text
        feature_name = suite.find('div', class_="heading").find('h1').text
        scenarios = suite.find('table', class_="scriptGrid")
        return ExportableFeature(suite_name=suite_name, feature_name=feature_name, scenarios=scenarios)


class ExportableFeature(object):
    def __init__(self, suite_name=None, feature_name=None, scenarios=None):
        self.scenarios = scenarios
        self.feature_name = feature_name
        self.suite_name = suite_name
