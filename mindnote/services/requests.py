from abc import ABC, abstractmethod

import requests
from django.conf import settings

from services.exceptions import ExternalRequestServerError, ExternalRequestClientError, \
    ExternalRequestTimeoutOrUnreachable


class Request(ABC):
    @classmethod
    def instance(cls):
        if settings.TEST:
            return RequestWithTest()

        return RequestWithHttp()

    def get(self, url, data=None, json=None, timeout=None, auth=None, **options):
        return self.request('GET', url, data=data, json=json, timeout=timeout, auth=auth, **options)

    def post(self, url, data=None, json=None, timeout=None, auth=None, **options):
        return self.request('POST', url, data=data, json=json, timeout=timeout, auth=auth, **options)

    @abstractmethod
    def request(self, method, url, data=None, json=None, timeout=None, auth=None, **options):
        pass


class RequestWithHttp(Request):
    def request(self, method, url, data=None, json=None, timeout=None, auth=None, **options):
        timeout = timeout or settings.DEFAULT_TIMEOUT

        response = None
        try:
            response = requests.request(method, url, data=data, json=json, timeout=timeout, auth=auth, **options)

            response.raise_for_status()

        except (requests.exceptions.HTTPError, UnicodeDecodeError):
            # 4xx or parsing error
            # 5xx

            if 500 <= response.status_code:
                raise ExternalRequestServerError

            raise ExternalRequestClientError

        except (requests.exceptions.Timeout, Exception):
            raise ExternalRequestTimeoutOrUnreachable

        return response


class RequestWithTest(Request):
    def request(self, method, url, data=None, json=None, timeout=None, auth=None, **options):
        raise Exception('Mocking needed')
