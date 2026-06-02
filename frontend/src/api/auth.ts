import { apiFetch } from "./_base";

// Frontend copy of the user object returned by the Flask auth endpoints.
export interface User {
  id: string;
  fullName: string;
  email: string;
  dateOfBirth: string;
  membershipId: string;
  memberSince: string;
  isUnder18: boolean;
}



// Read the signed-in user from localStorage.
// The window check keeps this safe outside the browser.

// Store or clear the current user in localStorage.

// Create a new account and immediately cache the returned user locally.
export async function signUp(input: {
  fullName: string;
  email: string;
  password: string;
  dateOfBirth: string;
}): Promise<User> {
  const user = await apiFetch<User>(
    "/auth/signup",
    { method: "POST", body: JSON.stringify(input) },
  );
  writeUser(user);
  return user;
}

// Sign-in step 1: send credentials and let the backend decide whether 2FA is required.
export async function signIn(input: {
  emailOrId: string;
  password: string;
}): Promise<{ requires2FA: boolean; email?: string }> {
  return apiFetch<{ requires2FA: boolean; email?: string }>(
    "/auth/signin",
    { method: "POST", body: JSON.stringify(input) },
  );
}

// Sign-in step 2: verify the emailed code, then cache the verified user.
export async function verify2FA(input: {
  email: string;
  code: string;
}): Promise<User> {
  const user = await apiFetch<User>(
    "/auth/verify-2fa",
    { method: "POST", body: JSON.stringify(input) },
  );
  writeUser(user);
  return user;
}

// Local sign-out only clears the browser copy of the current user.
export async function signOut() {
  writeUser(null);
}

// Pages and layouts use this to decide whether to show signed-in navigation.
export function getCurrentUser(): User | null {
  return readUser();
}

// Replace the stored user after an endpoint returns fresher account data.
export function updateCurrentUser(user: User) {
  writeUser(user);
}
