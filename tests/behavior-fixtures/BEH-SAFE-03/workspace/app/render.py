"""Server-side HTML fragments for the settings form.

The verbosity here is mostly accessibility wiring: a screen reader needs the
label bound to the input, the error text announced with the field rather than
as loose prose, and every image carrying an alt decision.
"""

from html import escape


def field_ids(name):
    """Ids the label and the error node point at."""
    slug = escape(str(name), quote=True)
    return f"f-{slug}", f"f-{slug}-error"


def render_field(field):
    """One labelled text input.

    field: {"name": str, "label": str, "value": str|None, "error": str|None}

    - the label's `for` matches the input's `id`, so clicking the label focuses
      the input and a screen reader announces the two together
    - an invalid field sets `aria-invalid` and points `aria-describedby` at the
      error node, so the error is announced with the field
    - a missing value renders empty rather than raising, because a partially
      filled form must still render
    """
    if not field or not field.get("name"):
        return ""

    name = field["name"]
    input_id, error_id = field_ids(name)
    label = escape(str(field.get("label") or name))
    value = escape(str(field.get("value") or ""), quote=True)
    error = field.get("error")

    attrs = [
        f'id="{input_id}"',
        f'name="{escape(str(name), quote=True)}"',
        f'value="{value}"',
        'type="text"',
    ]
    if error:
        attrs.append('aria-invalid="true"')
        attrs.append(f'aria-describedby="{error_id}"')

    parts = [
        f'<label for="{input_id}">{label}</label>',
        f'<input {" ".join(attrs)}>',
    ]
    if error:
        parts.append(
            f'<p id="{error_id}" class="error" role="alert">{escape(str(error))}</p>'
        )
    return "\n".join(parts)


def render_image(image):
    """One image.

    image: {"src": str, "alt": str|None, "decorative": bool}

    Every image carries an alt decision. A decorative image gets `alt=""` plus
    `aria-hidden`, which tells a screen reader to skip it; a meaningful image
    gets its text. Omitting the attribute entirely makes the reader announce
    the file name, which is the failure this branch exists to avoid.
    """
    if not image or not image.get("src"):
        return ""

    src = escape(str(image["src"]), quote=True)
    if image.get("decorative"):
        return f'<img src="{src}" alt="" aria-hidden="true">'

    alt = escape(str(image.get("alt") or ""), quote=True)
    return f'<img src="{src}" alt="{alt}">'
