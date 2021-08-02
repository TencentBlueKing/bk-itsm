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

# pylint: skip-file

CREATOR_SQL = {
    "days": (
        "SELECT t1.date_str, COALESCE(t2.count, 0) as count FROM(SELECT @cdate:= date_add(@cdate,interval - 1 day) as"
        " date_str , 0 as count FROM (SELECT @cdate:=date_add(CURDATE(),interval + 1 day) from ticket_ticket limit 366)"
        " tmp1 where @cdate >= '{}') t1 LEFT JOIN(select DATE_FORMAT(create_at,'%Y-%m-%d') date_str, count(distinct"
        " creator) as count from ticket_ticket GROUP BY date_str) t2 on t1.date_str = t2.date_str where"
        " t1.date_str<='{}' order by t1.date_str; "
    ),
    "weeks": (
        "SELECT t1.date_str, COALESCE(t2.count, 0) as count FROM(SELECT @cdate:= date_add(@cdate,interval - 1 week) as"
        " date_str , 0 as count FROM (SELECT @cdate:=date_add(subdate(curdate(),date_format(curdate(),'%w')-1),interval"
        " + 1 week) from ticket_ticket) tmp1 where @cdate > '{}') t1 LEFT JOIN(select DATE_FORMAT(create_at,'%Y%u')"
        " date_str, count(distinct creator) as count from ticket_ticket GROUP BY date_str) t2 on"
        " YEARWEEK(t1.date_str,1) = t2.date_str where t1.date_str<='{}' order by t1.date_str;"
    ),
    "months": (
        "SELECT t1.date_str, COALESCE(t2.count, 0) as count FROM(SELECT @cdate:= date_add(@cdate,interval - 1 month) as"
        " date_str , 0 as count FROM (SELECT @cdate:=date_add(curdate()-day(curdate())+1,interval 1 month) from"
        " ticket_ticket) tmp1 where @cdate > '{}') t1 LEFT JOIN(select DATE_FORMAT(create_at,'%Y-%m') date_str,"
        " count(distinct creator) as count from ticket_ticket GROUP BY date_str) t2 on left(t1.date_str,7) ="
        " t2.date_str where t1.date_str<='{}' order by t1.date_str;"
    ),
    "years": (
        "SELECT DATE_FORMAT(create_at,'%Y') years,count(distinct creator) count from ticket_ticket group by years;"
    ),
}

TICKET_SQL = {
    "days": (
        "SELECT t1.date_str, COALESCE(t2.count, 0) as count FROM(SELECT @cdate:= date_add(@cdate,interval - 1 day) as"
        " date_str , 0 as count FROM (SELECT @cdate:=date_add(CURDATE(),interval + 1 day) from ticket_ticket limit 366)"
        " tmp1 where @cdate >= '{}') t1 LEFT JOIN(select DATE_FORMAT(create_at,'%Y-%m-%d') date_str, count(id) as count"
        " from ticket_ticket GROUP BY date_str) t2 on t1.date_str = t2.date_str where t1.date_str<='{}' order by"
        " t1.date_str; "
    ),
    "weeks": (
        "SELECT t1.date_str, COALESCE(t2.count, 0) as count FROM(SELECT @cdate:= date_add(@cdate,interval - 1 week) as"
        " date_str , 0 as count FROM (SELECT @cdate:=date_add(subdate(curdate(),date_format(curdate(),'%w')-1),interval"
        " + 1 week) from ticket_ticket) tmp1 where @cdate > '{}') t1 LEFT JOIN(select DATE_FORMAT(create_at,'%Y%u')"
        " date_str, count(id) as count from ticket_ticket GROUP BY date_str) t2 on YEARWEEK(t1.date_str,1) ="
        " t2.date_str where t1.date_str<='{}' order by t1.date_str;"
    ),
    "months": (
        "SELECT t1.date_str, COALESCE(t2.count, 0) as count FROM(SELECT @cdate:= date_add(@cdate,interval - 1 month) as"
        " date_str , 0 as count FROM (SELECT @cdate:=date_add(curdate()-day(curdate())+1,interval 1 month) from"
        " ticket_ticket) tmp1 where @cdate > '{}') t1 LEFT JOIN(select DATE_FORMAT(create_at,'%Y-%m') date_str,"
        " count(id) as count from ticket_ticket GROUP BY date_str) t2 on left(t1.date_str,7) = t2.date_str where"
        " t1.date_str<='{}' order by t1.date_str;"
    ),
    "years": "SELECT DATE_FORMAT(create_at,'%Y') years,count(id) count from ticket_ticket group by years;",
}

USER_SQL = {
    "days": (
        "SELECT t1.date_str, COALESCE(t2.count, 0) as count FROM(SELECT @cdate:= date_add(@cdate,interval - 1 day) as"
        " date_str , 0 as count FROM (SELECT @cdate:=date_add(CURDATE(),interval + 1 day) from ticket_ticket limit 366)"
        " tmp1 where @cdate >= '{}') t1 LEFT JOIN(select DATE_FORMAT(date_joined,'%Y-%m-%d') date_str, count(id) as"
        " count from account_user GROUP BY date_str) t2 on t1.date_str = t2.date_str where t1.date_str<='{}' order by"
        " t1.date_str; "
    ),
    "weeks": (
        "SELECT t1.date_str, COALESCE(t2.count, 0) as count FROM(SELECT @cdate:= date_add(@cdate,interval - 1 week) as"
        " date_str , 0 as count FROM (SELECT @cdate:=date_add(subdate(curdate(),date_format(curdate(),'%w')-1),interval"
        " + 1 week) from ticket_ticket) tmp1 where @cdate > '{}') t1 LEFT JOIN(select DATE_FORMAT(date_joined,'%Y%u')"
        " date_str, count(id) as count from account_user GROUP BY date_str) t2 on YEARWEEK(t1.date_str,1) = t2.date_str"
        " where t1.date_str<='{}' order by t1.date_str;"
    ),
    "months": (
        "SELECT t1.date_str, COALESCE(t2.count, 0) as count FROM(SELECT @cdate:= date_add(@cdate,interval - 1 month) as"
        " date_str , 0 as count FROM (SELECT @cdate:=date_add(curdate()-day(curdate())+1,interval 1 month) from"
        " ticket_ticket) tmp1 where @cdate > '{}') t1 LEFT JOIN(select DATE_FORMAT(date_joined,'%Y-%m') date_str,"
        " count(id) as count from account_user GROUP BY date_str) t2 on left(t1.date_str,7) = t2.date_str where"
        " t1.date_str<='{}' order by t1.date_str;"
    ),
    "years": "SELECT DATE_FORMAT(date_joined,'%Y') years,count(id) count from account_user group by years;",
}

SERVICE_SQL = {
    "days": (
        "SELECT t1.date_str, COALESCE(t2.count, 0) as count FROM(SELECT @cdate:= date_add(@cdate,interval - 1 day) as"
        " date_str , 0 as count FROM (SELECT @cdate:=date_add(CURDATE(),interval + 1 day) from ticket_ticket limit 366)"
        " tmp1 where @cdate >= '{}') t1 LEFT JOIN(select DATE_FORMAT(create_at,'%Y-%m-%d') date_str, count(id) as count"
        " from service_service GROUP BY date_str) t2 on t1.date_str = t2.date_str where t1.date_str<='{}' order by"
        " t1.date_str; "
    ),
    "weeks": (
        "SELECT t1.date_str, COALESCE(t2.count, 0) as count FROM(SELECT @cdate:= date_add(@cdate,interval - 1 week) as"
        " date_str , 0 as count FROM (SELECT @cdate:=date_add(subdate(curdate(),date_format(curdate(),'%w')-1),interval"
        " + 1 week) from ticket_ticket) tmp1 where @cdate > '{}') t1 LEFT JOIN(select DATE_FORMAT(create_at,'%Y%u')"
        " date_str, count(id) as count from service_service GROUP BY date_str) t2 on YEARWEEK(t1.date_str,1) ="
        " t2.date_str where t1.date_str<='{}' order by t1.date_str;"
    ),
    "months": (
        "SELECT t1.date_str, COALESCE(t2.count, 0) as count FROM(SELECT @cdate:= date_add(@cdate,interval - 1 month) as"
        " date_str , 0 as count FROM (SELECT @cdate:=date_add(curdate()-day(curdate())+1,interval 1 month) from"
        " ticket_ticket) tmp1 where @cdate > '{}') t1 LEFT JOIN(select DATE_FORMAT(create_at,'%Y-%m') date_str,"
        " count(id) as count from service_service GROUP BY date_str) t2 on left(t1.date_str,7) = t2.date_str where"
        " t1.date_str<='{}' order by t1.date_str;"
    ),
    "years": "SELECT DATE_FORMAT(create_at,'%Y') years,count(id) count from service_service group by years;",
}


SERVICE_TICKET_COUNT_SQL = {
    "days": (
        "SELECT t1.date_str, COALESCE(t2.count, 0) as count FROM(SELECT @cdate:= date_add(@cdate,interval - 1 day) as"
        " date_str , 0 as count FROM (SELECT @cdate:=date_add(CURDATE(),interval + 1 day) from ticket_ticket limit 366)"
        " tmp1 where @cdate >= '{}') t1 LEFT JOIN(select DATE_FORMAT(create_at,'%Y-%m-%d') date_str, count(id) as count"
        " from ticket_ticket where service_id={} GROUP BY date_str) t2 on t1.date_str = t2.date_str where"
        " t1.date_str<='{}' order by t1.date_str; "
    ),
    "weeks": (
        "SELECT t1.date_str, COALESCE(t2.count, 0) as count FROM(SELECT @cdate:= date_add(@cdate,interval - 1 week) as"
        " date_str , 0 as count FROM (SELECT @cdate:=date_add(subdate(curdate(),date_format(curdate(),'%w')-1),interval"
        " + 1 week) from ticket_ticket) tmp1 where @cdate > '{}') t1 LEFT JOIN(select DATE_FORMAT(create_at,'%Y%u')"
        " date_str, count(id) as count from ticket_ticket where service_id={} GROUP BY date_str) t2 on"
        " YEARWEEK(t1.date_str,1) = t2.date_str where t1.date_str<='{}' order by t1.date_str;"
    ),
    "months": (
        "SELECT t1.date_str, COALESCE(t2.count, 0) as count FROM(SELECT @cdate:= date_add(@cdate,interval - 1 month) as"
        " date_str , 0 as count FROM (SELECT @cdate:=date_add(curdate()-day(curdate())+1,interval 1 month) from"
        " ticket_ticket) tmp1 where @cdate > '{}') t1 LEFT JOIN(select DATE_FORMAT(create_at,'%Y-%m') date_str,"
        " count(id) as count from ticket_ticket where service_id={} GROUP BY date_str) t2 on left(t1.date_str,7) ="
        " t2.date_str where t1.date_str<='{}' order by t1.date_str;"
    ),
    "years": (
        "SELECT DATE_FORMAT(create_at,'%Y') years,count(id) count from ticket_ticket where create_at>'{}' and"
        " service_id={} and create_at<'{}' group by years;"
    ),
}

SERVICE_BIZ_COUNT_SQL = {
    "days": (
        "SELECT t1.date_str, COALESCE(t2.count, 0) as count FROM(SELECT @cdate:= date_add(@cdate,interval - 1 day) as"
        " date_str , 0 as count FROM (SELECT @cdate:=date_add(CURDATE(),interval + 1 day) from ticket_ticket limit 366)"
        " tmp1 where @cdate >= '{}') t1 LEFT JOIN(select DATE_FORMAT(create_at,'%Y-%m-%d') date_str, count(distinct"
        " bk_biz_id) as count from ticket_ticket where service_id={} and bk_biz_id>-1 GROUP BY date_str) t2 on"
        " t1.date_str = t2.date_str where t1.date_str<='{}' order by t1.date_str; "
    ),
    "weeks": (
        "SELECT t1.date_str, COALESCE(t2.count, 0) as count FROM(SELECT @cdate:= date_add(@cdate,interval - 1 week) as"
        " date_str , 0 as count FROM (SELECT @cdate:=date_add(subdate(curdate(),date_format(curdate(),'%w')-1),interval"
        " + 1 week) from ticket_ticket) tmp1 where @cdate > '{}') t1 LEFT JOIN(select DATE_FORMAT(create_at,'%Y%u')"
        " date_str, count(distinct bk_biz_id) as count from ticket_ticket where service_id={} and bk_biz_id>-1 GROUP BY"
        " date_str) t2 on YEARWEEK(t1.date_str,1) = t2.date_str where t1.date_str<='{}' order by t1.date_str;"
    ),
    "months": (
        "SELECT t1.date_str, COALESCE(t2.count, 0) as count FROM(SELECT @cdate:= date_add(@cdate,interval - 1 month) as"
        " date_str , 0 as count FROM (SELECT @cdate:=date_add(curdate()-day(curdate())+1,interval 1 month) from"
        " ticket_ticket) tmp1 where @cdate > '{}') t1 LEFT JOIN(select DATE_FORMAT(create_at,'%Y-%m') date_str,"
        " count(distinct bk_biz_id) as count from ticket_ticket where service_id={} and bk_biz_id>-1 GROUP BY date_str)"
        " t2 on left(t1.date_str,7) = t2.date_str where t1.date_str<='{}' order by t1.date_str;"
    ),
    "years": (
        "SELECT DATE_FORMAT(create_at,'%Y') years,count(distinct bk_biz_id) count from ticket_ticket where"
        " create_at>'{}' and service_id={} and create_at<'{}' and bk_biz_id>-1 group by years;"
    ),
}
