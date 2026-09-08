#!/usr/bin/env python3
"""Rebuild template/index.html from index.html.

Run this only when the English page has been edited directly; the normal flow is
to edit template/index.html and run tools/build.py.

Every translatable string becomes a {{...}} placeholder holding the English text,
so the template stays readable and the English build needs no locale file: an
unknown key renders the English inside its own braces.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Same in every locale: technology names, brands, products, code identifiers,
# handles and contact values.
DNT = {
    "S. AXADJONOV", "K", "Sardorbek", "Axadjonov", "axadjonovsardorbeck@gmail.com",
    "Go", "PostgreSQL", "Redis", "gRPC", "Knative", "CloudEvents", "Casbin", "k6",
    "Docker", "GitLab&nbsp;CI", "MinIO", "S3", "Gemini", "MongoDB", "Gin", "chi",
    "PostgreSQL, pgvector, Redis, MongoDB, SQL",
    "REST, gRPC, Gin, chi, Knative Eventing / CloudEvents",
    "JWT, OTP, Casbin (RBAC)", "MinIO, S3, CDN",
    "Click, Payme, Firebase FCM, Telegram, Google Gemini, Yandex Maps",
    "Knative / FaaS, Docker, GitLab CI, goose, k6, Grafana",
    "UDEVS", "Cody Soft", "Vector-PVT",
    "CentralTour", "Furasentr Autopark", "Furasentr", "iMed",
    "(col IS NULL OR col IN (&hellip;))", "trip:point:&lt;id&gt;", "diff_km",
    "singleflight", "pgvector", "entity:version", "SELECT &hellip; FOR UPDATE",
    "Knative / FaaS", "Firebase", "CDN", "Najot Ta'lim",
    "B2", "B1", "GitHub", "LinkedIn", "Telegram",
    "github.com/axadjonovsardorbek", "sardorbek-axadjonov", "@axadjonovsardorbek",
    "PDF", "esc",
}

# Regions whose text is never page copy. SVG <text> holds code identifiers and
# field names, so it is masked — but the aria-label describing each diagram is
# prose and stays translatable.
MASK = [
    r"<style>.*?</style>",
    r"<script\b[^>]*>.*?</script>",
    r"<!--.*?-->",
    r"<text\b[^>]*>.*?</text>",
]

FONT_LINK = (
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,600;12..96,700;12..96,800'
    '&family=IBM+Plex+Mono:wght@400;500;600'
    '&family=IBM+Plex+Sans:wght@400;450;500;600&display=swap" />'
)

# Strings that live in content="" attributes the text-node scan cannot see.
META = [
    "description", "keywords", "og:description", "og:image:alt",
    "twitter:description", "twitter:image:alt",
]


# Command-palette and toast copy lives in the inline script, which the text-node
# scan cannot reach, so these literals are placeheld by exact match.
JS_STRINGS = [
    "Stack", "Experience", "Selected Work", "Education & Languages", "Contact",
    "section", "project \u00b7 booking + markup engine",
    "project \u00b7 freight marketplace", "project \u00b7 fleet management",
    "project \u00b7 learning platform", "Download CV", "pdf",
    "Copy email", "Copy phone", "Email", "Phone",
    "Toggle theme", "light / dark", "Dark theme", "Light theme",
    "No matches", " copied",
]


def placehold_js(t):
    m = re.search(r"<script>\n.*?</script>", t, re.S)
    assert m, "inline script not found"
    js = m.group(0)
    for text in sorted(JS_STRINGS, key=len, reverse=True):
        js = js.replace('"%s"' % text, '"{{%s}}"' % text)
    return t[: m.start()] + js + t[m.end():]


def masked_spans(src):
    spans = []
    for pat in MASK:
        for m in re.finditer(pat, src, re.S):
            spans.append((m.start(), m.end()))
    return spans


def collect(src):
    spans = masked_spans(src)

    def is_masked(i):
        return any(a <= i < b for a, b in spans)

    found, seen = [], set()

    def add(text):
        text = text.strip()
        if not text or not re.search(r"[A-Za-z]", text):
            return
        if text in seen or text in DNT:
            return
        seen.add(text)
        found.append(text)

    # text nodes, tolerating the indentation around multi-line copy
    for m in re.finditer(r">([^<>]+)<", src):
        if not is_masked(m.start()):
            add(m.group(1))

    for attr in ("aria-label", "placeholder", "alt"):
        for m in re.finditer(attr + r'="([^"]+)"', src):
            if not is_masked(m.start()):
                add(m.group(1))

    for name in META:
        key = "property" if name.startswith("og:") else "name"
        m = re.search(r'<meta %s="%s" content="([^"]+)"' % (key, re.escape(name)), src)
        if m:
            add(m.group(1))

    return found


def placehold(src, strings):
    out = src
    hits = 0
    # longest first so a short string never eats part of a longer one
    for text in sorted(strings, key=len, reverse=True):
        esc = re.escape(text)

        def sub_text(m, t=text):
            return ">" + m.group(1) + "{{" + t + "}}" + m.group(2) + "<"

        out, n = re.subn(r">(\s*)" + esc + r"(\s*)<", sub_text, out)
        hits += n
        for attr in ("aria-label", "placeholder", "alt", "content"):
            needle = '%s="%s"' % (attr, text)
            if needle in out:
                hits += out.count(needle)
                out = out.replace(needle, '%s="{{%s}}"' % (attr, text))
    return out, hits


def parameterise(t):
    """Swap the locale-dependent head bits for build tokens."""
    subs = [
        # root-absolute so /ru/ and /uz/ resolve the same assets
        ('<link rel="icon" href="favicon.svg"', '<link rel="icon" href="/favicon.svg"'),
        ('<link rel="apple-touch-icon" href="og.png" />',
         '<link rel="apple-touch-icon" href="/og.png" />'),
        ('href="cv.pdf"', 'href="/cv.pdf"'),
        ('<link rel="canonical" href="https://axadjonovsardorbek.uz/" />',
         '<link rel="canonical" href="__CANONICAL__" />\n<!--HREFLANG-->'),
        ('<meta property="og:url" content="https://axadjonovsardorbek.uz/" />',
         '<meta property="og:url" content="__CANONICAL__" />'),
        ('<meta property="og:locale" content="en_US" />',
         '<meta property="og:locale" content="__OGLOCALE__" />'),
        ('<html lang="en">', '<html lang="__LANG__">'),
        # Bricolage Grotesque ships no Cyrillic, so the font set is per locale
        (FONT_LINK, '<!--FONTS-->'),
        # language switcher slots
        ('    <div class="bar-tools">\n      <button class="kbd-btn"',
         '    <div class="bar-tools">\n      <!--LANG_SWITCH-->\n      <button class="kbd-btn"'),
        ('  <a class="cv" href="/cv.pdf"',
         '  <!--LANG_SWITCH_MOBILE-->\n  <a class="cv" href="/cv.pdf"'),
    ]
    for a, b in subs:
        assert a in t, "anchor not found: " + a[:70]
        t = t.replace(a, b, 1) if a.startswith(("    <div", "  <a class")) else t.replace(a, b)

    # the JSON-LD graph is rebuilt per locale
    t = re.sub(r'<script type="application/ld\+json">.*?</script>', "<!--JSONLD-->", t, flags=re.S)
    return t


def add_switcher_css(t):
    css = """  /* ---------- language switcher ---------- */
  .langs {
    display: flex;
    align-items: center;
    gap: 2px;
    padding: 2px;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 999px;
  }
  .langs a {
    font-family: var(--f-mono);
    font-size: 10px;
    letter-spacing: 0.12em;
    text-decoration: none;
    color: var(--muted);
    padding: 0.32rem 0.5rem;
    border-radius: 999px;
    transition: color 0.25s, background 0.25s;
  }
  .langs a:hover { color: var(--ink); }
  .langs a.is-on {
    color: var(--accent);
    background: var(--accent-soft);
    box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--accent) 26%, transparent);
  }
  @media (max-width: 680px) { .topbar .langs { display: none; } }

  .mobile-menu .langs-row {
    display: flex;
    gap: 0.5rem;
    padding: 0.9rem 0 0.2rem;
    border-bottom: 1px solid var(--line);
  }
  .mobile-menu .langs-row a {
    flex: 1;
    justify-content: center;
    padding: 0.55rem 0;
    margin-bottom: 0.7rem;
    font-family: var(--f-mono);
    font-size: var(--step--2);
    font-weight: 400;
    letter-spacing: 0.16em;
    color: var(--muted);
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 999px;
  }
  .mobile-menu .langs-row a.is-on {
    color: var(--accent);
    border-color: var(--accent);
    background: var(--accent-soft);
  }

  /* ---------- toast ---------- */"""
    anchor = "  /* ---------- toast ---------- */"
    assert anchor in t
    return t.replace(anchor, css, 1)


def main():
    src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    strings = collect(src)
    out, hits = placehold(src, strings)
    out = parameterise(out)
    out = add_switcher_css(out)
    out = placehold_js(out)

    os.makedirs(os.path.join(ROOT, "template"), exist_ok=True)
    open(os.path.join(ROOT, "template", "index.html"), "w", encoding="utf-8").write(out)

    unique = len(set(re.findall(r"\{\{(.*?)\}\}", out, re.S)))
    print("collected %d strings, wrote %d placeholders (%d unique)" % (len(strings), hits, unique))
    missed = [s for s in strings if "{{%s}}" % s not in out]
    if missed:
        print("NOT PLACED (%d):" % len(missed))
        for s in missed:
            print("   |%s|" % s[:90])


if __name__ == "__main__":
    main()
