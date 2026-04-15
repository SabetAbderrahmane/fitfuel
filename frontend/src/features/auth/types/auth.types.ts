export type LoginRequest = {
  email: string;
  password: string;
};

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
};

export type AuthenticatedUserResponse = {
  id: string;
  email: string;
  is_active?: boolean;
  is_verified?: boolean;
};