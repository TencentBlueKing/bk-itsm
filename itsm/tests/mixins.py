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

import json
import logging
import os
import time

from django.conf import settings
from django.test import SimpleTestCase

from itsm.service.models import Service, ServiceCatalog
from itsm.ticket.models import Status, Ticket
from itsm.workflow.models import Workflow

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('itsm-test')


def log_message(msg):
    return '############ %s' % msg


class ItsmTestCase(SimpleTestCase):
    common_fields = [
        {"key": "impact", "value": "1"},
        {"key": "priority", "value": "2"},
        {"key": "urgency", "value": "3"},
    ]

    allow_database_queries = True

    @classmethod
    def import_flow_to_service(cls, name):
        logger.info(log_message('import_flow_to_service'))
        with open(os.path.join(settings.BASE_DIR, 'itsm', 'tests', 'data', name), 'r') as f:
            data = json.loads(f.read())[0]
            workflow = Workflow.restore_tag(data, 'test')
            ver = workflow.create_version("system")

            test_root = ServiceCatalog.create_catalog(
                key='test_catalog',
                name='test_catalog',
                # is_deleted=True,
                parent_key='root',
            )

            service, created = Service.objects.get_or_create(
                defaults={'name': ver.name, 'workflow': ver},
                **{'key': 'question', 'is_deleted': ver.is_deleted, }
            )

            if not created:
                service.workflow = ver
                service.save()

            service.bind_catalog(test_root.id)

        return service

    def create_ticket(self, service, creator, fields):
        response = self.client.post(
            '/openapi/ticket/create_ticket/',
            data=json.dumps({"service_id": service.id, "creator": creator,
                             "fields": self.common_fields + fields}),
            content_type='application/json',
        )

        return response

    def get_ticket_status(self, sn):
        return self.client.get('/openapi/ticket/get_ticket_status/', data={'sn': sn}, ).json()

    def get_ticket_info(self, sn):
        return self.client.get('/openapi/ticket/get_ticket_info/', data={'sn': sn}, ).json()

    def operate_ticket(self, sn, operator, action_type, action_message=''):
        """
        :param sn: 单号
        :param operator: 操作人 
        :param action_type: SUSPEND|UNSUSPEND
        :param action_message: 操作备注
        """
        data = {
            "sn": sn,
            "operator": operator,
            "action_type": action_type,
            "action_message": action_message,
        }

        response = self.client.post(
            '/openapi/ticket/operate_ticket/', data=json.dumps(data),
            content_type='application/json'
        )

        return self.assert_response(response, True, 0)

    def submit_node(self, sn, operator, state_id, fields):
        response = self.operate_node(sn, operator, 'TRANSITION', state_id, fields)
        return self.assert_response(response, True, 0)

    def deliver_node(self, sn, operator, state_id, action_message, processors_type, processors):
        response = self.operate_node(
            sn,
            operator,
            'DELIVER',
            state_id,
            action_message=action_message,
            processors_type=processors_type,
            processors=processors,
        )
        return self.assert_response(response, True, 0)

    def assign_node(self, sn, operator, state_id, action_message, processors_type, processors):
        response = self.operate_node(
            sn,
            operator,
            'DISTRIBUTE',
            state_id,
            action_message=action_message,
            processors_type=processors_type,
            processors=processors,
        )
        return self.assert_response(response, True, 0)

    def claim_node(self, sn, operator, state_id):
        response = self.operate_node(sn, operator, 'CLAIM', state_id, processors_type='PERSON',
                                     processors=operator)

        return self.assert_response(response, True, 0)

    def terminate_node(self, sn, operator, state_id, action_message):
        response = self.operate_node(sn, operator, 'TERMINATE', state_id,
                                     action_message=action_message, )

        return self.assert_response(response, True, 0)

    def operate_node(
        self,
        sn,
        operator,
        action_type,
        state_id,
        fields=None,
        action_message=None,
        processors_type=None,
        processors=None,
    ):
        """
        :param sn: 单号
        :param operator: 操作人 
        :param action_type: 
                TRANSITION + fields
                CLAIM|ASSIGN|DELIVER|TERMINATE
        :param action_message: 操作备注
        :param state_id: 节点ID
        :param fields: 字段
        :param processors_type: 负责人类型
        :param processors: 负责人
        """
        data = {
            "sn": sn,
            "operator": operator,
            "action_type": action_type,
            "state_id": state_id,
        }

        if fields:
            data.update(fields=fields)

        if action_message:
            data.update(action_message=action_message)

        if processors_type:
            data.update(processors_type=processors_type)

        if processors:
            data.update(processors=processors)

        response = self.client.post(
            '/openapi/ticket/operate_node/', data=json.dumps(data), content_type='application/json'
        )

        return response

    def get_ticket_node(self, ticket, state_id):
        return ticket.status(state_id)

    @classmethod
    def wait(cls, sec):
        logger.info(log_message('wait for %s second...' % sec))
        time.sleep(sec)

    def wait_for_nodes(self, ticket, nodes, wait_status=Status.RUNNING_STATUS):
        retries = 0
        state_meet = set()

        while retries < 30:
            logger.info(log_message('wait {} nodes to {}'.format(len(nodes), wait_status)))
            for state_id in nodes:
                state = ticket.status(state_id)
                if state and state.status in wait_status:
                    state_meet.add(state_id)

            self.wait(1)
            retries = retries + 1

            if len(state_meet) == len(nodes):
                break
        else:
            assert False, 'wait_for_nodes timeout error'

    def wait_for_next_steps(self, sn, passed_steps, num_of_steps=1):
        retries = 0

        while retries < 30:
            res = self.get_ticket_status(sn)
            current_steps = [step for step in res['data']['current_steps'] if
                             step['state_id'] not in passed_steps]
            self.wait(1)
            retries = retries + 1

            if len(current_steps) == num_of_steps:
                return current_steps
        else:
            assert False, 'wait_for_next_steps timeout error'

    def wait_ticket_finished(self, sn):
        retries = 0
        while retries < 30:
            logger.info(log_message('wait_ticket_finished'))
            res = self.get_ticket_status(sn)
            if res['data']['current_status'] in Status.STOPPED_STATUS:
                break

            time.sleep(1)
            retries = retries + 1
        else:
            assert False, 'wait_ticket_finished timeout error'

    def assert_response(self, response, result, code):
        self.assertEqual(response.status_code, 200)

        response_json = response.json()
        self.assertEqual(response_json['result'], result, response_json['message'])
        self.assertEqual(response_json['code'], code, response_json['message'])

        return response_json

    def assert_ticket_is_deleted(self, ticket):
        with self.assertRaises(Ticket.DoesNotExist):
            ticket.refresh_from_db()

    def assert_ticket_status(self, ticket, status):
        ticket.refresh_from_db()
        self.assertEqual(ticket.current_status, status)

    def assert_ticket_nodes(self, ticket, nodes, wait_status=Status.RUNNING_STATUS):
        logger.info(log_message('assert {} node to {}'.format(len(nodes), wait_status)))

        for node_status in ticket.node_status.filter(state_id__in=nodes):
            self.assertTrue(node_status.status in wait_status)

    def assert_current_processors(self, ticket, state_id, processors_type, processors):
        node = self.get_ticket_node(ticket, state_id)
        self.assertEqual(node.processors_type, processors_type)
        self.assertEqual(node.processors, processors)

    @classmethod
    def pass_test(cls, desc=''):
        logger.info('\n')
        logger.info(f'#################### {cls.__name__} pass a test: {desc} ####################')
        logger.info('\n')
