"""Domain / business logic for the web app.

Keep business rules and data mutations here, not in views — views stay thin.
`import-linter` enforces that this module never imports the view or form layer
(see `.importlinter`), so the dependency direction can only be views -> services.
Replace these examples with your own domain logic.
"""

from web.models import Message


def greeting(name: str = "") -> str:
    """Return a greeting. Plain text only — escaping is the template's job."""
    name = name.strip()
    return f"Hello, {name}!" if name else "Hello, world!"


def recent_messages(limit: int = 5) -> list[Message]:
    return list(Message.objects.all()[:limit])
