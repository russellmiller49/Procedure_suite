"""The workbench UI tests render against a committed profile; it must match the contract.

Regenerate after a contract or dictionary change:
    python -c "import json, app.registry_workbench; from app.registry_workbench import service; \
open('ui/source/registry_workbench/src/__fixtures__/profile.json','w').write(\
json.dumps(service.profile(), indent=1, sort_keys=True) + '\\n')"
"""

import json
from pathlib import Path

from app.registry_workbench import service

FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "ui/source/registry_workbench/src/__fixtures__/profile.json"
)


def test_ui_profile_fixture_matches_the_live_profile():
    assert json.loads(FIXTURE.read_text()) == json.loads(json.dumps(service.profile()))
