-- The auth mirror trigger function is SECURITY DEFINER, so it must not be
-- callable through /rest/v1/rpc by client roles.

revoke all on function public.handle_new_auth_user() from anon, authenticated, public;
