
from typing import Callable, List, Optional
import httpx

from .leaves.tools import create_tool_specs as _leaves
from .attendance.tools import create_tool_specs as _attendance
from .feedback.tools import create_tool_specs as _feedback
from .tickets.tools import create_tool_specs as _tickets
from .team_management.tools import create_tool_specs as _team
from .miscellaneous.tools import create_tool_specs as _misc

try:
    from .referrals.tools import create_tool_specs as _referrals
except Exception:
    _referrals = None

def all_tool_specs(base_url: str, auth_header_getter: Callable[[], str], http_client: Optional[httpx.Client] = None):
    specs = []
    for factory in (_leaves, _attendance, _feedback, _tickets, _team, _misc):
        specs.extend(factory(base_url, auth_header_getter, client=http_client))
    if _referrals:
        specs.extend(_referrals(base_url, auth_header_getter, client=http_client))
    # de-duplicate by name
    seen = set(); out = []
    for s in specs:
        if s.name not in seen:
            out.append(s); seen.add(s.name)
    return out
