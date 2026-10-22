export interface AuthUser {
  id: string;
  email: string | null;
}

export interface AppEnv {
  Variables: {
    user: AuthUser;
    requestId: string;
  };
}
