import json
import logging
from datetime import date, datetime
from typing import Any, Optional, Union

import requests

from usermaven.utils import remove_trailing_slash
from usermaven.settings import DEFAULT_HOST, USER_AGENT

_session = requests.sessions.Session()


def post(
    api_key: str, server_token: str, host: Optional[str] = None, path=None, timeout: int = 15, **kwargs
) -> requests.Response:
    """Post the `kwargs` to the API"""
    log = logging.getLogger("usermaven")
    body = kwargs
    url = remove_trailing_slash(host or DEFAULT_HOST) + path
    data = body["batch"]
    log.debug("making request: %s", data)
    headers = {"Content-Type": "application/json", "User-Agent": USER_AGENT}
    server_secret_key = api_key + "." + server_token
    res = _session.post(url, params={'token': server_secret_key}, json=data, headers=headers, timeout=timeout)

    if res.status_code == 200:
        log.debug("data uploaded successfully")

    return res


def _process_response(
    res: requests.Response, success_message: str, *, return_json: bool = True
) -> Union[requests.Response, Any]:
    log = logging.getLogger("usermaven")
    if res.status_code == 200:
        log.debug(success_message)
        return res.json() if return_json else res
    try:
        payload = res.json()
        log.debug("received response: %s", payload)
        raise APIError(res.status_code, payload["detail"])
    except (KeyError, ValueError):
        raise APIError(res.status_code, res.text)


def batch_post(
    api_key: str, server_token: str, host: Optional[str] = None, timeout: int = 15, **kwargs
) -> requests.Response:
    """Post the `kwargs` to the batch API endpoint for events"""
    res = post(api_key, server_token, host, "/api/v1/s2s/event/", timeout, **kwargs)
    return _process_response(res, success_message="data uploaded successfully", return_json=False)


class APIError(Exception):
    def __init__(self, status: Union[int, str], message: str):
        self.message = message
        self.status = status

    def __str__(self):
        msg = "[Usermaven] {0} ({1})"
        return msg.format(self.message, self.status)


class DatetimeSerializer(json.JSONEncoder):
    def default(self, obj: Any):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)
