import os

from testpad import authentication
from testpad.statics import User, Project
from testpad_exporter.exporter import Exporter


def main():
    report_project = os.getenv('reportProject')

    report_folder = os.getenv('reportFolder')
    # checkout_dir = os.getenv('checkoutDir')
    # if checkout_dir.startswith("~"):
    #     home = os.path.expanduser("~")
    #     checkout_dir = os.path.join(home, checkout_dir.replace("~/", '', 1))

    Project.set(report_project)
    User.set(authentication.authenticate())

    export = Exporter(user=User.get(), project=Project.get(), report_folder=report_folder)
    data = export.export_tests()
    # print(data)


if __name__ == '__main__':
    main()
