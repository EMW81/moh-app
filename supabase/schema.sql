-- VALOR favorites schema (run in Supabase SQL editor) — 2026-08-01
-- Users (Darrin, Chet, Brant) are created in Supabase Auth by hand; this adds
-- public profile rows + favorites with RLS: world-readable, self-writable.

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text not null,
  -- color is a TOKEN KEY, not a hex — the app maps it to CSS custom properties
  -- with light/dark variants: 'sky' | 'rose' | 'moss' | 'amber'
  color text not null default 'sky' check (color in ('sky','rose','moss','amber'))
);

create table if not exists public.favorites (
  user_id uuid not null references auth.users(id) on delete cascade,
  story_id text not null,
  created_at timestamptz not null default now(),
  primary key (user_id, story_id)
);

alter table public.profiles enable row level security;
alter table public.favorites enable row level security;

create policy "profiles readable by everyone" on public.profiles
  for select using (true);
create policy "favorites readable by everyone" on public.favorites
  for select using (true);
create policy "insert own favorites" on public.favorites
  for insert with check (auth.uid() = user_id);
create policy "delete own favorites" on public.favorites
  for delete using (auth.uid() = user_id);

-- Profile rows: adjust display names/colors after confirming spellings.
-- Look up ids first:   select id, email from auth.users;
-- insert into public.profiles (id, display_name, color) values
--   ('<darrin-uuid>', 'Darrin', 'sky'),
--   ('<chet-uuid>',   'Chet',   'moss'),
--   ('<brant-uuid>',  'Brant',  'amber');
