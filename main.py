import os

from test_loader import testpad_loader
from testpad import authentication
from testpad.statics import User, Project

PUBLIC_TESTPAD_URL = 'https://ontestpad.com/login'


def main():
    # todo: add argparse to override the env vars which should only be a fallback
    # todo: add logging
    # todo: add unit tests
    # todo: add error handling
    project = os.getenv('project')
    # targetfolder = os.getenv('targetfolder')
    checkout_dir = os.getenv('checkoutDir')
    if checkout_dir.startswith("~"):
        home = os.path.expanduser("~")
        checkout_dir = os.path.join(home, checkout_dir.replace("~/", '', 1))

    Project.set(project)
    User.set(authentication.authenticate())

    ldr = testpad_loader.Loader(user=User.get(), project=Project.get(),  # targetfolder=targetfolder,
                                checkout_dir=checkout_dir)  # , create_folder_func=mock_create_folder)
    ldr.load_tests()


if __name__ == '__main__':
    main()
