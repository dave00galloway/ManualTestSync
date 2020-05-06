class User(object):
    USER = None

    @classmethod
    def get(cls):
        return cls.USER

    @classmethod
    def set(cls, value):
        cls.USER = value
