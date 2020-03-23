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
        'x-csrftoken' : ('%s' % csrftoken),
        'referer' : ('%s%s/%s' % (testpadurl, project, targetfolder)),
        'cookie': ('csrftoken=%s; sessionid=%s;' % (csrftoken, sessionid))
    }

    a = requests.post('%s/a%s/%sloadScripts' % (testpadurl, project, targetfolder), headers=headers, json='{"data":null}')
    print(a.status_code)

    assert a.json()['data'][0]['_id']

if __name__ == '__main__':
    main()