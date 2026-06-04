// src/api/auth.ts
import { apiFetch } from "./_base";

export interface User {
  id: string;
  fullName: string;
  email: string;
  dateOfBirth: string;
  membershipId: string;
  memberSince: string;
  isUnder18: boolean;
}

const USER_KEY = "thecall.user";

// get user stored in localStorage (not sensitive) 
// only JWT tokens go in HTTP-only cookies
function saveUser(user: User) {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

function clearUser() {
  localStorage.removeItem(USER_KEY);
}

export function getCurrentUser(): User | null {
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? (JSON.parse(raw) as User) : null;
  } catch {
    return null;
  }
}

// sign up
export async function signUp(input: {
  fname: string;
  lname: string;
  email: string;
  password: string;
  phone_number: string;
  date_of_birth: string;
}): Promise<User> {
  const user = await apiFetch<User>(
    "/auth/signup",
    { method: "POST", body: JSON.stringify(input) },
  );
  
  saveUser(user);
  return user;
}

// sign in step 1 
export async function signIn(input: {
  emailOrId: string;
  password: string;
}): Promise<{ requires2FA: boolean; email: string }> {
  return apiFetch<{ requires2FA: boolean; email: string }>(
    "/auth/signin",
    { method: "POST", body: JSON.stringify(input) },
  );
}

// sign in step 2 — verify OTP
export async function verify2FA(input: {
  email: string;
  otp_code: string;
}): Promise<User> {
  const user = await apiFetch<User>(
    "/auth/verify",
    { method: "POST", body: JSON.stringify(input) },
  );
  // cookies set by Flask
  // save user info to localStorage
  saveUser(user);
  return user;
}

// resend OTP 
export async function resendOtp(email: string): Promise<void> {
  return apiFetch<void>(
    "/auth/resend-otp",
    { method: "POST", body: JSON.stringify({ email }) },
  );
}

//  sign out 
export async function signOut(): Promise<void> {
  try {
    await apiFetch<void>("/auth/logout", { method: "POST" });
  } finally {
    clearUser();                    // ← clear user from localStorage
    // cookies cleared by Flask response
  }
}