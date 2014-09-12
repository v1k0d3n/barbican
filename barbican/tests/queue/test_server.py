# Copyright (c) 2013-2014 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import mock

from barbican import queue
from barbican.queue import server
from barbican.tests import utils


class WhenUsingBeginTypeOrderTask(utils.BaseTestCase):
    """Test using the Tasks class for 'type order' task."""

    def setUp(self):
        super(WhenUsingBeginTypeOrderTask, self).setUp()

        self.tasks = server.Tasks()

    @mock.patch('barbican.tasks.resources.BeginTypeOrder')
    def test_should_process_order(self, mock_begin_order):
        mock_begin_order.return_value.process.return_value = None
        self.tasks.process_type_order(context=None,
                                      order_id=self.order_id,
                                      keystone_id=self.keystone_id)
        mock_begin_order.return_value.process.assert_called_with(
            self.order_id, self.keystone_id)

    @mock.patch('barbican.tasks.resources.UpdateOrder')
    def test_should_update_order(self, mock_update_order):
        mock_update_order.return_value.process.return_value = None
        updated_meta = {}
        self.tasks.update_order(context=None,
                                order_id=self.order_id,
                                keystone_id=self.keystone_id,
                                updated_meta=updated_meta)
        mock_update_order.return_value.process.assert_called_with(
            self.order_id, self.keystone_id, updated_meta
        )

    @mock.patch('barbican.tasks.resources.BeginTypeOrder')
    def test_process_order_catch_exception(self, mock_begin_order):
        """Test process_type_order() handles all exceptions."""
        mock_begin_order.return_value.process.side_effect = Exception()
        self.tasks.process_type_order(None, self.order_id, self.keystone_id)


class WhenUsingTaskServer(utils.BaseTestCase):
    """Test using the asynchronous task client."""

    def setUp(self):
        super(WhenUsingTaskServer, self).setUp()

        self.target = 'a target value here'
        queue.get_target = mock.MagicMock(return_value=self.target)

        self.server_mock = mock.MagicMock()
        self.server_mock.start.return_value = None
        self.server_mock.stop.return_value = None

        queue.get_server = mock.MagicMock(return_value=self.server_mock)

        self.server = server.TaskServer()

    def test_should_start(self):
        self.server.start()
        queue.get_target.assert_called_with()
        queue.get_server.assert_called_with(target=self.target,
                                            endpoints=[self.server])
        self.server_mock.start.assert_called_with()

    def test_should_stop(self):
        self.server.stop()
        queue.get_target.assert_called_with()
        queue.get_server.assert_called_with(target=self.target,
                                            endpoints=[self.server])
        self.server_mock.stop.assert_called_with()
