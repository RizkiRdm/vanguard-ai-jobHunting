-- Vanguard core schema.
-- Targets Supabase Postgres. Objects that only exist on Supabase (auth.users,
-- storage.buckets) are guarded so the migration also runs on plain Postgres.

create extension if not exists pgcrypto;

create table if not exists public.users (
  id uuid primary key references auth.users (id) on delete cascade,
  email text,
  version integer not null default 1,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.user_profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references public.users (id) on delete cascade,
  full_name text,
  email text,
  phone text,
  summary text,
  target_role text,
  expected_salary text,
  skills text[] not null default '{}',
  experience_years integer,
  location text,
  resume_path text,
  resume_filename text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.tasks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users (id) on delete cascade,
  parent_id uuid references public.tasks (id) on delete cascade,
  type text not null check (type in ('discover', 'apply')),
  status text not null default 'queued'
    check (status in ('queued', 'running', 'waiting_for_user', 'succeeded', 'failed', 'cancelled')),
  payload jsonb not null default '{}'::jsonb,
  result jsonb,
  error text,
  approval jsonb,
  attempts integer not null default 0,
  max_attempts integer not null default 3,
  worker_id text,
  lease_expires_at timestamptz,
  heartbeat_at timestamptz,
  next_run_at timestamptz not null default now(),
  started_at timestamptz,
  finished_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists tasks_claimable_idx on public.tasks (status, next_run_at, created_at);
create index if not exists tasks_user_idx on public.tasks (user_id, created_at desc);
create index if not exists tasks_parent_idx on public.tasks (parent_id);

create table if not exists public.jobs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users (id) on delete cascade,
  task_id uuid references public.tasks (id) on delete set null,
  source_url text not null,
  title text not null,
  company text,
  location text,
  description text,
  created_at timestamptz not null default now()
);

create index if not exists jobs_user_idx on public.jobs (user_id, created_at desc);

create table if not exists public.documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users (id) on delete cascade,
  task_id uuid references public.tasks (id) on delete cascade,
  doc_type text not null,
  content text not null,
  token_cost integer not null default 0,
  created_at timestamptz not null default now()
);

create index if not exists documents_user_idx on public.documents (user_id, created_at desc);

-- Audit trail of every AI call.
create table if not exists public.llm_usage_log (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references public.users (id) on delete cascade,
  model text not null,
  prompt_tokens integer not null default 0,
  completion_tokens integer not null default 0,
  total_tokens integer not null default 0,
  created_at timestamptz not null default now()
);

create index if not exists llm_usage_user_idx on public.llm_usage_log (user_id, created_at desc);

-- Daily token budget. `used_tokens` is the reserved+spent amount for `budget_day`.
create table if not exists public.budget_counters (
  user_id uuid primary key references public.users (id) on delete cascade,
  used_tokens bigint not null default 0,
  budget_day date not null default current_date,
  updated_at timestamptz not null default now()
);

create table if not exists public.rate_limits (
  key text primary key,
  window_start timestamptz not null default now(),
  count integer not null default 0
);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

do $$
declare
  t text;
begin
  foreach t in array array['users', 'user_profiles', 'tasks'] loop
    execute format(
      'drop trigger if exists set_updated_at_%1$s on public.%1$I', t
    );
    execute format(
      'create trigger set_updated_at_%1$s before update on public.%1$I
         for each row execute function public.set_updated_at()', t
    );
  end loop;
end;
$$;

-- Mirror Supabase Auth users into public.users so every owned resource has a
-- parent row to reference.
do $$
begin
  if to_regclass('auth.users') is null then
    return;
  end if;

  execute '
    create or replace function public.handle_new_auth_user()
    returns trigger language plpgsql security definer set search_path = public as $fn$
    begin
      insert into public.users (id, email) values (new.id, new.email)
        on conflict (id) do nothing;
      insert into public.budget_counters (user_id) values (new.id)
        on conflict (user_id) do nothing;
      return new;
    end;
    $fn$';

  execute 'drop trigger if exists on_auth_user_created on auth.users';
  execute '
    create trigger on_auth_user_created
    after insert on auth.users
    for each row execute function public.handle_new_auth_user()';
end;
$$;

-- Private bucket for resumes. Public URLs are never used.
do $$
begin
  if to_regclass('storage.buckets') is null then
    return;
  end if;

  insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
  values ('resumes', 'resumes', false, 10485760, array['application/pdf'])
  on conflict (id) do nothing;
end;
$$;
