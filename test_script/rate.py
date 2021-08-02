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


def get_rate():
    with open("last_rate") as fp:
        last_rate = fp.readline()
        last_rate = float(last_rate) if last_rate else 0

    with open("coverage.xml") as fp:
        for i in range(5):
            line = fp.readline()
            if "line-rate" in line:
                value = line.split("line-rate=")[1].split()[0]
                print("value is {}".format(float(eval(value))))
                rate = float(eval(value))
                print("last_rate is {}, current rate is {}".format(last_rate, rate))
                if last_rate > rate:
                    raise Exception(
                        "Unit test coverage does not meet the requirements, "
                        "last_rate {} > current rate {}, please modify and submit".format(last_rate, rate)
                    )
                with open("last_rate", "w") as fp:
                    fp.write(str(rate))
                break


if __name__ == "__main__":
    get_rate()
