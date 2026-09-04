# axadjonovsardorbek.uz

Personal CV / portfolio site for Sardorbek Axadjonov — Go backend developer.

Static site, no build step.

| File | Purpose |
| --- | --- |
| `index.html` | The portfolio site |
| `cv.html` | Print-ready one-page résumé (source for the PDF) |
| `cv.pdf` | Generated résumé, linked from the hero "Download CV" button |
| `assets/og.html` | Source for the social preview image |
| `og.png` | Generated 1200×630 Open Graph image |
| `favicon.svg` | Tab icon |
| `robots.txt`, `sitemap.xml` | Crawler hints; `cv.html` and `assets/` are excluded |

## Analytics

`index.html` loads `/_vercel/insights/script.js` (Vercel Web Analytics — cookieless,
no consent banner needed). Turn it on under **Project → Analytics** in the Vercel
dashboard, otherwise the script simply 404s and nothing is collected.

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

## Deploy

Hosted on Vercel. Push to `main` auto-deploys.

```bash
npx vercel --prod
```
