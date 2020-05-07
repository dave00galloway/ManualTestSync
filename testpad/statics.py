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
