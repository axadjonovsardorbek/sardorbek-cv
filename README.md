# axadjonovsardorbek.uz

Personal CV / portfolio site for Sardorbek Axadjonov — Go backend developer.

Static site. One small build step generates the three language pages.

> **Edit `template/index.html`, never `index.html`.** The three `index.html`
> files are generated output and any change made to them directly is lost on the
> next build.

| File | Purpose |
| --- | --- |
| `template/index.html` | **Source of truth** for the site — English copy with `{{…}}` placeholders |
| `i18n/ru.json`, `i18n/uz.json` | Translations, keyed by the English string |
| `tools/build.py` | Renders the template into all three pages |
| `tools/make_template.py` | One-shot scaffolding; only needed if the template is ever rebuilt from a plain HTML page |
| `index.html` | Generated English page (site root) |
| `ru/index.html`, `uz/index.html` | Generated Russian and Uzbek pages |
| `cv.html` | Print-ready one-page résumé (source for the PDF) |
| `cv.pdf` | Generated résumé, linked from the hero "Download CV" button |
| `assets/og.html` | Source for the social preview image |
| `og.png` | Generated 1200×630 Open Graph image |
| `assets/icon.html` | Source for the SA monogram icons |
| `favicon.ico`, `favicon.svg` | Tab icon — ICO for Safari and crawlers, SVG for everything modern |
| `apple-touch-icon.png` | 180×180 iOS home-screen icon |
| `icon-192.png`, `icon-512.png`, `site.webmanifest` | Android / installable icon set |
| `favicon-32.png` | Source bitmap the ICO is wrapped around |
| `robots.txt`, `sitemap.xml` | Crawler hints; `cv.html` and `assets/` are excluded |
| `googlee05561e621d94a1c.html`, `yandex_34e841ce5c9772d1.html` | Search console verification files — keep both reachable |

## Languages

The site ships in English (`/`), Russian (`/ru/`) and Uzbek (`/uz/`), each a real
static page with its own URL — so all three are indexable and linked to each
other with `hreflang`.

```bash
python3 tools/build.py        # rebuild all three pages
python3 tools/build.py -v     # also list every untranslated string
```

Placeholders are written `{{English text}}`, so the template reads as English
prose and the English page needs no translation file: an unknown key renders the
text inside its own braces. That also means a half-finished translation still
produces a complete page — untranslated strings simply stay English, and the
build reports how many.

To change wording, edit `template/index.html`, add the same English string as a
key in `i18n/ru.json` and `i18n/uz.json`, then rebuild.

Deliberately left in English everywhere: technology names, product names, code
identifiers, and the `<text>` labels inside the architecture diagrams — those are
field and column names (`markup_rules`, `centbed_net`, `is_current`). The prose
around each diagram, including the long `aria-label` that describes it to a
screen reader, is translated.

**Fonts are per locale.** Bricolage Grotesque has no Cyrillic subset, so a
Russian heading set in it falls back mid-word to whatever the system has. The
Russian build swaps the display face for Manrope, which covers Cyrillic;
`tools/build.py` holds that mapping in `FONTS`.

## SEO

Everything lives in the `<head>` of `index.html` plus the two crawler files.

| Layer | What is there |
| --- | --- |
| Core meta | `title`, `description`, `keywords`, `author`, `canonical`, `robots` + `googlebot` (with `max-snippet:-1`, `max-image-preview:large`) |
| Appearance | `color-scheme`, and two `theme-color` tags scoped with `media` so the browser chrome follows the light / dark palette |
| Social | Full Open Graph `profile` card and a Twitter `summary_large_image` card, both pointing at `og.png` with dimensions, MIME type and alt text |
| Structured data | One JSON-LD `@graph` with five linked nodes: `WebSite`, `ProfilePage`, `ImageObject`, `DigitalDocument` (the résumé PDF) and `Person` |
| Crawler files | `robots.txt` (points at the sitemap, excludes `cv.html` and `assets/`) and `sitemap.xml` (all three language pages with `xhtml:link` alternates, plus `cv.pdf`) |
| Languages | Per-page `lang`, `canonical` and `og:locale`, and a four-entry `hreflang` set (en, ru, uz, x-default) on every page |

The `Person` node is the hub — every other node references it by `@id`, and it
carries `hasOccupation`, `knowsAbout`, `knowsLanguage`, `alumniOf`, `worksFor`
and `sameAs`. Keep the `@id` values stable; they are what ties the graph
together.

Document outline is one `h1` (the name), one `h2` per section, `h3` for each job
and project. If you add a section, give it a real `h2` — the section label in
`.sec-label` is that heading, not a styled `span`.

### Search console verification

Google and Yandex are each verified twice, so losing one method does not drop the
property:

| Engine | Meta tag in `<head>` | Reserve file at the site root |
| --- | --- | --- |
| Google | `google-site-verification` | `googlee05561e621d94a1c.html` |
| Yandex | `yandex-verification` | `yandex_34e841ce5c9772d1.html` |

Both files must keep their exact filenames and contents, and must stay crawlable —
do not add them to `robots.txt`. Submit `sitemap.xml` from inside each console
once the property is verified.

After changing page content, bump `<lastmod>` in `sitemap.xml` and `dateModified`
in the `ProfilePage` node.

## Analytics

`index.html` loads two Vercel scripts, both cookieless and needing no consent banner:

- `/_vercel/insights/script.js` — Web Analytics (visitors, page views, referrers)
- `/_vercel/speed-insights/script.js` — Speed Insights (real-user Core Web Vitals)

Turn each on in the Vercel dashboard under **Project → Analytics** and
**Project → Speed Insights**. Until then the scripts 404 and nothing is collected.
The dashboard's "Get Started" panel defaults to Next.js instructions — switch its
framework dropdown to **Other**, since this is a plain static site and the script
tags above are already the whole integration.

## Regenerating assets

Both generated files come from headless Chrome. Run from the repo root.

```bash
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# og.png — social preview
"$CHROME" --headless --disable-gpu --hide-scrollbars \
  --window-size=1200,630 --screenshot=og.png \
  --virtual-time-budget=8000 assets/og.html

# cv.pdf — one-page A4 résumé
"$CHROME" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=cv.pdf --virtual-time-budget=9000 cv.html
```

Re-run these after editing `assets/og.html` or `cv.html`.

Icons come from `assets/icon.html`. Chrome will not open a window narrower than
about 500px, so the small sizes are downscaled from the 512 master rather than
screenshotted directly — screenshotting at 32×32 silently yields a crop of the
top-left corner instead.

```bash
"$CHROME" --headless --disable-gpu --hide-scrollbars \
  --window-size=512,512 --screenshot=icon-512.png \
  --virtual-time-budget=7000 assets/icon.html

for S in 32:favicon-32 180:apple-touch-icon 192:icon-192; do
  cp icon-512.png "${S#*:}.png"
  sips -z "${S%%:*}" "${S%%:*}" "${S#*:}.png" >/dev/null
done

# favicon.ico is the 32px PNG in an ICO container
python3 -c "
import struct
png = open('favicon-32.png','rb').read()
open('favicon.ico','wb').write(
    struct.pack('<HHH', 0, 1, 1)
    + struct.pack('<BBBBHHII', 32, 32, 0, 0, 1, 32, len(png), 22)
    + png)
"
```

The résumé PDF is English only and is linked from all three language pages.

## Deploy

Hosted on Vercel. Push to `main` auto-deploys.

```bash
python3 tools/build.py    # commit the regenerated pages alongside the template
npx vercel --prod
```

The generated pages are committed, so Vercel needs no build command.
