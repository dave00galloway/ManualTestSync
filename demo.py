import os

import requests


def main():
    print(os.getenv('url'))
    print(os.getenv('username'))
    print(os.getenv('password'))

    csrftoken = os.getenv('csrftoken')
    sessionid = os.getenv('sessionid')
    testpadurl = os.getenv('testpadurl')
    project = os.getenv('project')
    targetfolder = os.getenv('targetfolder')

    headers = {
        'x-csrftoken': csrftoken,
        'referer': "{url}/{project}/{folder}".format(url=testpadurl, project=project, folder=targetfolder),
        'cookie': "csrftoken={csrftoken}; sessionid={sessionid};".format(csrftoken=csrftoken, sessionid=sessionid)
    }

    a = requests.post(
        '{url}/a/{project}/{folder}/loadScripts'.format(url=testpadurl, project=project, folder=targetfolder),
        headers=headers, json='{"data":null}')
    print(a.status_code)

    assert a.json()['data'][0]['_id']


if __name__ == '__main__':
    main()
