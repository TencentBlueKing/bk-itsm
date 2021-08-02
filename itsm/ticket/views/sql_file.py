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


solve_sql = """select date_format(create_at, '%%Y-%%m') as date,
                          sum(timestampdiff(SECOND, create_at, end_at)) as total,
                          count(*) as count,
                          sum(timestampdiff(SECOND, create_at, end_at))/count(*) as ratio
                       from ticket_ticket
                       where create_at>=%s
                          and create_at<%s
                          and current_status='FINISHED'
                          and is_deleted=0
                          and is_draft=0 group by date;"""

service_solve_sql = """select date_format(create_at, '%%Y-%%m') as date,
                          sum(timestampdiff(SECOND, create_at, end_at)) as total,
                          count(*) as count,
                          sum(timestampdiff(SECOND, create_at, end_at))/count(*) as ratio
                       from ticket_ticket
                       where create_at>=%s
                          and create_at<%s
                          and current_status='FINISHED'
                          and is_deleted=0
                          and is_draft=0
                          and service_type=%s group by date;"""

response_sql = """
                            SELECT
                                date_format(`ticket_ticket`.`create_at`, '%%Y-%%m') as date,
                                sum(log.deal_time) as total,
                                count(*) as count,
                                sum(log.deal_time)/count(*) as ratio
                            FROM `ticket_ticket`
                              INNER JOIN (
                                select `ticket_ticketeventlog`.`ticket_id`,`ticket_ticketeventlog`.`type`, `ticket_ticketeventlog`.`deal_time`
                                from `ticket_ticketeventlog`) log
                                ON ( `ticket_ticket`.`id` = `log`.`ticket_id` )
                            WHERE (`ticket_ticket`.`is_deleted` = False
                                     AND `ticket_ticket`.`is_draft` = False
                                     AND `ticket_ticket`.`current_status` = 'FINISHED'
                                     AND `log`.`type` = 'CLAIM'
                                     AND `ticket_ticket`.`create_at`>=%s
                                     AND `ticket_ticket`.`create_at`<%s)
                            GROUP BY date
                            ORDER BY date DESC;
                            """

service_response_sql = """
                            SELECT
                                date_format(`ticket_ticket`.`create_at`, '%%Y-%%m') as date,
                                sum(log.deal_time) as total,
                                count(*) as count,
                                sum(log.deal_time)/count(*) as ratio
                            FROM `ticket_ticket`
                              INNER JOIN (
                                select `ticket_ticketeventlog`.`ticket_id`,`ticket_ticketeventlog`.`type`, `ticket_ticketeventlog`.`deal_time`
                                from `ticket_ticketeventlog`) log
                                ON ( `ticket_ticket`.`id` = `log`.`ticket_id` )
                            WHERE (`ticket_ticket`.`is_deleted` = False
                                     AND `ticket_ticket`.`is_draft` = False
                                     AND `ticket_ticket`.`current_status` = 'FINISHED'
                                     AND `log`.`type` = 'CLAIM'
                                     AND `ticket_ticket`.`create_at`>=%s
                                     AND `ticket_ticket`.`create_at`<%s
                                     AND service_type=%s)
                            GROUP BY date
                            ORDER BY date DESC;
                            """

ticket_score_sql = """
SELECT
    date_format(`ticket_ticket`.`create_at`, '%%Y-%%m') as date,
    sum(`comment`.`stars`) as stars_sum,
    count(*) as count,
    sum(`comment`.`stars`)/count(*) as ratio
FROM `ticket_ticket`
  INNER JOIN (
    select `ticket_ticketcomment`.`ticket_id`,`ticket_ticketcomment`.`stars`
    from `ticket_ticketcomment`) comment
    ON ( `ticket_ticket`.`id` = `comment`.`ticket_id` )
WHERE (`ticket_ticket`.`is_deleted` = False
         AND `ticket_ticket`.`is_draft` = False
         AND `comment`.`stars` > 0
         AND `ticket_ticket`.`create_at` >= %s
         AND `ticket_ticket`.`create_at` < %s
  )
GROUP BY date
ORDER BY date DESC;"""

service_ticket_score_sql = """
SELECT
    date_format(`ticket_ticket`.`create_at`, '%%Y-%%m') as date,
    sum(`comment`.`stars`) as stars_sum,
    count(*) as count,
    sum(`comment`.`stars`)/count(*) as ratio
FROM `ticket_ticket`
  INNER JOIN (
    select `ticket_ticketcomment`.`ticket_id`,`ticket_ticketcomment`.`stars`
    from `ticket_ticketcomment`) comment
    ON ( `ticket_ticket`.`id` = `comment`.`ticket_id` )
WHERE (`ticket_ticket`.`is_deleted` = False
         AND `ticket_ticket`.`is_draft` = False
         AND `comment`.`stars` > 0
         AND `ticket_ticket`.`create_at` >= %s
         AND `ticket_ticket`.`create_at` < %s
         AND service_type=%s
  )
GROUP BY date
ORDER BY date DESC;"""

get_my_deal_time_sql = """
SELECT `ticket_ticket`.service_type AS service,
       sum(`ticket_ticketeventlog`.`deal_time`) AS deal_time
FROM `ticket_ticketeventlog`
  INNER JOIN (SELECT `id`, `service_type`, `is_draft` FROM `ticket_ticket`) ticket_ticket
    ON ( `ticket_ticketeventlog`.`ticket_id` = `ticket_ticket`.`id` )
WHERE (`ticket_ticketeventlog`.`operator` = %s
         AND `ticket_ticketeventlog`.`operate_at` >= %s
         AND `ticket_ticket`.`is_draft` = False)
GROUP BY `ticket_ticket`.service_type;
"""

get_my_deal_tickets_sql = """
SELECT  `ticket_ticket`.`service_type` AS service, count(*) as count
    FROM `ticket_ticket`
    WHERE `ticket_ticket`.`id` in (SELECT DISTINCT `ticket_ticketeventlog`.`ticket_id`
    FROM `ticket_ticketeventlog`
    WHERE ( `ticket_ticketeventlog`.`is_valid` = 1
            AND `ticket_ticketeventlog`.`operator` = %s
            AND `ticket_ticketeventlog`.`operate_at` >= %s)) AND `ticket_ticket`.`is_deleted`=0 and `ticket_ticket`.`is_draft`=0
    GROUP BY `ticket_ticket`.`service_type`;
"""
