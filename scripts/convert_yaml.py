# coding: utf-8
# !/usr/bin/env python

import argparse
import json
import os

import yaml


class BasicException(Exception):
    """异常"""

    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="convert yaml to apigw file")
    parser.add_argument("-s", "--source", type=str, help="input yaml file", required=True)
    parser.add_argument("-t", "--target", type=str, help="output dir", required=True)
    parser.add_argument("-n", "--name", type=str, help="output file name", required=False)
    parser.add_argument(
        "-f", "--format", type=str, help="output file format", required=True, choices=["json", "yaml"], default="yaml"
    )
    args = parser.parse_args()

    source, target, format, name = args.source, args.target, args.format, args.name
    name = name or 'apigw_default'

    print(
        """
        ===========================
        source:         {},
        target:         {},
        format:         {},
        name:         {},
        ===========================
    """.format(
            source, target, format, name
        )
    )

    with open(source, 'r', encoding='utf-8') as f:
        apis = yaml.load(f)
        data = [
            {
                "resource_classification": "无分类",
                "headers": {},
                "resource_name": api['name'],
                "description": api['label'],
                "timeout": 10,
                "path": api['path'],
                "registed_http_method": api['suggest_method'],
                "dest_http_method": api['dest_http_method'],
                "dest_url": "http://{stageVariables.domain}" + api['dest_path'][len('/o/bk_itsm') :],
            }
            for api in apis
        ]

        output = open(os.path.join(target, '{}.{}'.format(name, format)), 'w', encoding='utf-8')
        if format == 'json':
            json.dump(data, output, indent=2)
        else:
            yaml.dump(data, output)
