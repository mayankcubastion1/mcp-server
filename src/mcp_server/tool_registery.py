from .leaves.tools import create_tool_specs as leaves
from .attendance.tools import create_tool_specs as attendance
from .feedback.tools import create_tool_specs as feedback
from .tickets.tools import create_tool_specs as tickets
from .team_management.tools import create_tool_specs as team
from .miscellaneous.tools import create_tool_specs as misc
# (optional) referrals if you added it earlier:
try:
    from .referrals.tools import create_tool_specs as referrals
except Exception:
    referrals = None

def all_tool_specs(base_url: str, auth_header_getter, http_client=None):
    specs = []
    for f in (leaves, attendance, feedback, tickets, team, misc):
        specs.extend(f(base_url, auth_header_getter, client=http_client))
    if referrals:
        specs.extend(referrals(base_url, auth_header_getter, client=http_client))
    # de-dup by name
    seen, out = set(), []
    for s in specs:
        if s.name not in seen:
            out.append(s); seen.add(s.name)
    return out
