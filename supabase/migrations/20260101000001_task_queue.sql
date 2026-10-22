-- Durable task queue primitives.
--
-- The worker claims a task with `claim_task`, which uses `FOR UPDATE SKIP LOCKED`
-- so two workers can never own the same row. Leases let abandoned tasks be
-- recovered instead of staying `running` forever.

create or replace function public.claim_task(p_worker text, p_lease_seconds integer)
returns setof public.tasks
language plpgsql
as $$
declare
  v_task public.tasks;
begin
  select *
    into v_task
    from public.tasks
   where status = 'queued'
     and next_run_at <= now()
   order by created_at
   for update skip locked
   limit 1;

  if v_task.id is null then
    return;
  end if;

  update public.tasks
     set status = 'running',
         worker_id = p_worker,
         attempts = attempts + 1,
         started_at = coalesce(started_at, now()),
         heartbeat_at = now(),
         lease_expires_at = now() + make_interval(secs => p_lease_seconds),
         finished_at = null,
         updated_at = now()
   where id = v_task.id
   returning * into v_task;

  return next v_task;
end;
$$;

create or replace function public.heartbeat_task(
  p_task uuid,
  p_worker text,
  p_lease_seconds integer
)
returns boolean
language plpgsql
as $$
begin
  update public.tasks
     set heartbeat_at = now(),
         lease_expires_at = now() + make_interval(secs => p_lease_seconds),
         updated_at = now()
   where id = p_task
     and worker_id = p_worker
     and status = 'running';
  return found;
end;
$$;

-- Finishes (or parks) a task. Only the worker that owns the lease may call this.
create or replace function public.finish_task(
  p_task uuid,
  p_worker text,
  p_status text,
  p_result jsonb default null,
  p_error text default null
)
returns boolean
language plpgsql
as $$
begin
  update public.tasks
     set status = p_status,
         result = coalesce(p_result, result),
         error = p_error,
         worker_id = null,
         lease_expires_at = null,
         heartbeat_at = null,
         finished_at = case when p_status in ('succeeded', 'failed', 'cancelled')
                          then now() else null end,
         updated_at = now()
   where id = p_task
     and worker_id = p_worker
     and status = 'running';
  return found;
end;
$$;

-- Returns abandoned `running` tasks to the queue (or fails them when out of attempts).
create or replace function public.reclaim_expired_tasks()
returns integer
language plpgsql
as $$
declare
  v_count integer;
begin
  with expired as (
    select id
      from public.tasks
     where status = 'running'
       and lease_expires_at is not null
       and lease_expires_at < now()
     for update skip locked
  ),
  requeued as (
    update public.tasks t
       set status = 'queued',
           worker_id = null,
           lease_expires_at = null,
           heartbeat_at = null,
           error = coalesce(t.error, 'Worker lease expired; task requeued.'),
           next_run_at = now() + make_interval(secs => least(60, 5 * t.attempts)),
           updated_at = now()
      from expired e
     where t.id = e.id
       and t.attempts < t.max_attempts
    returning t.id
  ),
  failed as (
    update public.tasks t
       set status = 'failed',
           worker_id = null,
           lease_expires_at = null,
           heartbeat_at = null,
           error = coalesce(t.error, 'Worker lease expired and retry limit reached.'),
           finished_at = now(),
           updated_at = now()
      from expired e
     where t.id = e.id
       and t.attempts >= t.max_attempts
    returning t.id
  )
  select count(*) into v_count from requeued;

  return v_count;
end;
$$;

-- Fails a task, or re-queues it with backoff when attempts remain.
create or replace function public.retry_task(
  p_task uuid,
  p_worker text,
  p_error text,
  p_backoff_seconds integer
)
returns boolean
language plpgsql
as $$
declare
  v_attempts integer;
begin
  select attempts into v_attempts from public.tasks where id = p_task and worker_id = p_worker;
  if v_attempts is null then
    return false;
  end if;

  if v_attempts < (select max_attempts from public.tasks where id = p_task) then
    update public.tasks
       set status = 'queued',
           error = p_error,
           worker_id = null,
           lease_expires_at = null,
           heartbeat_at = null,
           next_run_at = now() + make_interval(secs => p_backoff_seconds),
           updated_at = now()
     where id = p_task and worker_id = p_worker;
  else
    update public.tasks
       set status = 'failed',
           error = p_error,
           worker_id = null,
           lease_expires_at = null,
           heartbeat_at = null,
           finished_at = now(),
           updated_at = now()
     where id = p_task and worker_id = p_worker;
  end if;

  return true;
end;
$$;

-- Parks a task that needs an explicit human decision, and stores what is being asked.
create or replace function public.request_approval(
  p_task uuid,
  p_worker text,
  p_reason text,
  p_details jsonb default '{}'::jsonb
)
returns boolean
language plpgsql
as $$
begin
  update public.tasks
     set status = 'waiting_for_user',
         approval = jsonb_build_object(
           'reason', p_reason,
           'requested_at', now(),
           'details', p_details
         ),
         worker_id = null,
         lease_expires_at = null,
         heartbeat_at = null,
         finished_at = null,
         updated_at = now()
   where id = p_task
     and worker_id = p_worker
     and status = 'running';
  return found;
end;
$$;

-- Re-queues a task that was parked waiting for a human.
create or replace function public.resume_task(p_task uuid, p_user uuid, p_answer jsonb)
returns boolean
language plpgsql
as $$
begin
  update public.tasks
     set status = 'queued',
         payload = payload || jsonb_build_object('user_answer', p_answer),
         approval = null,
         worker_id = null,
         lease_expires_at = null,
         heartbeat_at = null,
         next_run_at = now(),
         updated_at = now()
   where id = p_task
     and user_id = p_user
     and status = 'waiting_for_user';
  return found;
end;
$$;

-- Approves a parked task (explicit user confirmation before a consequential action).
create or replace function public.approve_task(p_task uuid, p_user uuid, p_note text default null)
returns boolean
language plpgsql
as $$
begin
  update public.tasks
     set status = 'queued',
         -- Merge, don't replace: the worker needs details.submit_selector to finish the job.
         approval = coalesce(approval, '{}'::jsonb) || jsonb_build_object('approved_at', now(), 'note', p_note),
         worker_id = null,
         lease_expires_at = null,
         heartbeat_at = null,
         next_run_at = now(),
         updated_at = now()
   where id = p_task
     and user_id = p_user
     and status = 'waiting_for_user';
  return found;
end;
$$;

create or replace function public.cancel_task(p_task uuid, p_user uuid)
returns boolean
language plpgsql
as $$
begin
  update public.tasks
     set status = 'cancelled',
         worker_id = null,
         lease_expires_at = null,
         heartbeat_at = null,
         finished_at = now(),
         updated_at = now()
   where id = p_task
     and user_id = p_user
     and status in ('queued', 'waiting_for_user', 'running');
  return found;
end;
$$;

-- Atomic rate limiter: one upsert decides whether the caller is over budget.
create or replace function public.consume_rate_limit(
  p_key text,
  p_limit integer,
  p_window_seconds integer
)
returns boolean
language sql
as $$
  with upsert as (
    insert into public.rate_limits (key, window_start, count)
    values (p_key, now(), 1)
    on conflict (key) do update
      set count = case
                    when rate_limits.window_start < now() - make_interval(secs => p_window_seconds)
                    then 1
                    else rate_limits.count + 1
                  end,
          window_start = case
                    when rate_limits.window_start < now() - make_interval(secs => p_window_seconds)
                    then now()
                    else rate_limits.window_start
                  end
    returning count
  )
  select count <= p_limit from upsert;
$$;

-- Token budget. A single conditional UPDATE makes the check-and-reserve atomic,
-- so concurrent AI calls cannot overspend the cap.
create or replace function public.reserve_llm_tokens(
  p_user uuid,
  p_amount integer,
  p_cap bigint
)
returns boolean
language plpgsql
as $$
declare
  v_tokens bigint;
begin
  insert into public.budget_counters (user_id, used_tokens, budget_day)
  values (p_user, 0, current_date)
  on conflict (user_id) do nothing;

  update public.budget_counters
     set used_tokens = case
                         when budget_day <> current_date then p_amount
                         else used_tokens + p_amount
                       end,
         budget_day = current_date,
         updated_at = now()
   where user_id = p_user
     and (case when budget_day <> current_date then 0 else used_tokens end) + p_amount <= p_cap
  returning used_tokens into v_tokens;

  return v_tokens is not null;
end;
$$;

create or replace function public.settle_llm_tokens(
  p_user uuid,
  p_reserved integer,
  p_actual integer
)
returns void
language plpgsql
as $$
begin
  update public.budget_counters
     set used_tokens = greatest(0, used_tokens - p_reserved + p_actual),
         updated_at = now()
   where user_id = p_user;
end;
$$;
