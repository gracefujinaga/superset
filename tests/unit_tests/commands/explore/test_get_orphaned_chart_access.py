# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from unittest.mock import MagicMock

import pytest
from flask import current_app
from pytest_mock import MockerFixture

from superset.commands.explore.get import GetExploreCommand
from superset.commands.explore.parameters import CommandParameters
from superset.daos.exceptions import DatasourceNotFound
from superset.exceptions import SupersetSecurityException


def _run_with_orphaned_chart(mocker: MockerFixture) -> None:
    """Run ``GetExploreCommand`` for a chart whose dataset no longer exists."""
    slc = MagicMock()
    slc.data = {"slice_id": 1}
    slc.editors = []
    slc.dashboards = []
    slc.created_by = None
    slc.changed_by = None
    mocker.patch(
        "superset.commands.explore.get.get_form_data",
        return_value=({"datasource": "999__table", "viz_type": "table"}, slc),
    )
    mocker.patch(
        "superset.commands.explore.get.get_datasource_info",
        return_value=(999, "table"),
    )
    mocker.patch(
        "superset.commands.explore.get.DatasourceDAO.get_datasource",
        side_effect=DatasourceNotFound(),
    )
    mocker.patch(
        "superset.commands.explore.get.DatasetDAO.get_rls_filters_for_dataset",
        return_value=[],
    )
    params = CommandParameters(
        permalink_key=None,
        form_data_key=None,
        datasource_id=None,
        datasource_type=None,
        slice_id=1,
    )
    with current_app.test_request_context():
        GetExploreCommand(params).run()


def test_orphaned_chart_requires_chart_access(
    app_context: None, mocker: MockerFixture
) -> None:
    """The chart-level check must run even when the dataset does not resolve."""
    mock_sm = mocker.patch(
        "superset.commands.explore.get.security_manager", new_callable=MagicMock
    )
    mock_sm.raise_for_access.side_effect = SupersetSecurityException(MagicMock())

    with pytest.raises(SupersetSecurityException):
        _run_with_orphaned_chart(mocker)

    mock_sm.raise_for_access.assert_called_once()
    assert mock_sm.raise_for_access.call_args.kwargs["chart"] is not None


def test_orphaned_chart_served_when_authorized(
    app_context: None, mocker: MockerFixture
) -> None:
    mock_sm = mocker.patch(
        "superset.commands.explore.get.security_manager", new_callable=MagicMock
    )
    mock_sm.can_access.return_value = True

    _run_with_orphaned_chart(mocker)

    mock_sm.raise_for_access.assert_called_once()
