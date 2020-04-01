import os

import requests
from requests import Response


def main():
    csrf_token = None
    session_id = None
    a = requests.get('https://ontestpad.com/login')
    print(a.status_code)
    print(a.cookies.items())

    csrf_token, session_id = update_cookies(a, csrf_token, session_id)
    update_cookies()

    # csrftoken1 = "ylQA0LzyufPrOGC0slEMbPKhaiQVf5y9"
    # sessionid1 = "n5b65ddshtoroxwhedbva3va22tidwmq"
    headers2 = {
        "x-csrftoken": csrf_token,
        "referer": "https://ontestpad.com/login",
        'cookie': "csrftoken={csrftoken}; sessionid={sessionid};".format(csrftoken=csrf_token, sessionid=session_id)
    }
    b = requests.post(
        'https://ontestpad.com/login',
        headers=headers2,
        json='{"data":null}')
    print(b.status_code)
    print(b.cookies.items())

    csrftoken2 = "ylQA0LzyufPrOGC0slEMbPKhaiQVf5y9"
    sessionid2 = "n5b65ddshtoroxwhedbva3va22tidwmq"
    headers3 = {
        "x-csrftoken": csrftoken2,
        "referer": "https://ontestpad.com/login",
        'cookie': "csrftoken={csrftoken}; sessionid={sessionid};".format(csrftoken=csrftoken2, sessionid=sessionid2)
    }
    c = requests.post(
        'https://ontestpad.com/login',
        headers=headers3,
        json='{"data":null}')
    print(c.status_code)
    print(c.cookies.items())

    csrftoken3 = os.getenv('csrftoken')
    sessionid3 = os.getenv('sessionid')
    testpadurl = os.getenv('testpadurl')
    project = os.getenv('project')
    targetfolder = os.getenv('targetfolder')
    headers = {
        'x-csrftoken': csrftoken3,
        'referer': "{url}/{project}/{folder}".format(url=testpadurl, project=project, folder=targetfolder),
        'cookie': "csrftoken={csrftoken}; sessionid={sessionid};".format(csrftoken=csrftoken3, sessionid=sessionid3)
    }
    d = requests.post(
        '{url}/a/{project}/{folder}/loadScripts'.format(url=testpadurl, project=project, folder=targetfolder),
        headers=headers, json='{"data":null}')
    print(d.status_code)


def update_cookies(response=None, csrf_token=None, session_id=None):
    if response is None:
        response = Response()
        if response.status_code is None:
            raise ValueError("response cannot be None local variables = {locals}".format(locals=locals()))
    _csrf_token, _session_id = None, None

    for cookie in response.cookies:
        if cookie.name == "csrftoken":
            _csrf_token = cookie.value
        if cookie.name == "sessionid":
            _session_id = cookie.value
        if csrf_token and session_id:
            break

    csrf_token, session_id = _csrf_token, _session_id
    return csrf_token, session_id


if __name__ == '__main__':
    main()
