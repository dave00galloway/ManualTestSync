class Loader(object):
    def __init__(self, user=None, project=None, targetfolder=None, checkout_dir=None):
        self.checkout_dir = checkout_dir
        self.targetfolder = targetfolder
        self.project = project
        self.user = user
        # maintain list of dirs and equivalent testpad folders at each level
        # and add new tests and folders until all added
