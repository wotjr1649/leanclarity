"""Page assembly. Calls the fragment renderers."""

from app.render import render_field, render_image


def settings_page(fields, logo):
    parts = [render_image(logo), "<form method='post'>"]
    parts.extend(render_field(f) for f in fields)
    parts.append("<button type='submit'>Save</button></form>")
    return "\n".join(p for p in parts if p)
