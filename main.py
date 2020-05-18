import json
import os

from test_loader import file_system_parser
from testpad import authentication, scripts, statics
from testpad.statics import User, Project

PUBLIC_TESTPAD_URL = 'https://ontestpad.com/login'


def main():
    project = os.getenv('project')
    targetfolder = os.getenv('targetfolder')
    checkout_dir = os.getenv('checkoutDir')
    Project.set(project)
    User.set(authentication.authenticate())
    project, user = statics.set_project_user(project=project, user=User.get())

    loaded = scripts.load_scripts(user=user, project=project, targetfolder=targetfolder)
    assert loaded
    print(json.dumps(loaded, indent=4))
    if checkout_dir.startswith("~"):
        home = os.path.expanduser("~")
        checkout_dir = os.path.join(home, checkout_dir.replace("~/", '', 1))
    l = file_system_parser.list_files(dir_=checkout_dir)
    kv = file_system_parser.structure_files(file_tuples=l)
    print(json.dumps(kv, indent=4))


if __name__ == '__main__':
    main()
