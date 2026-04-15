export type LoginRequest = {
  email: string;
  password: string;
};

export type RegisterRequest = {
  email: string;
  username: string;
  password: string;
};

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type?: string;
};

export type AuthenticatedUserResponse = {
  id: string;
  email: string;
  username: string;
  is_active?: boolean;
  is_verified?: boolean;
  is_superuser?: boolean;
};