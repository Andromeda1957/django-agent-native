"""Example negative security test.

Demonstrates the security-testing discipline the template expects: for every
trust boundary, prove the control works. Here: user-controlled input reflected
into a page must be HTML-escaped (XSS defense). Add tests like this near the
domain that owns each boundary.
"""

from django.test import TestCase
from django.urls import reverse


class XssEscapingTests(TestCase):
    def test_reflected_input_is_escaped(self):
        payload = "<script>alert(1)</script>"
        response = self.client.get(reverse("web:home"), {"name": payload})
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        # The raw payload must never appear unescaped...
        self.assertNotIn(payload, body)
        # ...it must be HTML-escaped by Django's template auto-escaping.
        self.assertIn("&lt;script&gt;", body)
