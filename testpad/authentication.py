import os

import requests
from requests import Response

from main import PUBLIC_TESTPAD_URL
from testpad.statics import User


class AuthenticationData(object):
    def __init__(self, csrf_token=None, session_id=None, username=None, password=None, testpad_url=None, **kwargs):
        if username is None:
            username = os.getenv('username')
        if password is None:
            password = os.getenv('password')
        if testpad_url is None:
            testpad_url = os.getenv('testpadurl')
        self.username = username
        self.csrf_token = csrf_token
        self.session_id = session_id
        self.password = password
        self.testpad_url = testpad_url
        self.kwargs = kwargs


def authenticate(csrf_token=None, session_id=None, username=None, password=None, testpad_url=None, **kwargs):
    _user = AuthenticationData(csrf_token=csrf_token, session_id=session_id, username=username, password=password,
                               testpad_url=testpad_url, kwargs=kwargs)
    public_login_response = requests.get(PUBLIC_TESTPAD_URL)
    _user = update_cookies(response=public_login_response, user=_user)
    headers = testpad_headers(user=_user, referer=PUBLIC_TESTPAD_URL)
    form_data = {
        "csrfmiddlewaretoken": _user.csrf_token,
        "email": _user.username,
        "password": _user.password,
        "js": "y",
        "next": None
    }
    private_login_response = requests.post(PUBLIC_TESTPAD_URL, headers=headers, data=form_data)
    _user = update_cookies(response=private_login_response, user=_user)
    return _user


def update_cookies(response=None, user=None, **kwargs):
    if response is None:
        response = Response()
        if response.status_code is None:
            raise ValueError("response cannot be None local variables = {locals}".format(locals=locals()))
    if user is None:
        user = AuthenticationData(**kwargs)
    _csrf_token, _session_id = None, None

    for cookie in response.cookies:
        if cookie.name == "csrftoken":
            _csrf_token = cookie.value
            user.csrf_token = _csrf_token
        elif cookie.name == "sessionid":
            _session_id = cookie.value
            user.session_id = _session_id
        if _csrf_token and _session_id:
            break

    return user


def testpad_headers(user=None, referer=None, **kwargs):
    if user is None:
        user = User.get()
    headers = {
        'x-csrftoken': user.csrf_token,
        'cookie': "csrftoken={csrftoken}; sessionid={sessionid};".format(csrftoken=user.csrf_token,
                                                                         sessionid=user.session_id),
        'x-requested-with': 'XMLHttpRequest',
        'referer': referer,
        **kwargs
    }
    return headers
