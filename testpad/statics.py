class User(object):
    USER = None

    @classmethod
    def get(cls):
        return cls.USER

    @classmethod
    def set(cls, value):
        cls.USER = value


class Project(object):
    PROJECT = None

    @classmethod
    def get(cls):
        return cls.PROJECT

    @classmethod
    def set(cls, value):
        cls.PROJECT = value


def set_project_user(project=None, user=None):
    if user is None:
        user = User.get()
    if project is None:
        project = Project.get()
    return project, user


if __name__ == '__main__':
    import os
    import json
    from testpad import authentication

    target_folder = os.getenv('targetfolder')
    Project.set(os.getenv('project'))
    User.set(authentication.authenticate())
    hdrs = authentication.testpad_headers(thing="stuff", otherthings="more stuff")
    print(json.dumps(hdrs, indent=4))
