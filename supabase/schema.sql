-- Luma Skin Care — database schema (Supabase / PostgreSQL)
-- Run this in Supabase Dashboard -> SQL Editor.
-- Safe to re-run: every statement is idempotent.

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

-- ---------------------------------------------------------------------------
-- admins  (Feature 2)
-- Passwords and invitation emails are handled by Supabase Auth (auth.users).
-- This table adds what Supabase Auth does not know about: the back-office role
-- and whether the account may log in. There is no sign-up page: the first
-- super_admin is created with backend/scripts/create_super_admin.py, every
-- other account comes from a super_admin invitation.
--   super_admin : everything an admin can do + manage admin accounts
--   admin       : manage products (import, edit, images, QR)
-- activated_at is null while the invitation has not been accepted yet.
-- ---------------------------------------------------------------------------
create table if not exists public.admins (
    id             uuid primary key references auth.users (id) on delete cascade,
    email          text not null unique check (email = lower(email)),
    role           text not null default 'admin' check (role in ('super_admin', 'admin')),
    is_active      boolean not null default true,
    invited_by     uuid references public.admins (id) on delete set null,
    invited_at     timestamptz,
    activated_at   timestamptz,
    last_login_at  timestamptz,
    created_at     timestamptz not null default now(),
    updated_at     timestamptz not null default now()
);

-- Migration from the first Feature 2 draft (own bcrypt passwords + invitation table)
drop table if exists public.admin_invitations;
alter table public.admins drop column if exists password_hash;
alter table public.admins add column if not exists invited_at timestamptz;
alter table public.admins add column if not exists activated_at timestamptz;
delete from public.admins a where not exists (select 1 from auth.users u where u.id = a.id);
alter table public.admins alter column id drop default;
do $$
begin
    if not exists (
        select 1 from pg_constraint
        where conrelid = 'public.admins'::regclass and conname = 'admins_id_fkey'
    ) then
        alter table public.admins
            add constraint admins_id_fkey foreign key (id) references auth.users (id) on delete cascade;
    end if;
end;
$$;

drop trigger if exists admins_set_updated_at on public.admins;
create trigger admins_set_updated_at
    before update on public.admins
    for each row execute function public.set_updated_at();

alter table public.admins enable row level security;
