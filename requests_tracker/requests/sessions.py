# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.

License for BK-ITSM 蓝鲸流程服务:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

# requests_tracker.requests
# =========================
from requests.models import Request
from requests.packages.urllib3.connectionpool import HTTPConnectionPool
from requests.sessions import Session as _Session

from django.utils.timezone import now
from requests_tracker.signals import request_failed, response
from requests_tracker.utils.unique import uniqid


__implements__ = ['Session']


def _make_request(self, conn, method, url, **kwargs):
    resp = self._old_make_request(conn, method, url, **kwargs)
    sock = getattr(conn, 'sock', False)
    if sock:
        setattr(resp, 'peer', sock.getpeername())
    else:
        setattr(resp, 'peer', None)
    return resp


HTTPConnectionPool._old_make_request = HTTPConnectionPool._make_request
HTTPConnectionPool._make_request = _make_request


class Session(_Session):

    def request(self, method, url,
                params=None,
                data=None,
                headers=None,
                cookies=None,
                files=None,
                auth=None,
                timeout=None,
                allow_redirects=True,
                proxies=None,
                hooks=None,
                stream=None,
                verify=None,
                cert=None,
                json=None,
                **kwargs):
        """
        patched requests.session.Session
        """
        # Create the Request.
        req = Request(
            method=method.upper(),
            url=url,
            headers=headers,
            files=files,
            data=data or {},
            json=json,
            params=params or {},
            auth=auth,
            cookies=cookies,
            hooks=hooks
        )
        prep = self.prepare_request(req)

        proxies = proxies or {}

        settings = self.merge_environment_settings(
            prep.url, proxies, stream, verify, cert
        )

        # Send the request.
        send_kwargs = {
            'timeout': timeout,
            'allow_redirects': allow_redirects,
        }
        send_kwargs.update(settings)

        # make request uid
        uid = uniqid()
        before_time = now()

        # Send the request.
        try:
            resp = self.send(prep, **send_kwargs)
            response.send(
                sender=self.request,
                uid=uid,
                prep=prep,
                resp=resp,
                duration=now() - before_time,
                **kwargs
            )

            return resp
        except Exception as e:
            request_failed.send(
                sender=self.request,
                uid=uid,
                prep=prep,
                exception=e,
                duration=now() - before_time,
                **kwargs
            )
