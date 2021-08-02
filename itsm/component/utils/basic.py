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

import datetime
import hashlib
import inspect
import json
import os
import posixpath
import re
import stat
import tarfile
from collections import Counter, namedtuple
from functools import reduce
from itertools import combinations

import six
from celery.result import AsyncResult
from django.db.models.fields.reverse_related import ManyToManyRel
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext as _
from jsonschema import validate
from pypinyin import lazy_pinyin
from rest_framework.exceptions import ValidationError

from common.log import logger
from itsm.component.exceptions import ParamError

# 基础工具包

# 清理终端颜色
COLOR_REMOVE = re.compile(r"\x1b[^m]*m")
CLEAR_COLOR_RE = re.compile(r"\\u001b\[\D{1}|\[\d{1,2}\D?|\\u001b\[\d{1,2}\D?~?", re.I | re.U)
# 换行转换
LINE_BREAK_RE = re.compile(r"\r\n|\r|\n", re.I | re.U)
# ip地址v4版本
IPV4_RE = re.compile(r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}")


def merge_dict_list(dict_list):
    """合并字典列表为单个字典，后面的覆盖前面的
    """

    merged_dict = {}
    for dict_item in dict_list:
        merged_dict.update(dict_item)

    return merged_dict


def get_random_key(name):
    """
    通过中文名生成英文key，并做md5转码返回
    若拼音解析失败，则生成随机key
    """

    try:
        word_list = lazy_pinyin(name)
    except BaseException:
        word_list = [get_random_string(3) for _ in range(3)]

    pinyin_key = "{}-{}".format(".".join(word_list), get_random_string(4))

    return hashlib.md5(pinyin_key.encode("utf-8")).hexdigest()


def get_pinyin_key(name):
    """
    通过中文名生成英文key
    若拼音解析失败，则生成随机key
    """

    try:
        word_list = lazy_pinyin(name)
    except BaseException:
        word_list = [get_random_string(3) for _ in range(3)]

    pinyin_key = "".join(word_list)

    return pinyin_key.upper()


class ComplexRegexField(object):
    """
    复杂正则字符验证
    validate_type：type:list 说明：en：英文   num：0-9数字 ch：中文 numwithoutzero：1-9数字 lower-en：小写a-z upper-en：大写：a-z special：特殊字符
    special_char:用户指定特殊字符，如果没有指定，默认键盘上能输入的其他特殊字符
    min_match_count：至少匹配的type个数 type:int
    start_with：以什么类型的字符开头 type:list
    end_with：以什么类型的字符结束 type:list
    """

    def __init__(self, validate_type=None, min_match_count=1, start_with=None, end_with=None, special_char=""):
        
        if end_with is None:
            end_with = []
        if start_with is None:
            start_with = []
        if validate_type is None:
            validate_type = []
        
        self.validate_type = validate_type
        self.min_match_count = min_match_count if min_match_count else len(validate_type)
        self.start_with = start_with
        self.end_with = end_with
        self.regex_dict = {
            "num": "0-9",
            "numwithoutzero": r"\+|-?[1-9][0-9]",
            "lower_en": "a-z",
            "upper_en": "A-Z",
            "en": "a-zA-Z",
            "ch": "\u4e00-\u9fa5",
            "special": "~!@#$%^&*()_+-=?/; :<>.",
            "email": r"[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}",
            "phone": r"(13[0-9]|14[5|7]|15[0|1|2|3|5|6|7|8|9]|18[0|1|2|3|5|6|7|8|9]|17[6|7|8])\d{8}",
            "id_card": r"(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)",
            "ip": "((?:(?:25[0-5]|2[0-4]\\d|[01]?\\d?\\d)\\.){3}(?:25[0-5]|2[0-4]\\d|[01]?\\d?\\d))",
            "qq": "[1-9][0-9]{4,}",
            "en_num": "a-zA-Z0-9",
            "en_ch": "\u4e00-\u9fa5_a-zA-Z",
            "en_ch_num": "\u4e00-\u9fa5_a-zA-Z0-9",
            "start_en": "a-zA-Z",
        }
        self.regex_display_dict = {
            "num": _("数字0-9"),
            "numwithoutzero": _("不能为0"),
            "lower_en": _("小写字母"),
            "upper_en": _("大写字母"),
            "en": _("英文"),
            "ch": _("中文"),
            "special": special_char,
            "email": _("邮箱"),
            "phone": _("内地手机号码"),
            "id_card": _("身份证"),
            "ip": _("IP地址"),
            "qq": _("腾讯QQ号"),
            "en_num": _("仅能包含英文字符和数字"),
            "en_ch": _("仅能包含中英文字符"),
            "en_ch_num": _("仅能包含中英文，数字，下划线"),
            "start_en": _("包含中英文，数字，以英文字符开头"),
        }
        self.regex_error_display = [
            str(value) for key, value in list(self.regex_display_dict.items()) if key in self.validate_type
        ]
        if special_char:
            self.regex_dict["special"] = special_char
        if not self.validate_type:
            self.validate_type = list(self.regex_dict.keys())

    def get_regex(self):
        regex_list = list(
            combinations(
                ["(?=.*[%s])" % self.regex_dict.get(type_key, "") for type_key in self.validate_type],
                self.min_match_count,
            )
        )
        start_pattern = (
            "[%s]" % "".join([self.regex_dict.get(type_key, "") for type_key in self.start_with])
            if self.start_with
            else ""
        )
        end_pattern = (
            "[%s]" % "".join([self.regex_dict.get(type_key, "") for type_key in self.end_with]) if self.end_with else ""
        )
        include_rules = "".join([self.regex_dict.get(type_key, "") for type_key in self.validate_type])
        include_pattern = "^{}[{}]*{}$".format(start_pattern, include_rules, end_pattern)
        end_pattern = "^.*%s$" % end_pattern
        start_pattern = "^%s.*$" % start_pattern
        least_pattern = "^%s.*$" % "|".join(["".join(item) for item in regex_list])
        return include_pattern, least_pattern, start_pattern, end_pattern

    def validate(self, value):
        if not value:
            return
        include_pattern, least_pattern, start_pattern, end_pattern = self.get_regex()
        if list(set(self.start_with).difference(self.validate_type)):
            raise ValidationError(_("包含了指定字符【{}】以外的内容").format(",".join(self.regex_error_display)), code="not-matched")
        if list(set(self.end_with).difference(self.validate_type)):
            raise ValidationError(_("包含了指定字符【{}】以外的内容").format(",".join(self.regex_error_display)), code="not-matched")
        if not re.match(start_pattern, value):
            raise ValidationError(_("开头格式不正确"), code="not-matched")
        if not re.match(end_pattern, value):
            raise ValidationError(_("结尾格式不正确"), code="not-matched")
        if not re.match(include_pattern, value):
            raise ValidationError(
                _("输入格式不正确：包含了指定字符【{}】以外的内容").format(",".join(self.regex_error_display)), code="not-matched"
            )
        if not re.match(least_pattern, value):
            raise ValidationError(
                _("至少需要匹配%s种字符(%s)") % (self.min_match_count, ",".join(self.regex_error_display)), code="not-matched"
            )


class Regex(object):
    def __init__(self, validate_type=""):
        self.validate_type = validate_type
        self.regex_dict = {
            "num": r"^[0-9]$",
            "numwithoutzero": r"^\+|-?[1-9][0-9]*$",
            "float": r"^(-?\d+)(\.\d+)?$",
            "non_negative": r"^[1-9]\d*\.\d*|0\.\d*[1-9]\d*|[0-9]\d*$",
            "non_positive": r"^(-([1-9]\d*\.\d*|0\.\d*[1-9]\d*|[1-9]\d*))|0?\.0+|0$",
            "gte_zero": r"^[1-9]\d*\.\d*|0\.\d*[1-9]\d*|[1-9]\d*$",
            "lte_zero": r"^(-([1-9]\d*\.\d*|0\.\d*[1-9]\d*| [1-9]\d*))$",
            "lower_en": "^[a-z]*$",
            "upper_en": "^[A-Z]*$",
            "en": "^[a-zA-Z]*$",
            "ch": "^[\u4e00-\u9fa5]*$",
            "email": r"^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$",
            "phone_num": r"^(13[0-9]|14[5|7]|15[0|1|2|3|5|6|7|8|9]|18[0|1|2|3|5|6|7|8|9]|17[6|7|8])\d{8}$",
            "id_card": r"(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)",
            "ip": "((?:(?:25[0-5]|2[0-4]\\d|[01]?\\d?\\d)\\.){3}(?:25[0-5]|2[0-4]\\d|[01]?\\d?\\d))",
            "qq": "[1-9][0-9]{4,20}$",
            "en_num": "^[a-zA-Z0-9]*$",
            "en_ch": "^[\u4e00-\u9fa5_a-zA-Z]*$",
            "en_ch_num": "^[\u4e00-\u9fa5_a-zA-Z0-9]*$",
            "start_en": "^[a-zA-Z]",
        }
        # 待确认
        self.regex_display_dict = {
            "num": _("数字0-9"),
            "numwithoutzero": _("数字首位只能为1-9"),
            "float": _("浮点数"),
            "non_negative": _("非负数（0，正数，正浮点数）"),
            "non_positive": _("非正数（0，负数，负浮点数）"),
            "gte_zero": _("大于零的数（包括正数和正浮点数）"),
            "lte_zero": _("小于零的数（包括负数和负浮点数）"),
            "lower_en": _("小写字母"),
            "upper_en": _("大写字母"),
            "en": _("英文"),
            "ch": _("中文"),
            "email": _("邮箱"),
            "phone_num": _("内地手机号码"),
            "id_card": _("身份证"),
            "ip": _("IP地址"),
            "qq": _("腾讯QQ号"),
            "en_num": _("仅能包含英文字符和数字"),
            "en_ch": _("仅能包含中英文字符"),
            "en_ch_num": _("仅能包含中英文，数字，下划线"),
            "start_en": _("包含中英文，数字，以英文字符开头"),
        }
        self.regex_error_display = [
            value for key, value in list(self.regex_display_dict.items()) if key == self.validate_type
        ]

    def validate(self, value):
        if not value:
            return
        pattern = self.regex_dict.get(self.validate_type, "")
        if not re.match(pattern, value):
            raise ValidationError(
                _("输入格式不正确：包含了指定字符【{}】以外的内容").format(",".join(self.regex_error_display)), code="not-matched"
            )


def now():
    """
    返回当前时间
    """
    return timezone.now()


def better_time_or_none(time):
    return time.strftime("%Y-%m-%d %H:%M:%S") if time else time


def time_delta(hours=1, minutes=30):
    """
    时间间隔
    """
    return datetime.timedelta(hours=hours, minutes=minutes)


def index_of_list(objarr, key, val):
    """
    根据对象的某一属性寻找对象在其所在列表中的位置
    """
    return next((k for k, v in enumerate(objarr) if v[key] == val), -1)


def safe_cast(val, to_type, default=None):
    """
    安全类型转换
    """
    try:
        return to_type(val)
    except ValueError:
        return default or val
    except TypeError:
        return default or val


def duplicate_check(id_list):
    """
    重复元素校验
    """

    # 筛选出现次数大于1的元素
    return len([k for k, v in list(Counter(id_list).items()) if v > 1]) > 0


def safe_remove(file_path):
    """
    安全删除文件
    """
    try:
        os.remove(file_path)
    except BaseException:
        pass


def deep_getattr(obj, attr):
    """
    Recurses through an attribute chain to get the ultimate value.
    http://pingfive.typepad.com/blog/2010/04/deep-getattr-python-function.html
    """
    return reduce(getattr, attr.split("."), obj)


def group_by(item_list, key_or_index_tuple, dict_result=False, aggregate=None, as_key=None):
    """
    对列表中的字典元素进行groupby操作，依据为可排序的某个key
    :param item_list: 待分组字典列表或元组列表
    :param key_or_index_tuple: 分组关键字或位置列表
    :param dict_result: 是否返回字典格式
    :return: 可迭代的groupby对象或者字典
    :ref: http://stackoverflow.com/questions/21674331/
    group-by-multiple-keys-and-summarize-average-values-of-a-list-of-dictionaries
    """
    from itertools import groupby
    from operator import itemgetter

    list_sorted = sorted(item_list, key=itemgetter(*key_or_index_tuple))
    group_result = groupby(list_sorted, key=itemgetter(*key_or_index_tuple))
    if dict_result:
        return {k: list(g) for k, g in group_result}
    else:
        return group_result


def revoke_task(task):
    """
    递归revoke
    """

    if task.children:
        for child in task.children:
            revoke_task(child)
            # 终止未执行的任务
            # if not task.ready():
            #     task.revoke(terminate=True)

    try:
        task.revoke(terminate=True)
    except BaseException:
        pass


def parse_color(content):
    """
    成功/失败/正常/异常/结果/返回码
    <span class="agent-color-red">中转机登录失败</span>
    """

    color_pattern_list = [
        {
            "pattern": [
                _("失败"),
                _("异常"),
                _("超时"),
                _("放弃"),
                _("无法"),
                _("错误码"),
                _("错误"),
                _("批量安装作业启动失败"),
                _("command not found"),
                _("error"),
                _("exception"),
                _("timeout"),
                _("failed"),
                _("setup failed"),
                _("no such file or directory"),
            ],
            "class": "agent-color-red",
        },
        {
            "pattern": [
                _("执行成功"),
                _("启动成功"),
                _("发送成功"),
                _("成功录入cmdb"),
                _("Done"),
                _("step done"),
                _("正常"),
                _("install_success"),
                _("success"),
                _("100%"),
            ],
            "class": "agent-color-green",
        },
        {"pattern": [], "class": "agent-color-gray"},
        {
            "pattern": [_("返回码"), _("执行完毕"), _("作业参数"), _("curl"), _("status"), _("agent状态"), _("yum"), _("apt-get")],
            "class": "agent-color-black",
        },
        {
            "pattern": [
                _("warning"),
                _("执行命令"),
                _("输出结果"),
                _("add crontab task failed. you can add it manually"),
                _("Failed to register host to cmdb. you can register it manually"),
            ],
            "class": "agent-color-orange",
        },
        {"pattern": IPV4_RE, "class": "agent-color-black"},
    ]

    # 正则替换
    for color_pattern in color_pattern_list:
        pattern = color_pattern.get("pattern")
        cls = color_pattern.get("class")
        if isinstance(pattern, list):
            # 空规则跳过
            if not pattern:
                continue
            t = re.compile(str("|".join(pattern)), re.IGNORECASE)
        else:
            t = pattern

        pts = set(t.findall(content))
        for kw in pts:
            content = content.replace(kw, '<span class="{}">{}</span>'.format(cls, kw))
    else:
        return content


def log_parser(content):
    """
    \n\r->换行 + 清理终端颜色码 + 特殊颜色标记
    """
    # content = CLEAR_COLOR_RE.sub('', content)
    content = LINE_BREAK_RE.sub("<br/>", content)
    return content


def strftime_local(aware_time, fmt="%Y-%m-%d %H:%M:%S %z"):
    """格式化aware_time为本地时间"""

    if timezone.is_aware(aware_time):
        return timezone.localtime(aware_time).strftime(fmt)

    return aware_time.strftime(fmt)


def tuple_choices(tupl):
    """从django-model的choices转换到namedtuple"""
    return [(t, t) for t in tupl]


def dict_to_choices(dic, is_reversed=False):
    """从django-model的choices转换到namedtuple"""
    if is_reversed:
        return [(v, k) for k, v in six.iteritems(dic)]
    return [(k, v) for k, v in six.iteritems(dic)]


def reverse_dict(dic):
    return {v: k for k, v in six.iteritems(dic)}


def dict_to_namedtuple(dic):
    """从dict转换到namedtuple"""
    return namedtuple("AttrStore", list(dic.keys()))(**dic)


def choices_to_namedtuple(choices):
    """从django-model的choices转换到namedtuple"""
    return dict_to_namedtuple(dict(choices))


def tuple_to_namedtuple(tupl):
    """从tuple转换到namedtuple"""
    return dict_to_namedtuple(dict(tuple_choices(tupl)))


def revoke_celery_task(task_id):
    """
    终止celery任务
    """

    try:
        task = AsyncResult(task_id)
        task.revoke(terminate=True)
    except Exception as e:
        logger.error("revoke_celery_task(Exception): %s" % e)


def rmtree(sftp, remotepath, level=0):
    """
    递归删除操作
    """

    for f in sftp.listdir_attr(remotepath):
        rpath = posixpath.join(remotepath, f.filename)

        # 如果是目录，则递归删除
        if stat.S_ISDIR(f.st_mode):
            rmtree(sftp, rpath, level + 1)
        else:
            sftp.remove(rpath)

    # 删除当前目录
    sftp.rmdir(remotepath)


def ansi_escape(str):
    """终端颜色编码清理"""
    return COLOR_REMOVE.sub("", str)


def extract_tarfile(file_name, target_dir=None):
    """extract tgz file"""
    tar = tarfile.open(file_name)
    target_dir = target_dir or os.path.dirname(file_name)
    tar.extractall(target_dir)
    tar.close()


def generate_random_sn(service_type):
    """单号生成器"""
    from itsm.component.data import incr_expireat, exists
    from itsm.component.constants import PREFIX_KEY

    prefix_mapping = {"event": "INC", "request": "REQ", "change": "CRQ", "question": "PBI"}
    key = PREFIX_KEY + service_type
    when = None
    now_time = now()
    if not exists(key):
        # 设置第二天的0:00:00过期
        when = datetime.datetime(year=now_time.year, month=now_time.month, day=now_time.day) + datetime.timedelta(
            days=1
        )
    num = incr_expireat(key, when=when)
    sn = prefix_mapping[service_type] + now_time.strftime("%Y%m%d") + "{:0>6}".format(num)
    return sn


def size_mapper(size):
    """
    1G/1M/1K/1 --> 1024*1024*1024/1024*1024/1024/1Byte
    """

    if isinstance(size, int):
        return size
    else:
        size = size.lower()

    if size.endswith("g"):
        factor = 1024 * 1024 * 1024.0
    elif size.endswith("m"):
        factor = 1024 * 1024.0
    elif size.endswith("k"):
        factor = 1024.0
    else:
        raise ValidationError(_("格式错误，仅支持【G/M/K】结尾的大小标记字符串."))
    size = size.replace("g", "").replace("m", "").replace("k", "")
    return int(size) * factor


def list_by_separator(dots_str, separator=","):
    """返回逗号分隔的列表，并过滤无效字符串"""
    if not dots_str:
        return []

    dots_list = dots_str.split(separator)
    not_repeat_dots_list = list(set(dots_list))
    # 保证原始顺序
    not_repeat_dots_list.sort(key=dots_list.index)
    return [dot for dot in not_repeat_dots_list if dot]


def dotted_name(nodot_str, mode="both"):
    """字符串首尾追加逗号"""
    mode_dict = {
        "prefix": ",{}",
        "suffix": "{},",
        "both": ",{},",
    }

    if not nodot_str:
        return ""

    return mode_dict.get(mode).format(nodot_str)


def normal_name(dot_str, mode="both"):
    """字符串首尾去掉逗号"""

    if not dot_str:
        return ""

    if dot_str[0] == ",":
        dot_str = dot_str[1:]

    if dot_str[-1] == ",":
        dot_str = dot_str[0:-1]

    return dot_str


def dotted_property(instance, name):
    """
    '' -> ''
    ',aaa,bbb,ccc', -> 'aaa,bbb,ccc'
    """
    property = instance.get(name, "") if isinstance(instance, dict) else getattr(instance, name, "")

    return ",".join(list_by_separator(property))


def create_version_number(create_time=None):
    """生成时间版本号"""

    if create_time:
        return create_time.strftime("%Y%m%d%H%M%S")

    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")


class TempDisableSignal(object):
    """临时关闭信号"""

    def __init__(self, signal, receiver, sender, dispatch_uid=None):
        self.signal = signal
        self.receiver = receiver
        self.sender = sender
        self.dispatch_uid = dispatch_uid

    def __enter__(self):
        self.signal.disconnect(receiver=self.receiver, sender=self.sender, dispatch_uid=self.dispatch_uid)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.signal.connect(receiver=self.receiver, sender=self.sender, weak=False, dispatch_uid=self.dispatch_uid)


def fill_tree_route(pure_tree, pre_routes=None):
    """add routes for tree item"""

    # print pre_routes, '->', pure_tree['name']
    if pre_routes is None:
        pre_routes = []
    pure_tree["route"] = pre_routes

    for child in pure_tree.get("children", []):
        fill_tree_route(child, pre_routes + [{"id": pure_tree["id"], "name": pure_tree["name"]}])


def build_tree(raw_nodes, parent_name, empty_parent=None, need_route=False):
    # modified from: https://stackoverflow.com/a/43984479/274549

    # build node hash map for find
    nodes = {}
    for i in raw_nodes:
        id, obj = (i["id"], i)
        nodes[id] = obj

    forest = []
    for i in raw_nodes:
        id, parent_id, obj = (i["id"], i[parent_name], i)
        node = nodes[id]

        # append to root list or append to children list
        if parent_id == empty_parent:
            forest.append(node)
        else:
            parent = nodes[parent_id]
            if "children" not in parent:
                parent["children"] = []
            parent["children"].append(node)

    # 路径填充
    if need_route:
        for sub_tree in forest:
            fill_tree_route(sub_tree)

    return forest


def jsonschema_validate(schema, instance):
    try:
        validate(instance, schema)
    except Exception as e:
        raise ParamError(_("请求参数校验失败: %s") % str(e))


def walk(node):
    """ iterate tree in pre-order depth-first search order """
    yield node
    for child in node.get("children", []):
        for item in walk(child):
            yield item


def get_model_fields(model_class, name_only=True):
    """获取模型的字段信息"""

    model_fields = model_class._meta.get_fields()
    if name_only:
        return [f.name for f in model_fields if not isinstance(f, ManyToManyRel)]

    return model_fields


def get_function_name():
    return inspect.stack()[1][3]


def dictfetchall(connection, sql, *params, **kwargs):
    """
    Return all rows from a cursor as a dict,
    if kwargs.get("format") == 'list', return as list
    """

    with connection.cursor() as cursor:
        cursor.execute(sql, params)

    columns = [col[0] for col in cursor.description]

    if kwargs.get("format") == "list":
        return list(cursor.fetchall())

    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def convert_bytes_to_str(obj):
    converted = set()

    def _convert(obj, converted):
        if isinstance(obj, dict):
            new_dict = obj.__class__()

            for attr, value in obj.items():

                if isinstance(attr, bytes):
                    attr = attr.decode("utf-8")

                value = _convert(value, converted)

                new_dict[attr] = value

            obj = new_dict

        if isinstance(obj, list):
            new_list = obj.__class__()

            for item in obj:
                new_list.append(_convert(item, converted))

            obj = new_list

        elif isinstance(obj, bytes):

            try:
                obj = obj.decode("utf-8")
            except Exception:
                pass

        elif hasattr(obj, "__dict__"):

            if id(obj) in converted:
                return obj
            else:
                converted.add(id(obj))

            new__dict__ = {}

            for attr, value in obj.__dict__.items():

                if isinstance(attr, bytes):
                    attr = attr.decode("utf-8")

                new__dict__[attr] = _convert(value, converted)

            obj.__dict__ = new__dict__

        return obj

    return _convert(obj, converted)


def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


if __name__ == "__main__":
    raw_nodes = [
        {"id": 1, "parent": -1, "prop1": "blarg", "prop2": "blarg2"},
        {"id": 2, "parent": 1, "prop1": "blarg", "prop2": "blarg2"},
        {"id": 3, "parent": -1, "prop1": "blarg", "prop2": "blarg2"},
        {"id": 4, "parent": 1, "prop1": "blarg", "prop2": "blarg2"},
        {"id": 5, "parent": 1, "prop1": "blarg", "prop2": "blarg2"},
        {"id": 11, "parent": 10, "prop1": "blarg", "prop2": "blarg2"},
        {"id": 12, "parent": 11, "prop1": "blarg", "prop2": "blarg2"},
        {"id": 6, "parent": 2, "prop1": "blarg", "prop2": "blarg2"},
        {"id": 7, "parent": 2, "prop1": "blarg", "prop2": "blarg2"},
        {"id": 8, "parent": 2, "prop1": "blarg", "prop2": "blarg2"},
        {"id": 9, "parent": 3, "prop1": "blarg", "prop2": "blarg2"},
        {"id": 10, "parent": 3, "prop1": "blarg", "prop2": "blarg2"},
    ]

    tree = build_tree(raw_nodes, "parent", -1, True)
    # print(json.dumps(tree, indent=4))

    # for sub_tree in tree:
    #     fill_forest_route(sub_tree)

    print(json.dumps(tree, indent=4))
