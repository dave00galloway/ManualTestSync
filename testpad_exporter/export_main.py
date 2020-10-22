import argparse
import os
import time
from argparse import RawTextHelpFormatter

from test_rails.csv_importer import TestRailCSVImporter
from testpad import authentication
from testpad.statics import User, Project
from testpad_exporter.testpad_export import TestpadExporter


def main():
    parser = argparse.ArgumentParser(
        description="run export from testpad ",
        epilog="pycharm help\n"
               "=============\n"
               "tbc \n",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument('-p', '--report_project', help='report_project', default=os.getenv('reportProject'))
    parser.add_argument('-f', '--report_folder', help='report_folder', default=os.getenv('reportFolder'))
    parser.add_argument('-o', '--out_dir', help='out_dir', default=os.getenv('out_dir'))

    args = parser.parse_args()
    report_project = args.report_project
    report_folder = args.report_folder
    out_dir = args.out_dir

    if out_dir.startswith("~"):
        home = os.path.expanduser("~")
        out_dir = os.path.join(home, out_dir.replace("~/", '', 1), str(time.time()).replace('.', ''))

    Project.set(report_project)
    User.set(authentication.authenticate())

    export = TestpadExporter(user=User.get(), project=Project.get(), report_folder=report_folder, out_dir=out_dir)
    print(out_dir)
    suites = export.export_tests()
    # importer = TestRailXMLImporter(out_dir=out_dir, suites=suites)
    # importer.create_sections()
    # importer.create_xml_for_import()
    importer = TestRailCSVImporter(out_dir=out_dir, suites=suites)
    importer.create_sections()
    importer.create_csv_for_import()
    # print(data)


if __name__ == '__main__':
    main()
