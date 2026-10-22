-- Hardening found by the security advisor after the first deploy.
--
-- 1. Supabase grants EXECUTE on new public functions to anon/authenticated via
--    default privileges, so `revoke ... from public` alone is not enough. These
--    functions are an internal API called by the server over the service role.
-- 2. Pin search_path on every function (advisor: function_search_path_mutable).
-- 3. rate_limits is service-only; an explicit policy documents the denial.

revoke all on function public.claim_task(text, integer) from anon, authenticated;
revoke all on function public.heartbeat_task(uuid, text, integer) from anon, authenticated;
revoke all on function public.finish_task(uuid, text, text, jsonb, text) from anon, authenticated;
revoke all on function public.reclaim_expired_tasks() from anon, authenticated;
revoke all on function public.retry_task(uuid, text, text, integer) from anon, authenticated;
revoke all on function public.request_approval(uuid, text, text, jsonb) from anon, authenticated;
revoke all on function public.resume_task(uuid, uuid, jsonb) from anon, authenticated;
revoke all on function public.approve_task(uuid, uuid, text) from anon, authenticated;
revoke all on function public.cancel_task(uuid, uuid) from anon, authenticated;
revoke all on function public.consume_rate_limit(text, integer, integer) from anon, authenticated;
revoke all on function public.reserve_llm_tokens(uuid, integer, bigint) from anon, authenticated;
revoke all on function public.settle_llm_tokens(uuid, integer, integer) from anon, authenticated;
revoke all on function public.set_updated_at() from anon, authenticated;

alter function public.claim_task(text, integer) set search_path = '';
alter function public.heartbeat_task(uuid, text, integer) set search_path = '';
alter function public.finish_task(uuid, text, text, jsonb, text) set search_path = '';
alter function public.reclaim_expired_tasks() set search_path = '';
alter function public.retry_task(uuid, text, text, integer) set search_path = '';
alter function public.request_approval(uuid, text, text, jsonb) set search_path = '';
alter function public.resume_task(uuid, uuid, jsonb) set search_path = '';
alter function public.approve_task(uuid, uuid, text) set search_path = '';
alter function public.cancel_task(uuid, uuid) set search_path = '';
alter function public.consume_rate_limit(text, integer, integer) set search_path = '';
alter function public.reserve_llm_tokens(uuid, integer, bigint) set search_path = '';
alter function public.settle_llm_tokens(uuid, integer, integer) set search_path = '';
alter function public.set_updated_at() set search_path = '';

alter table public.rate_limits enable row level security;
drop policy if exists rate_limits_service_only on public.rate_limits;
create policy rate_limits_service_only on public.rate_limits for all to service_role
  using (true) with check (true);
