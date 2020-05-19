import os


def get_suites(dir_=None):
    if dir_ is None:
        raise ValueError("dir_cannot be None")
    return structure_files(file_tuples=list_files(dir_=dir_))


def list_files(dir_=None):
    r = []
    for root, dirs, files in os.walk(dir_):
        for name in files:
            if name.endswith(".feature"):
                file_path_minus_root_dir = root.replace(dir_, '', 1)
                r.append((file_path_minus_root_dir, name))
    return r


def structure_files(file_tuples=None):
    if file_tuples is None:
        file_tuples = [("path-to-files", "name-of-feature.feature")]
    suites = {}
    for item in file_tuples:
        if item[0] not in suites.keys():
            suites.update({item[0]: [item[1]]})
        else:
            suites[item[0]].append(item[1])
    return suites


if __name__ == '__main__':
    home = os.path.expanduser("~")
    l = list_files(os.path.join(home, "git/cucumber/cucumber-jvm"))
    kv = structure_files(file_tuples=l)
    print(kv)
