# -*- coding: utf-8 -*-
import sys
import yaml


def add_sub_path(yaml_path):
    file = open(yaml_path, "r", encoding="utf-8")
    file_data = file.read()
    file.close()

    data = yaml.safe_load(file_data)

    for p, p_info in data.get("paths", {}).items():
        for method, m_info in p_info.items():
            url_path = m_info["x-bk-apigateway-resource"]["backend"]["path"]
            m_info["x-bk-apigateway-resource"]["backend"]["path"] = "{}{}".format(
                "/{env.api_sub_path}", url_path[0:]
            )

    file = open(yaml_path, "w")
    yaml.dump(data, file)
    file.close()


if __name__ == "__main__":
    # 为所有path添加env.api_sub_path前缀
    path = sys.argv[1]
    add_sub_path(path)
