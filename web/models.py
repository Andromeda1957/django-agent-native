from django.db import models


class Message(models.Model):
    """Minimal example model. Replace with your own domain models.

    Exists so the demo has a database table, an admin entry, and something for
    the service layer and tests to exercise.
    """

    text = models.CharField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.text
