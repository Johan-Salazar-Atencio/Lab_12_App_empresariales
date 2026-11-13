from rest_framework.permissions import SAFE_METHODS, BasePermission

AGENT_GROUP = "agente"

WRITE_METHODS = ("POST", "PUT", "PATCH")


class AgentPermission(BasePermission):
    """Who may do what. This is the SERVER's rule: it holds even if a client misbehaves.

    The rule the lab asks for:
      - anybody, even anonymous, can read (GET, HEAD, OPTIONS);
      - a person (user with is_staff) can do anything else;
      - a member of the group «agente» can create and modify, but NEVER delete;
      - anybody else who is logged in can only read;
      - an unknown method is denied (deny by default).
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.is_staff:
            return True
        if user.groups.filter(name=AGENT_GROUP).exists():
            return request.method in WRITE_METHODS
        return False
