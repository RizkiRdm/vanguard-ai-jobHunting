-- Lock down the SQL API surface.
--
-- Public functions are executable by PUBLIC (which includes anon and
-- authenticated) unless revoked. The API and worker call these functions over an
-- authenticated service-role connection, so no browser role needs EXECUTE.
-- Attacker-relevant examples if left open: reserve_llm_tokens(p_user => <other
-- user>) would spend someone else's budget, and claim_task would let anonymous
-- callers compete for queued work.

revoke all on function public.claim_task(text, integer) from public;
revoke all on function public.heartbeat_task(uuid, text, integer) from public;
revoke all on function public.finish_task(uuid, text, text, jsonb, text) from public;
revoke all on function public.reclaim_expired_tasks() from public;
revoke all on function public.retry_task(uuid, text, text, integer) from public;
revoke all on function public.request_approval(uuid, text, text, jsonb) from public;
revoke all on function public.resume_task(uuid, uuid, jsonb) from public;
revoke all on function public.approve_task(uuid, uuid, text) from public;
revoke all on function public.cancel_task(uuid, uuid) from public;
revoke all on function public.consume_rate_limit(text, integer, integer) from public;
revoke all on function public.reserve_llm_tokens(uuid, integer, bigint) from public;
revoke all on function public.settle_llm_tokens(uuid, integer, integer) from public;
revoke all on function public.set_updated_at() from public;

-- Trigger functions run as the table owner; nothing should call them directly.
do $$
begin
  if to_regprocedure('public.handle_new_auth_user()') is not null then
    revoke all on function public.handle_new_auth_user() from public;
  end if;
end;
$$;

grant execute on function public.claim_task(text, integer) to service_role;
grant execute on function public.heartbeat_task(uuid, text, integer) to service_role;
grant execute on function public.finish_task(uuid, text, text, jsonb, text) to service_role;
grant execute on function public.reclaim_expired_tasks() to service_role;
grant execute on function public.retry_task(uuid, text, text, integer) to service_role;
grant execute on function public.request_approval(uuid, text, text, jsonb) to service_role;
grant execute on function public.resume_task(uuid, uuid, jsonb) to service_role;
grant execute on function public.approve_task(uuid, uuid, text) to service_role;
grant execute on function public.cancel_task(uuid, uuid) to service_role;
grant execute on function public.consume_rate_limit(text, integer, integer) to service_role;
grant execute on function public.reserve_llm_tokens(uuid, integer, bigint) to service_role;
grant execute on function public.settle_llm_tokens(uuid, integer, integer) to service_role;
