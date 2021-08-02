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

from django.db.models import F
from django.forms import model_to_dict

from itsm.component.constants import DEFAULT_STRING
from itsm.component.utils.basic import create_version_number
from itsm.helper.utils import time_this_function
from itsm.service.models import CatalogService, DictData, OldSla, Service, ServiceCatalog, SysDict
from itsm.ticket.models import Ticket
from itsm.workflow.models import Workflow, WorkflowSnap, WorkflowVersion


@time_this_function
def get_or_create_version_from_workflow():
    """抛弃旧的流程版本，合并流程快照到最后一个流程版本"""

    total = Workflow._objects.all().count()
    print('get_or_create_version_from_workflow, total workflow: %s' % total)

    ver_for_snaps = {}
    count = 0
    # 创建流程最新版本，并聚合快照（被删除的流程相关的工单也需要迁移）
    for workflow in Workflow._objects.all():
        # workflow对应的快照
        snaps = set(
            WorkflowSnap.objects.filter(workflow_id=workflow.pk).values_list('id', flat=True))
        count += 1
        # 跳过已有版本的迁移（避免重复迁移）
        try:
            version = WorkflowVersion._objects.get(workflow_id=workflow.id)
            print(
                'skip exist workflow version: {}({})'.format(version.name, version.version_number))
        except WorkflowVersion.DoesNotExist:
            version = workflow.create_version("system")
            print('create workflow version: {}({})'.format(version.name, version.version_number))

        ver_for_snaps[version.pk] = snaps
        print('update workflow: {}, cnt={}, workflow_number={}'.format(workflow.name, len(snaps),
                                                                       count))

    return ver_for_snaps


@time_this_function
def update_ticket_service_type():
    Ticket._objects.filter(service_type=DEFAULT_STRING).update(service_type=F('service'))


@time_this_function
def update_ticket_catalog_and_service(*args, **kwargs):
    """
    根据服务及目录特性更新ticket
    """

    print('Ticket.update_ticket_catalog_and_service')

    ver_to_snaps = get_or_create_version_from_workflow()
    # print 'ver_for_snaps: %s' % ver_for_snaps

    ver_to_catalog_service = get_or_create_service_and_catalog_from_version()
    # print 'ver_for_service: %s' % ver_for_catalog_service

    # 外键到ticket
    for ver_pk, snaps in ver_to_snaps.items():
        service_catalog = ver_to_catalog_service.get(ver_pk)
        if not service_catalog:
            ver = WorkflowVersion._objects.get(id=ver_pk)
            print('skip empty service_catalog: %s, public: %s' % (
            ver_pk, ver.extras.get('service_property')))
            continue

        Ticket._objects.filter(workflow_snap_id__in=snaps).update(
            catalog_id=service_catalog.catalog.id, service_id=service_catalog.service.id,
        )

        print('update ticket workflow: {}, cnt={}'.format(ver_pk, len(snaps)))


@time_this_function
def get_or_create_service_and_catalog_from_version(*args, **kwargs):
    """创建服务条目并绑定到服务目录
    排除草稿流程，仅创建有效流程的服务项
    """

    ver_for_service = {}

    print('Service.get_or_create_service_and_catalog_from_version')
    for ver in WorkflowVersion._objects.all():

        # 排除草稿流程
        if ver.is_draft:
            print('skip draft workflow version: %s(%s)' % (ver.name, ver.flow_type))
            continue

        print('create service item for version: %s(%s)' % (ver.name, ver.flow_type))
        obj, created = Service.objects.get_or_create(
            defaults={
                'key': ver.flow_type,
                'sla': OldSla.objects.get(name='三级', level=1),
                'desc': ver.desc,
                'is_deleted': ver.is_deleted,
            },
            **{'name': ver.name, 'workflow': ver}
        )

        # 关联目录
        try:
            catalog = ServiceCatalog._objects.get(
                key=ver.extras['service_property'].get('public', {}).get('service_category')
            )

            catalog_service, created = CatalogService.objects.get_or_create(service=obj,
                                                                            catalog=catalog)

            ver_for_service[ver.pk] = catalog_service

            print('create service({}) and bind catalog({})'.format(obj.id, catalog.id))
        except ServiceCatalog.DoesNotExist:
            print('catalog not found: {} - {}'.format(ver.id, ver.name))

    return ver_for_service


@time_this_function
def update_ticket_flow_id():
    """测试专用"""
    start = datetime.datetime.now()
    print("update_ticket_flow_id start: %s" % start)
    bad_ticket_cnt = 0

    same_snaps, diff_snaps = compare_case_snaps_with_last_case_workflow()
    count = Ticket._objects.filter(workflow_snap_id__in=same_snaps).update(
        flow_id=WorkflowVersion.objects.get(workflow_id=57).id
    )
    print("update last ver case count=%s" % count)

    for ticket in Ticket._objects.all().exclude(workflow_snap_id__in=same_snaps):
        try:
            workflow_snap = WorkflowSnap.objects.get(id=ticket.workflow_snap_id)
            workflow = Workflow._objects.get(id=workflow_snap.workflow_id)
            version = create_version_by_ticket_workflowsnap(workflow, workflow_snap)
            ticket.flow_id = version.id
            ticket.save()
            print('update flow_id for: %s' % ticket.sn)
        except (WorkflowSnap.DoesNotExist, Workflow.DoesNotExist):
            print('%s: bad flow_id ticket' % ticket.sn)
    end = datetime.datetime.now()
    print('bad_ticket_cnt = %s, end=%s, use=%s' % (bad_ticket_cnt, end, end - start))


def create_version_by_ticket_workflowsnap(workflow, workflow_snap):
    """根据单据的流程快照创建流程版本，默认删除"""
    data = model_to_dict(workflow)
    # remove and update some fields
    for field in [
        'id',
        'creator',
        'create_at',
        'end_at',
        'update_at',
        'notify',
        'updated_by',
        'service',
        'service_property',
        'is_biz_needed',
        'is_supervise_needed',
        'supervise_type',
        'supervisor',
        '_state',
    ]:
        data.pop(field, None)
    data.update(
        master=workflow_snap.master,
        creator="system",
        updated_by="system",
        workflow_id=workflow_snap.id,
        version_number=create_version_number(),
        version_message="version created.",
        states=workflow_snap.states,
        transitions=workflow_snap.transitions,
        fields=workflow_snap.fields,
        notify=list(workflow.notify.values_list('id', flat=True)),
        is_deleted=True,
        extras={
            # 关联服务
            'service': workflow.service,
            # 服务目录
            'service_property': workflow.service_property,
            # 关联业务
            'biz_related': workflow.is_biz_needed,
            # 督办相关
            'need_urge': workflow.is_supervise_needed,
            'urgers_type': workflow.supervise_type,
            'urgers': workflow.supervisor,
        },
    )
    notify = data.pop('notify', [])
    version = WorkflowVersion.objects.create(**data)
    version.notify = notify
    version.save()
    return version


@time_this_function
def compare_case_snaps_with_last_case_workflow(case_workflow=None):
    """测试用"""
    if case_workflow is None:
        case_workflow = Workflow.objects.get(id=57)

    case_field_ids = [str(id) for id in case_workflow.fields.values_list("id", flat=True)]
    case_states_ids = [str(id) for id in case_workflow.states.values_list("id", flat=True)]
    case_transitions_ids = [str(id) for id in
                            case_workflow.transitions.values_list("id", flat=True)]

    same_snaps, diff_snaps = [], []
    for snap in WorkflowSnap.objects.filter(workflow_id=case_workflow.id):
        if set(snap.fields.keys()).difference(case_field_ids):
            diff_snaps.append(snap.id)
        elif set(snap.states.keys()).difference(case_states_ids):
            diff_snaps.append(snap.id)
        elif set(snap.transitions.keys()).difference(case_transitions_ids):
            diff_snaps.append(snap.id)
        else:
            same_snaps.append(snap.id)
    return same_snaps, diff_snaps


def update_event_type_datadict():
    dict_table = SysDict.objects.get(key='EVENT_TYPE')
    DictData.objects.filter(dict_table=dict_table).delete()
    data_list = [
        {'key': '567e174c9c1136bc2c9550f8d843a4be', 'name': '基础设施故障'},
        {'key': '03745bf6aca591d212bd5811f8ca8252', 'name': '安全事件'},
        {'key': '74a33c956c10a9d871338baf60ce0328', 'name': '云平台故障'},
        {'key': '61334f4e572575bede2a54292cc26574', 'name': '应用系统故障'},
    ]
    data_keys = [data['key'] for data in data_list]

    for dictdata in DictData._objects.filter(key__in=data_keys):
        dictdata.hard_delete()

    for data in data_list:
        new_item, _ = DictData.objects.get_or_create(
            defaults={
                'creator': 'system',
                'updated_by': 'system',
                'name': data['name'],
                'is_deleted': False,
                'is_readonly': True,
            },
            **{'key': data['key'], 'dict_table': dict_table, }
        )
