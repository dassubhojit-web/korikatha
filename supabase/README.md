# KoriKatha inventory setup

1. Create a Supabase project.
2. In the SQL Editor, run `schema.sql`, then run `seed.sql`.
3. In Authentication > Users, create the owner account.
4. Copy that user's UUID and run `insert into public.inventory_admins (user_id) values ('USER-UUID');`.
5. Copy `supabase-config.example.js` to `supabase-config.js` at the site root.
6. Add the project URL and the **publishable/anon** key. Never put a service-role key in the website.
7. Deploy the updated site and sign in at `inventory.html`.

The public shop can only read active products. Inventory updates require an authenticated user listed in `inventory_admins` and are protected by Row Level Security.

Run `python3 scripts/generate_catalog.py` to regenerate the 10-item catalogue, import files, and optional image prompt manifests.
