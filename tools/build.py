#!/usr/bin/env python3
"""Render template/index.html into one static page per locale.

    python3 tools/build.py

Writes index.html (English, site root), ru/index.html and uz/index.html.

Placeholders in the template are written {{English text}}. A locale file maps
that English text to its translation; anything a locale file does not cover
falls back to the English inside the braces, so a half-finished translation
still produces a complete page and English needs no locale file at all.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://axadjonovsardorbek.uz"

LOCALES = [
    # code, output dir, url path, og:locale, display label
    ("en", "", "/", "en_US", "EN"),
    ("ru", "ru", "/ru/", "ru_RU", "RU"),
    ("uz", "uz", "/uz/", "uz_UZ", "UZ"),
]

GF = "https://fonts.googleapis.com/css2?"
PLEX = "family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;450;500;600"

# Bricolage Grotesque has no Cyrillic subset, so a Russian heading set in it
# falls back mid-word to whatever the system offers. Russian gets Manrope for
# the display face instead; Latin locales keep Bricolage.
FONTS = {
    "default": '<link rel="stylesheet" href="%sfamily=Bricolage+Grotesque:opsz,wght@'
               '12..96,500;12..96,600;12..96,700;12..96,800&%s&display=swap" />' % (GF, PLEX),
    "ru": '<link rel="stylesheet" href="%sfamily=Manrope:wght@500;600;700;800&%s'
          '&display=swap" />\n'
          '<style>:root { --f-display: "Manrope", "Segoe UI", system-ui, sans-serif; }</style>'
          % (GF, PLEX),
}


def load_strings(code):
    path = os.path.join(ROOT, "i18n", code + ".json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def lang_switch(current, mobile=False):
    cls = "langs langs-row" if mobile else "langs"
    tag = "div" if mobile else "nav"
    rows = []
    for code, _dir, path, _og, label in LOCALES:
        on = code == current
        attrs = ' class="is-on" aria-current="true"' if on else ""
        rows.append(
            '<a href="%s" hreflang="%s"%s>%s</a>' % (path, code, attrs, label)
        )
    label = ' aria-label="Language"' if not mobile else ""
    return '<%s class="%s"%s>%s</%s>' % (tag, cls, label, "".join(rows), tag)


def hreflang_block():
    out = []
    for code, _dir, path, _og, _label in LOCALES:
        out.append('<link rel="alternate" hreflang="%s" href="%s%s" />' % (code, SITE, path))
    out.append('<link rel="alternate" hreflang="x-default" href="%s/" />' % SITE)
    return "\n".join(out)


def json_ld(code, url, strings):
    def t(s):
        return strings.get(s, s)

    person_id = SITE + "/#person"
    image_id = SITE + "/#image"
    website_id = SITE + "/#website"
    page_id = url + "#webpage"

    graph = [
        {
            "@type": "WebSite",
            "@id": website_id,
            "url": SITE + "/",
            "name": "Sardorbek Axadjonov",
            "description": t("Portfolio and CV of Sardorbek Axadjonov, Go backend developer."),
            "inLanguage": code,
            "publisher": {"@id": person_id},
        },
        {
            "@type": "ProfilePage",
            "@id": page_id,
            "url": url,
            "name": t("Sardorbek Axadjonov — Go Backend Developer"),
            "description": t(
                "Go backend developer with 2+ years in production — microservices and "
                "event-driven serverless systems for travel, e-commerce, and "
                "fleet-management platforms."
            ),
            "isPartOf": {"@id": website_id},
            "about": {"@id": person_id},
            "mainEntity": {"@id": person_id},
            "primaryImageOfPage": {"@id": image_id},
            "inLanguage": code,
            "dateModified": "2026-09-08",
        },
        {
            "@type": "ImageObject",
            "@id": image_id,
            "url": SITE + "/og.png",
            "contentUrl": SITE + "/og.png",
            "width": 1200,
            "height": 630,
            "encodingFormat": "image/png",
            "caption": t("Sardorbek Axadjonov — Go backend developer"),
        },
        {
            "@type": "DigitalDocument",
            "@id": SITE + "/cv.pdf#resume",
            "name": "Sardorbek Axadjonov — Résumé",
            "url": SITE + "/cv.pdf",
            "encodingFormat": "application/pdf",
            "inLanguage": "en",
            "author": {"@id": person_id},
            "about": {"@id": person_id},
        },
        {
            "@type": "Person",
            "@id": person_id,
            "name": "Sardorbek Axadjonov",
            "givenName": "Sardorbek",
            "familyName": "Axadjonov",
            "jobTitle": t("Backend Developer"),
            "description": t(
                "Go backend developer with 2+ years in production, building microservices "
                "and event-driven serverless systems for travel, e-commerce, and "
                "fleet-management platforms."
            ),
            "url": SITE + "/",
            "mainEntityOfPage": {"@id": page_id},
            "image": {"@id": image_id},
            "subjectOf": {"@id": SITE + "/cv.pdf#resume"},
            "email": "mailto:axadjonovsardorbeck@gmail.com",
            "telephone": "+998200070424",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "Tashkent",
                "addressCountry": "UZ",
            },
            "nationality": {"@type": "Country", "name": "Uzbekistan"},
            "knowsLanguage": [
                {"@type": "Language", "name": "Uzbek", "alternateName": "uz"},
                {"@type": "Language", "name": "Russian", "alternateName": "ru"},
                {"@type": "Language", "name": "English", "alternateName": "en"},
            ],
            "knowsAbout": [
                "Go", "PostgreSQL", "Redis", "MongoDB", "gRPC", "REST APIs",
                "Knative", "CloudEvents", "Casbin", "Docker", "GitLab CI", "k6",
                "Microservices", "Event-driven architecture", "Serverless",
            ],
            "hasOccupation": {
                "@type": "Occupation",
                "name": t("Backend Developer"),
                "occupationalCategory": "15-1252.00",
                "occupationLocation": {"@type": "City", "name": "Tashkent"},
                "skills": "Go, PostgreSQL, Redis, gRPC, Knative, CloudEvents, "
                          "microservices, event-driven architecture, serverless",
            },
            "alumniOf": {"@type": "EducationalOrganization", "name": "Najot Ta'lim"},
            "worksFor": {"@type": "Organization", "name": "UDEVS"},
            "sameAs": [
                "https://github.com/axadjonovsardorbek",
                "https://www.linkedin.com/in/sardorbek-axadjonov-b28603295/",
                "https://t.me/axadjonovsardorbek",
            ],
        },
    ]
    body = json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, indent=2)
    return '<script type="application/ld+json">\n%s\n</script>' % body


PLACEHOLDER = re.compile(r"\{\{(.*?)\}\}", re.S)


def render(template, code, out_dir, path, og_locale):
    strings = load_strings(code)
    url = SITE + path
    missing = []

    def swap(m):
        key = m.group(1)
        if code != "en" and key not in strings:
            missing.append(key)
        return strings.get(key, key)

    page = PLACEHOLDER.sub(swap, template)
    page = page.replace("__LANG__", code)
    page = page.replace("__CANONICAL__", url)
    page = page.replace("__OGLOCALE__", og_locale)
    page = page.replace("<!--FONTS-->", FONTS.get(code, FONTS["default"]))
    page = page.replace("<!--HREFLANG-->", hreflang_block())
    page = page.replace("<!--JSONLD-->", json_ld(code, url, strings))
    page = page.replace("<!--LANG_SWITCH-->", lang_switch(code))
    page = page.replace("<!--LANG_SWITCH_MOBILE-->", lang_switch(code, mobile=True))

    target_dir = os.path.join(ROOT, out_dir) if out_dir else ROOT
    os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, "index.html")
    with open(target, "w", encoding="utf-8") as f:
        f.write(page)
    return target, sorted(set(missing))


def main():
    with open(os.path.join(ROOT, "template", "index.html"), encoding="utf-8") as f:
        template = f.read()

    left = PLACEHOLDER.findall(template)
    print("template: %d placeholders (%d unique)" % (len(left), len(set(left))))

    for code, out_dir, path, og_locale, _label in LOCALES:
        target, missing = render(template, code, out_dir, path, og_locale)
        rel = os.path.relpath(target, ROOT)
        note = "" if not missing else "  (%d untranslated, falls back to English)" % len(missing)
        print("  %-2s -> %-16s%s" % (code, rel, note))
        if missing and "-v" in sys.argv:
            for k in missing:
                print("       .. " + k[:100])


if __name__ == "__main__":
    main()
