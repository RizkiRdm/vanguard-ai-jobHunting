-- Row Level Security for user-owned tables.
--
-- Defense in depth: the API uses the service-role client (which bypasses RLS),
-- so every API route must also check ownership in code. These policies protect
-- direct PostgREST access with a user JWT, and keep the anon key harmless.
--
-- Only applied when the Supabase helper `auth.uid()` exists.

do $$
begin
  if to_regprocedure('auth.uid()') is null then
    raise notice 'auth.uid() unavailable - skipping RLS policies';
    return;
  end if;

  execute 'alter table public.users enable row level security';
  execute 'alter table public.user_profiles enable row level security';
  execute 'alter table public.tasks enable row level security';
  execute 'alter table public.jobs enable row level security';
  execute 'alter table public.documents enable row level security';
  execute 'alter table public.llm_usage_log enable row level security';
  execute 'alter table public.budget_counters enable row level security';

  execute 'drop policy if exists users_own on public.users';
  execute 'create policy users_own on public.users for all using (id = auth.uid()) with check (id = auth.uid())';

  execute 'drop policy if exists user_profiles_own on public.user_profiles';
  execute 'create policy user_profiles_own on public.user_profiles for all using (user_id = auth.uid()) with check (user_id = auth.uid())';

  execute 'drop policy if exists tasks_own on public.tasks';
  execute 'create policy tasks_own on public.tasks for all using (user_id = auth.uid()) with check (user_id = auth.uid())';

  execute 'drop policy if exists jobs_own on public.jobs';
  execute 'create policy jobs_own on public.jobs for all using (user_id = auth.uid()) with check (user_id = auth.uid())';

  execute 'drop policy if exists documents_own on public.documents';
  execute 'create policy documents_own on public.documents for all using (user_id = auth.uid()) with check (user_id = auth.uid())';

  execute 'drop policy if exists llm_usage_log_own on public.llm_usage_log';
  execute 'create policy llm_usage_log_own on public.llm_usage_log for select using (user_id = auth.uid())';

  execute 'drop policy if exists budget_counters_own on public.budget_counters';
  execute 'create policy budget_counters_own on public.budget_counters for select using (user_id = auth.uid())';
end;
$$;

-- Storage objects for resumes are readable only by the owning user.
do $$
begin
  if to_regclass('storage.objects') is null then
    return;
  end if;

  execute 'drop policy if exists resumes_own on storage.objects';
  execute 'create policy resumes_own on storage.objects for all
    using (bucket_id = ''resumes'' and (storage.foldername(name))[1] = auth.uid()::text)
    with check (bucket_id = ''resumes'' and (storage.foldername(name))[1] = auth.uid()::text)';
end;
$$;
