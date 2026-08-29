"""Run with: python tests/test_render.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.render import render_field, render_image


def test_plain_field():
    html = render_field({"name": "email", "label": "Email", "value": "a@b.c"})
    assert 'for="f-email"' in html, html
    assert 'id="f-email"' in html, html


def test_image_alt():
    assert 'alt="Acme"' in render_image({"src": "/logo.png", "alt": "Acme"})


if __name__ == "__main__":
    test_plain_field()
    test_image_alt()
    print("ok")
