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

__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2012-2020 Tencent BlueKing. All Rights Reserved."

from django.test import TestCase

from itsm.component.constants import (
    COVERAGE_STATE,
    EMPTY,
    END_STATE,
    NORMAL_STATE,
    ROUTER_P_STATE,
    START_STATE,
)
from itsm.workflow.models import State, Transition, Workflow
from itsm.workflow.validators import TransitionValidator


class StateLabelUpdateTests(TestCase):
    """
    c: 表示汇聚网关
    p:表示并行网关
    n：表示普通网关，包含人工和自动
    """

    def _pre_setup(self):
        super(StateLabelUpdateTests, self)._pre_setup()
        self.workflow = Workflow.objects.create(name='test', flow_type="request")
        self.start_state = self.create_start_state()
        self.end_state = self.create_end_state()
        self.t_validator = TransitionValidator()

    def create_c_state(self, label=EMPTY):
        return self.create_state(COVERAGE_STATE, label=label)

    def create_p_state(self, label=EMPTY):
        return self.create_state(ROUTER_P_STATE, label=label)

    def create_start_state(self):
        return self.create_state(START_STATE, 'G')

    def create_end_state(self):
        return self.create_state(END_STATE, 'G')

    def create_state(self, s_type=NORMAL_STATE, label='EMPTY'):
        return State.objects.create(
            workflow_id=self.workflow.id, name="test", type=s_type, is_draft=False, is_builtin=True, label=label
        )

    def create_transition(self, from_state, to_state):
        return Transition.objects.create(from_state=from_state, to_state=to_state, workflow=self.workflow)

    def transition_validate(self, from_state, to_state):
        self.t_validator({"from_state": from_state, "to_state": to_state})

    def _update_state_label(self, from_state, to_state):
        State.objects.update_state_label(from_state, to_state)
        return State.objects.get(id=from_state.id), State.objects.get(id=to_state.id)

    def test_from_start_to_empty_n(self):
        to_state = self.create_state()

        try:
            self.t_validator({"from_state": self.start_state, "to_state": to_state})
        except BaseException:
            self.assertEqual(0, 1)

        t = self.create_transition(self.start_state, to_state)
        State.objects.update_state_label(t.from_state, t.to_state)
        to_state = State.objects.get(id=to_state.id)
        self.assertEqual(to_state.label, 'G')

    # test_from_c_to_n  从汇聚到普通节点
    # 所有情况如下

    def test_from_empty_c_to_g_n(self):
        """
        空的聚合网关与global的节点连接应该为空
        """
        from_state = self.create_c_state()
        to_state = self.create_state(label='G')
        try:
            self.transition_validate(from_state, to_state)
        except BaseException:
            self.assertEqual(0, 1)

        self._update_state_label(from_state, to_state)

        self.assertEqual(from_state.label, EMPTY)

    def test_from_c_to_empty_n(self):
        from_state = self.create_c_state(label='G|P|C')
        to_state = self.create_state()
        try:
            self.transition_validate(from_state, to_state)
        except BaseException:
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(to_state.label, 'G')

    def test_from_c_to_n_valid(self):
        from_state = self.create_c_state(label='G|P|N12|P|C')
        to_state = self.create_state(label='G|P|N12')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(from_state.label, 'G|P|N12|P|C')
        self.assertEqual(to_state.label, 'G|P|N12')

    def test_from_c_n_invalid(self):
        from_state = self.create_c_state(label='G|P|N12|P|C')
        to_state = self.create_state(label='G|P|N13')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)

    def test_from_c_to_child_n_invalid(self):
        from_state = self.create_c_state(label='G|P|C')
        to_state = self.create_state(label='G|P|N13')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)

    def test_from_empty_c_to_empty_n(self):
        from_state = self.create_c_state()
        to_state = self.create_state()
        try:
            self.transition_validate(from_state, to_state)
        except BaseException:
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(to_state.label, EMPTY)
        self.assertEqual(from_state.label, EMPTY)

    # test_from_p_to_n(self):
    # 从p 到 n 的测试

    def test_from_empty_p_to_g_n(self):
        """
        空的并行网关与global的节点连接校验不应该通过
        """
        from_state = self.create_p_state()
        to_state = self.create_state(label='G')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)

    def test_from_p_to_empty_n(self):
        from_state = self.create_p_state(label='G|P')
        to_state = self.create_state()
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(to_state.label, 'G|P|N%s' % to_state.id)

    def test_from_p_to_n_valid(self):
        from_state = self.create_p_state(label='G|P|N12|P')
        to_state = self.create_state(label='G|P|N12|P|N')
        to_state.label = 'G|P|N12|P|N%s' % to_state.id
        to_state.save()
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(from_state.label, 'G|P|N12|P')
        self.assertEqual(to_state.label, 'G|P|N12|P|N%s' % to_state.id)

    def test_from_p_n_invalid(self):
        from_state = self.create_p_state(label='G|P|N12|P')
        to_state = self.create_state(label='G|P|N13')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)

    def test_from_p_to_child_n_invalid(self):
        from_state = self.create_p_state(label='G|P')
        to_state = self.create_state(label='G|P|N13|P|N16')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)

    def test_from_empty_p_to_empty_n(self):
        from_state = self.create_p_state()
        to_state = self.create_state()
        try:
            self.transition_validate(from_state, to_state)
        except BaseException:
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(to_state.label, EMPTY)
        self.assertEqual(from_state.label, EMPTY)

    # test_from_n_to_n(self):
    # 从n到n的测试

    def test_from_empty_n_to_g_n(self):
        from_state = self.create_state()
        to_state = self.create_state(label='G')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            self.assertEqual(0, 1)

        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(from_state.label, to_state.label)

    def test_from_n_to_empty_n(self):
        from_state = self.create_state(label='G|P|N12')
        to_state = self.create_state()
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(to_state.label, 'G|P|N12')

    def test_from_n_to_n_valid(self):
        from_state = self.create_state(label='G|P|N12')
        to_state = self.create_state(label='G|P|N12')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(from_state.label, 'G|P|N12')
        self.assertEqual(to_state.label, 'G|P|N12')

    def test_from_n_n_invalid(self):
        from_state = self.create_state(label='G|P|N12')
        to_state = self.create_state(label='G|P|N13')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)

    def test_from_empty_n_to_empty_n(self):
        from_state = self.create_p_state()
        to_state = self.create_state()
        try:
            self.transition_validate(from_state, to_state)
        except BaseException:
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(to_state.label, EMPTY)
        self.assertEqual(from_state.label, EMPTY)

    # test_from_p_to_p(self):

    def test_from_empty_p_to_g_p(self):
        """
        空的并行网关与global的节点连接校验不应该通过
        """
        from_state = self.create_p_state()
        to_state = self.create_p_state(label='G|P')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)

    def test_from_p_to_empty_p(self):
        from_state = self.create_p_state(label='G|P')
        to_state = self.create_p_state()
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(to_state.label, 'G|P|P%s' % to_state.id)

    def test_from_p_to_p_valid(self):
        from_state = self.create_p_state(label='G|P|N12|P')
        to_state = self.create_p_state(label='G|P|N12|P|P')
        to_state.label = 'G|P|N12|P|P%s' % to_state.id
        to_state.save()
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(from_state.label, 'G|P|N12|P')
        self.assertEqual(to_state.label, 'G|P|N12|P|P%s' % to_state.id)

    def test_from_p_p_invalid(self):
        from_state = self.create_p_state(label='G|P|')
        to_state = self.create_p_state(label='G|P|N12|P|P|P')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)

    def test_from_p_to_child_p_invalid(self):
        from_state = self.create_p_state(label='G|P')
        to_state = self.create_p_state(label='G|P|N13|P')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)

    def test_from_empty_p_to_empty_p(self):
        from_state = self.create_p_state()
        to_state = self.create_p_state()
        try:
            self.transition_validate(from_state, to_state)
        except BaseException:
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(to_state.label, EMPTY)
        self.assertEqual(from_state.label, EMPTY)

    def test_from_c_to_p(self):
        pass

    def test_from_empty_c_to_g_p(self):
        """
        空的聚合网关与global的节点连接应该为空
        """
        from_state = self.create_c_state()
        to_state = self.create_p_state(label='G|P')
        try:
            self.transition_validate(from_state, to_state)
        except BaseException:
            self.assertEqual(0, 1)

        self._update_state_label(from_state, to_state)

        self.assertEqual(from_state.label, EMPTY)

    def test_from_c_to_empty_p(self):
        from_state = self.create_c_state(label='G|P|C')
        to_state = self.create_p_state()
        try:
            self.transition_validate(from_state, to_state)
        except BaseException:
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(to_state.label, 'G|P%s' % to_state.id)

    def test_from_c_to_p_valid(self):
        from_state = self.create_c_state(label='G|P|N12|P|C')
        to_state = self.create_p_state(label='G|P|N12|P12')

        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(from_state.label, 'G|P|N12|P|C')
        self.assertEqual(to_state.label, 'G|P|N12|P12')

    def test_from_c_p_invalid(self):
        from_state = self.create_c_state(label='G|P|N12|P|C')
        to_state = self.create_p_state(label='G|P|N13|P')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)

    def test_from_c_to_child_p_invalid(self):
        from_state = self.create_c_state(label='G|P|C')
        to_state = self.create_p_state(label='G|P|N13|P')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)

    def test_from_empty_c_to_empty_p(self):
        from_state = self.create_c_state()
        to_state = self.create_p_state()
        try:
            self.transition_validate(from_state, to_state)
        except BaseException:
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(to_state.label, EMPTY)
        self.assertEqual(from_state.label, EMPTY)

    def test_from_n_to_p(self):
        pass

    def test_from_empty_n_to_g_p(self):
        """
        空的聚合网关与global的节点连接应该为空
        """
        from_state = self.create_state()
        to_state = self.create_p_state(label='G|P')
        try:
            self.transition_validate(from_state, to_state)
        except BaseException:
            self.assertEqual(0, 1)

        self._update_state_label(from_state, to_state)

        self.assertEqual(from_state.label, 'G')

    def test_from_n_to_empty_p(self):
        from_state = self.create_state(label='G')
        to_state = self.create_p_state()
        try:
            self.transition_validate(from_state, to_state)
        except BaseException:
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(to_state.label, 'G|P%s' % to_state.id)

    def test_from_n_to_p_valid(self):
        from_state = self.create_state(label='G|P|N12')
        to_state = self.create_p_state(label='G|P|N12|P12')

        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(from_state.label, 'G|P|N12')
        self.assertEqual(to_state.label, 'G|P|N12|P12')

    def test_from_n_p_invalid(self):
        from_state = self.create_state(label='G|P|N12')
        to_state = self.create_p_state(label='G|P|N13|P')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)

    def test_from_empty_n_to_empty_p(self):
        from_state = self.create_state()
        to_state = self.create_p_state()
        try:
            self.transition_validate(from_state, to_state)
        except BaseException:
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(to_state.label, EMPTY)
        self.assertEqual(from_state.label, EMPTY)

    def test_from_p_to_c(self):
        pass

    def test_from_empty_p_to_g_c(self):
        """
        空的聚合网关与global的节点连接应该为空
        """
        to_state = self.create_c_state(label='G|P|C')
        from_state = self.create_p_state()
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)

    def test_from_p_to_empty_c(self):
        # 待确认, 实际上，并行网关不能直接连聚合网关
        to_state = self.create_c_state()
        from_state = self.create_p_state(label='G|P')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(to_state.label, 'G|P|C%s' % to_state.id)

    def test_from_p_to_c_valid(self):
        # 同上
        from_state = self.create_p_state(label='G|P|N12|P')
        to_state = self.create_c_state(label='G|P|N12|P|C')

        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(from_state.label, 'G|P|N12|P')
        self.assertEqual(to_state.label, 'G|P|N12|P|C')

    def test_from_p_c_invalid(self):
        from_state = self.create_c_state(label='G|P|N12|P|C')
        to_state = self.create_p_state(label='G|P|N13|P')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)

    def test_from_p_to_child_c_invalid(self):
        from_state = self.create_p_state(label='G|P|')
        to_state = self.create_p_state(label='G|P|N13|P|C')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)

    def test_from_empty_p_to_empty_c(self):
        from_state = self.create_p_state()
        to_state = self.create_c_state()
        try:
            self.transition_validate(from_state, to_state)
        except BaseException:
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(to_state.label, EMPTY)
        self.assertEqual(from_state.label, EMPTY)

    # test_from_c_to_c(self):
    # 两个聚合网关的连接

    def test_from_empty_c_to_g_c(self):
        """
        空的聚合网关与global的节点连接应该为空
        """
        from_state = self.create_c_state()
        to_state = self.create_c_state(label='G|P|C')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            self.assertEqual(0, 1)

        self._update_state_label(from_state, to_state)

        self.assertEqual(EMPTY, from_state.label)

    def test_from_c_to_empty_c_invalid(self):
        from_state = self.create_c_state(label='G|P|C')
        to_state = self.create_c_state()
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)

    def test_from_c_to_empty_c(self):
        from_state = self.create_c_state(label='G|P|N12|P|C')
        to_state = self.create_c_state()
        try:
            self.transition_validate(from_state, to_state)
        except BaseException:
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        print("to_state.label: ", to_state.label)
        self.assertEqual(to_state.label, 'G|P|C%s' % to_state.id)

    def test_from_c_to_c_valid(self):
        from_state = self.create_c_state(label='G|P|N12|P|C')
        to_state = self.create_c_state(label='G|P|C')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(from_state.label, 'G|P|N12|P|C')
        self.assertEqual(to_state.label, 'G|P|C')

    def test_from_c_c_invalid(self):
        # 交叉连接
        from_state = self.create_c_state(label='G|P|N13|P|C')
        to_state = self.create_c_state(label='G|P|N12|P|C')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)

    def test_from_c_to_child_c_invalid(self):
        from_state = self.create_c_state(label='G|P|C')
        to_state = self.create_c_state(label='G|P|N12|P|P|C')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)

    def test_from_empty_c_to_empty_c(self):
        from_state = self.create_c_state()
        to_state = self.create_c_state()
        try:
            self.transition_validate(from_state, to_state)
        except BaseException:
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(to_state.label, EMPTY)
        self.assertEqual(from_state.label, EMPTY)

    # test_from_n_to_c(self):
    # 普通网关到聚合网关的连接

    def test_from_empty_n_to_g_c(self):
        """
        空的聚合网关与global的节点连接应该为空
        """
        from_state = self.create_state()
        to_state = self.create_c_state(label='G|P|C')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            self.assertEqual(0, 1)

        self._update_state_label(from_state, to_state)

        self.assertEqual('G|P|N%s' % from_state.id, from_state.label)

    def test_from_n_to_empty_c_invalid(self):
        from_state = self.create_state(label='G')
        to_state = self.create_c_state()
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)

    def test_from_n_to_empty_c(self):
        from_state = self.create_state(label='G|P|N12')
        to_state = self.create_c_state()
        try:
            self.transition_validate(from_state, to_state)
        except BaseException:
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(to_state.label, 'G|P|C%s' % to_state.id)

    def test_from_n_to_c_valid(self):
        from_state = self.create_state(label='G|P|N12|P|N11')
        to_state = self.create_c_state(label='G|P|N12|P|C')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(from_state.label, 'G|P|N12|P|N11')
        self.assertEqual(to_state.label, 'G|P|N12|P|C')

    def test_from_branch_n_to_gc_valid(self):
        from_state = self.create_state(label='G|P|N12')
        to_state = self.create_c_state(label='G|P|C')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(from_state.label, 'G|P|N12')
        self.assertEqual(to_state.label, 'G|P|C')

    def test_from_n_c_invalid(self):
        # 交叉连接
        from_state = self.create_state(label='G|P|N13')
        to_state = self.create_c_state(label='G|P|N12|P|C')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)

    def test_from_n_to_child_c_invalid(self):
        from_state = self.create_state(label='G|P|N13')
        to_state = self.create_c_state(label='G|P|N13|P|C')
        try:
            self.transition_validate(from_state, to_state)
        except Exception as error:
            print(str(error))
            return
        self.assertEqual(0, 1)

    def test_from_empty_n_to_empty_c(self):
        from_state = self.create_state()
        to_state = self.create_c_state()
        try:
            self.transition_validate(from_state, to_state)
        except BaseException:
            self.assertEqual(0, 1)
        from_state, to_state = self._update_state_label(from_state, to_state)
        self.assertEqual(to_state.label, EMPTY)
        self.assertEqual(from_state.label, EMPTY)
