# -*- coding: utf-8 -*-
import json
from urllib import parse

from requests_toolbelt import MultipartEncoder
from requests.auth import HTTPBasicAuth, AuthBase


class HTTPBearerToken(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        authstr = "Bearer " + self.token
        r.headers["Authorization"] = authstr
        return r


class EncodeWebhook(object):
    def __init__(self, headers=None):
        self.headers = headers or {}

    @staticmethod
    def encode_authorization(authorize):
        auth_type = authorize.get("auth_type")
        auth_config = authorize.get("auth_config")
        if auth_type == "basic_auth":
            return HTTPBasicAuth(auth_config["username"], auth_config["password"])
        if auth_type == "bearer_token":
            return HTTPBearerToken(auth_config["token"])

    def encode_body(self, body):
        if not body:
            return b""
        data_type = body["type"]
        encode_method = getattr(
            self, "encode_{}_body".format(data_type.replace("-", "_")), None
        )
        if encode_method is None:
            return b""

        return encode_method(body)

    def encode_raw_body(self, body):
        """
        组装raw格式的headers
        """
        content_type_headers = {
            "json": "application/json",
            "text": "text/plain",
            "javascript": "application/javascript",
            "html": "text/html",
            "xml": "application/xml",
        }

        raw_type = body["raw_type"]
        self.headers.update(
            {"Content-Type": content_type_headers.get(raw_type.lower(), "text/plain")}
        )
        if isinstance(body["content"], str):
            return body["content"].encode("utf-8")
        return json.dumps(body["content"])

    def encode_form_data_body(self, body):
        params = body.get("params", [])
        multipart_data = MultipartEncoder(
            fields={item["key"]: item["value"] for item in params}
        )
        self.headers.update({"Content-Type": multipart_data.content_type})
        return multipart_data.to_string()

    def encode_x_www_form_urlencoded_body(self, body):
        """
        x-www-form-urlencoded数据格式组装
        """
        params = body.get("params", [])
        self.headers.update(
            {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
        )
        data = parse.urlencode({item["key"]: item["value"] for item in params})
        return data.encode("utf-8")
