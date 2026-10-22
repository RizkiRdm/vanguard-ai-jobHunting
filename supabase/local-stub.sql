-- Local stand-in for the Supabase-managed schemas, so migrations and the SQL
-- functions can be verified against a plain Postgres instance. Never applied to
-- a real Supabase project, which already provides these objects.
create schema if not exists auth;
create table if not exists auth.users (id uuid primary key, email text);
create or replace function auth.uid() returns uuid
language sql stable as
$$ select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid $$;

-- Supabase roles referenced by grants and RLS policies.
do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'anon') then
    create role anon nologin;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'authenticated') then
    create role authenticated nologin;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'service_role') then
    create role service_role nologin bypassrls;
  end if;
end;
$$;

create schema if not exists storage;
create table if not exists storage.buckets (
  id text primary key,
  name text not null,
  public boolean default false,
  file_size_limit bigint,
  allowed_mime_types text[]
);
create table if not exists storage.objects (
  id uuid primary key default gen_random_uuid(),
  bucket_id text references storage.buckets (id),
  name text not null,
  owner uuid
);
create or replace function storage.foldername(name text) returns text[]
language sql immutable as
$$ select string_to_array(name, '/') $$;
