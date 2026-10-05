-- Luma Skin Care — database schema (Supabase / PostgreSQL)
-- Run this in Supabase Dashboard -> SQL Editor.
-- Feature 1 needs only the `products` table. Tables for later features
-- (admins, invitations, scan_logs) will be added when those features start.

create extension if not exists "pgcrypto";

-- ---------------------------------------------------------------------------
-- products
-- One table for every product. Re-importing an Excel file upserts rows by
-- `sku`, so a printed QR (which points to /products/{sku}) keeps working
-- and shows the latest data.
-- ---------------------------------------------------------------------------
create table if not exists public.products (
    id           uuid primary key default gen_random_uuid(),
    sku          text not null unique check (sku ~ '^LS-[0-9]{4}$'),
    name         text not null,
    category     text not null check (category in
                   ('Cleanser', 'Toner', 'Serum', 'Moisturizer', 'Sunscreen', 'Mask')),
    price        numeric(10, 2) not null check (price > 0),
    size         text,
    description  text,
    how_to_use   text,
    status       text not null default 'active' check (status in ('active', 'inactive')),
    image_url    text,
    created_at   timestamptz not null default now(),
    updated_at   timestamptz not null default now()
);

create index if not exists products_status_idx on public.products (status);
create index if not exists products_category_idx on public.products (category);

-- Keep updated_at fresh on every update
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists products_set_updated_at on public.products;
create trigger products_set_updated_at
    before update on public.products
    for each row execute function public.set_updated_at();

-- Requirement: an empty status counts as 'active'. Normalising here (instead of
-- only in the importer) means every write path follows the rule.
create or replace function public.normalize_product_status()
returns trigger
language plpgsql
as $$
begin
    new.status = coalesce(nullif(lower(trim(new.status)), ''), 'active');
    return new;
end;
$$;

drop trigger if exists products_normalize_status on public.products;
create trigger products_normalize_status
    before insert or update on public.products
    for each row execute function public.normalize_product_status();

-- The FastAPI backend talks to Supabase with the service_role key, so RLS is
-- enabled with no public policies: the browser can never read/write directly.
alter table public.products enable row level security;
