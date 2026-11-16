# blog.valdorjets.com

Valdor Jets guides and waitlist, hosted on GitHub Pages.

- **Articles** are committed automatically by [content-engine](https://github.com/valdor-jets/content-engine) as `<slug>/index.html`, `hero.jpg` and `meta.json`.
- **Every push** rebuilds the site (`build.py`): home page with article cards, `/waitlist/`, `feed.xml`, `sitemap.xml`.
- **Waitlist form** (`assets/waitlist.js`) posts to the Cloudflare Worker in content-engine's `waitlist/` folder. Signups live in your Cloudflare D1 database.
- To edit the look: `assets/site.css` and `templates/`. To remove an article, delete its folder.

Preview locally: `python build.py && python -m http.server -d _site`.
