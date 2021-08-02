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

from django.test import TestCase

from django_signal_valve import valve
from django_signal_valve.models import Signal
from django_signal_valve.tests import mock_signal


class TestValve(TestCase):
    def setUp(self):
        valve.unload_valve_function()

    def test_set_valve_function(self):
        self.assertRaises(Exception, valve.set_valve_function, args=[1])

        def func():
            return True

        valve.unload_valve_function()
        valve.set_valve_function(func)
        self.assertEqual(valve.valve_function(), func)
        self.assertRaises(Exception, valve.set_valve_function, args=[func])

        valve.__valve_function = None

    def test_send_on_valve_is_none(self):
        kwargs_1 = {'1': 1}
        kwargs_2 = {'2': 2}

        valve.unload_valve_function()
        valve.send(mock_signal, 'signal_1', **kwargs_1)
        valve.send(mock_signal, 'signal_1', **kwargs_2)
        self.assertEqual(mock_signal.signal_1.history[0], kwargs_1)
        self.assertEqual(mock_signal.signal_1.history[1], kwargs_2)

        mock_signal.clear()

    def test_send_on_valve_opened(self):
        kwargs_1 = {'1': 1}
        kwargs_2 = {'2': 2}

        def is_valve_closed():
            return False

        valve.unload_valve_function()
        valve.set_valve_function(is_valve_closed)
        valve.send(mock_signal, 'signal_1', **kwargs_1)
        valve.send(mock_signal, 'signal_1', **kwargs_2)
        self.assertEqual(mock_signal.signal_1.history[0], kwargs_1)
        self.assertEqual(mock_signal.signal_1.history[1], kwargs_2)

        mock_signal.clear()

    def test_send_on_closed(self):
        kwargs_1 = {'1': 1}
        kwargs_2 = {'2': 2}

        def is_valve_closed():
            return True

        valve.unload_valve_function()
        valve.set_valve_function(is_valve_closed)
        valve.send(mock_signal, 'signal_1', **kwargs_1)
        valve.send(mock_signal, 'signal_1', **kwargs_2)
        self.assertEqual(len(mock_signal.signal_1.history), 0)

        mock_signal.clear()
        Signal.objects.all().delete()

    def test_open_valve(self):
        kwargs_1 = {'1': 1}
        kwargs_2 = {'2': 2}

        def valve_closed():
            return True

        valve.unload_valve_function()
        valve.set_valve_function(valve_closed)
        valve.send(mock_signal, 'signal_1', **kwargs_1)
        valve.send(mock_signal, 'signal_1', **kwargs_2)
        self.assertEqual(len(mock_signal.signal_1.history), 0)
        valve.open_valve(mock_signal)
        self.assertEqual(mock_signal.signal_1.history[0], kwargs_1)
        self.assertEqual(mock_signal.signal_1.history[1], kwargs_2)

        mock_signal.clear()
