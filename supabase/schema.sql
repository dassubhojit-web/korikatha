create extension if not exists pgcrypto;

create table if not exists public.products (
  id uuid primary key default gen_random_uuid(),
  sku text unique not null,
  name text not null,
  category text not null check (category in ('saree','jewellery')),
  subcategory text not null,
  description text not null,
  price integer not null check (price >= 0),
  compare_at_price integer check (compare_at_price >= price),
  quantity integer not null default 0 check (quantity >= 0),
  reorder_level integer not null default 5 check (reorder_level >= 0),
  colour text, motif text, material text, image text,
  featured boolean not null default false,
  active boolean not null default true,
  updated_at timestamptz not null default now()
);

create table if not exists public.inventory_admins (
  user_id uuid primary key references auth.users(id) on delete cascade,
  created_at timestamptz not null default now()
);

create or replace function public.is_inventory_admin()
returns boolean language sql stable security definer set search_path = public
as $$ select exists(select 1 from public.inventory_admins where user_id = auth.uid()) $$;

revoke all on function public.is_inventory_admin() from public;
grant execute on function public.is_inventory_admin() to authenticated;

create or replace function public.set_updated_at()
returns trigger language plpgsql set search_path = public
as $$ begin new.updated_at = now(); return new; end $$;

drop trigger if exists products_updated_at on public.products;
create trigger products_updated_at before update on public.products
for each row execute function public.set_updated_at();

alter table public.products enable row level security;
alter table public.inventory_admins enable row level security;

drop policy if exists "Public can view active products" on public.products;
create policy "Public can view active products" on public.products for select
using (active or public.is_inventory_admin());

drop policy if exists "Admins manage products" on public.products;
create policy "Admins manage products" on public.products for all
using (public.is_inventory_admin()) with check (public.is_inventory_admin());

drop policy if exists "Admins can view own membership" on public.inventory_admins;
create policy "Admins can view own membership" on public.inventory_admins for select
using (user_id = auth.uid());

grant usage on schema public to anon, authenticated;
grant select on public.products to anon, authenticated;
grant insert, update, delete on public.products to authenticated;
grant select on public.inventory_admins to authenticated;

create index if not exists products_category_idx on public.products(category);
create index if not exists products_quantity_idx on public.products(quantity);
create index if not exists products_active_idx on public.products(active);

-- After creating your owner in Authentication > Users, run this with that user's UUID:
-- insert into public.inventory_admins (user_id) values ('YOUR-AUTH-USER-UUID');
