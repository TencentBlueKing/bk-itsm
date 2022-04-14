# -*- coding: utf-8 -*-
import json
from urllib import parse

from jinja2 import Template
from requests.auth import HTTPBasicAuth
from requests_toolbelt import MultipartEncoder


class EncodeWebhook(object):
    def __init__(self, kv=None):
        self.kv = kv or {}

    @staticmethod
    def encode_authorization(authorize):
        auth_type = authorize.get("auth_type")
        auth_config = authorize.get("auth_config")
        if auth_type == "basic_auth":
            return HTTPBasicAuth(auth_config["username"], auth_config["password"])

    def encode_body(self, body):
        if not body:
            return b""
        data_type = body["type"]
        encode_method = getattr(self, "encode_{}_body".format(data_type), None)
        if encode_method is None:
            return b""

        return encode_method(body)

    def encode_raw_body(self, body):
        """
        组装raw格式的headers
        """

        if isinstance(body["content"], str):
            return body["content"].encode("utf-8")
        from django.template import Template  # noqa

        content = Template(body["content"]).render(self.kv)
        return json.dumps(content)

    def encode_form_data_body(self, body):
        params = body.get("params", [])
        fields = {}
        for item in params:
            template = Template(item["value"])
            fields[item["key"]] = template.render(self.kv)

        multipart_data = MultipartEncoder(fields=fields)
        return multipart_data.to_string()

    def encode_x_www_form_urlencoded_body(self, body):
        """
        x-www-form-urlencoded数据格式组装
        """
        params = body.get("params", [])
        fields = {}
        for item in params:
            template = Template(item["value"])
            fields[item["key"]] = template.render(self.variables)
        data = parse.urlencode(fields)
        return data.encode("utf-8")
