import os

from test_loader import file_system_parser
from testpad import folders, authentication
from testpad.scripts import create_script, populate_script
from testpad.statics import User, Project


class Loader(object):
    def __init__(self, user=None, project=None, targetfolder=None, checkout_dir=None, create_folder_func=None):
        self.checkout_dir = checkout_dir
        self.targetfolder = targetfolder
        self.project = project
        self.user = user
        # maintain list of dirs and equivalent testpad folders at each level
        # and add new tests and folders until all added
        self.suites_to_load = {}
        self.dir_structure = {}
        if create_folder_func is None:
            create_folder_func = folders.create_folder
        self.create_folder_func = create_folder_func

    def load_tests(self):
        self.suites_to_load = file_system_parser.get_suites(dir_=self.checkout_dir)
        for suite in self.suites_to_load.keys():
            target_folder = None
            levels = suite.strip(os.sep).split(os.sep)
            iterable_levels = levels.copy()
            last_level = None
            for level in iterable_levels:
                next_level = level
                if last_level:
                    next_level = os.path.join(last_level, level)
                if next_level not in self.dir_structure.keys():
                    target = self.dir_structure[last_level] if last_level else self.targetfolder
                    folder_id = self.create_folder_func(user=self.user, project=self.project,
                                                        targetfolder=target,
                                                        name=level)
                    self.dir_structure[next_level] = folder_id
                    target_folder = folder_id
                last_level = next_level
            for feature in self.suites_to_load[suite]:
                script_id = create_script(user=self.user, project=self.project, targetfolder=target_folder,
                                          name=os.path.splitext(feature)[0])['data']['id']
                # script_id = 1
                # use last level rather than suite since os.path.join treats suite as an absolute path
                feature_path = os.path.join(self.checkout_dir, last_level, feature)
                with open(feature_path) as feature_file:
                    populate_script(user=self.user, project=self.project, script_id=script_id,
                                    text=feature_file.read())


if __name__ == '__main__':
    home = os.path.expanduser("~")
    project = os.getenv('project')
    targetfolder = os.getenv('targetfolder')
    checkout_dir = os.getenv('checkoutDir')
    if checkout_dir.startswith("~"):
        home = os.path.expanduser("~")
        checkout_dir = os.path.join(home, checkout_dir.replace("~/", '', 1))
    fake_folder_no = 1


    def mock_create_folder(name=None, **kwargs):
        global fake_folder_no
        fake_folder = "f{no}".format(no=fake_folder_no)
        fake_folder_no = fake_folder_no + 1
        return fake_folder


    Project.set(project)
    User.set(authentication.authenticate())

    ldr = Loader(user=User.get(), project=Project.get(), #targetfolder=targetfolder,
                 checkout_dir=checkout_dir)  # , create_folder_func=mock_create_folder)
    ldr.load_tests()
