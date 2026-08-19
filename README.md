# KoriKatha

An editorial storefront and inventory system for **KoriKatha — কড়িকথা**, celebrating traditional Bengali sarees, handcrafted jewellery, and the stories of Bengal's makers.

## Run locally

This is a dependency-free static site. Start any local file server in this directory, for example:

```bash
python3 -m http.server 4173
```

Then open `http://localhost:4173`.

## Deploy

The site is ready for GitHub Pages and can be served directly from the repository root.

## Catalogue and inventory

- `shop.html` provides search, category filters, sorting, and stock labels for the first 10 products.
- `data/products.json` is the static GitHub Pages catalogue fallback.
- `inventory.html` is the authenticated inventory dashboard.
- `inspiration.html` is a separately labelled 1,000-image visual reference archive.
- `data/inspiration.json` records the source, creator, and license for every archive image.
- `supabase/schema.sql` and `supabase/seed.sql` create and populate the protected backend.
- `supabase/README.md` contains the one-time Supabase setup.
- `scripts/generate_catalog.py` deterministically rebuilds all catalogue and import files.

The two optional prompt manifests in `data/` contain five saree and five jewellery image jobs. Image generation requires `OPENAI_API_KEY`; it is intentionally never stored in this repository.

Run `python3 scripts/build_inspiration_gallery.py` to resume or rebuild the licensed Wikimedia Commons archive. The downloader is intentionally rate-limited and stores resumable plans under `data/inspiration-plans/`.

To create all optimized product images, copy `.env.example` to `.env.local`, add the API key, install `openai` and `Pillow` for Python, then run `sh scripts/generate_product_images.sh`.

## Notes

- The initial shop catalogue uses attributed Creative Commons reference photography; see `image-credits.html`.
- Contact and newsletter forms submit to `houseofkorikatha@gmail.com` through FormSubmit.
