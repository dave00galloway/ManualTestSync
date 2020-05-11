import json
import os

from testpad import authentication, scripts
from testpad.statics import User, Project

PUBLIC_TESTPAD_URL = 'https://ontestpad.com/login'


def main():
    project = os.getenv('project')
    targetfolder = os.getenv('targetfolder')
    Project.set(project)
    User.set(authentication.authenticate())

    loaded = scripts.load_scripts(user=User.get(), project=project, targetfolder=targetfolder)
    assert loaded
    print(json.dumps(loaded, indent=4))


if __name__ == '__main__':
    main()
