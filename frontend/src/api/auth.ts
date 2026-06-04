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

const USER_KEY = "thecall.user"


// user stored in localStorage (not sensitive)
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
  dateOfBirth: string;
}): Promise<User> {
  const user = await apiFetch<User>(
    "/auth/signup",
    { method: "POST", body: JSON.stringify(input) },
  );
  // cookies set by Flask automatically
  // just save user info to localStorage
  saveUser(user);
  return user;
}

// Sign-in step 1: send credentials and let the backend decide whether 2FA is required.
export async function signIn(input: {
  emailOrId: string;
  password: string;
}): Promise<{ requires2FA: boolean; email: string }> {
  return apiFetch<{ requires2FA: boolean; email: string }>(
    "/auth/signin",
    { method: "POST", body: JSON.stringify(input) },
  );
}

// Sign-in step 2: verify the emailed code, then cache the verified user.
export async function verify2FA(input: {
  email: string;
  otp_code: string;
}): Promise<User> {
  const user = await apiFetch<User>(
    "/auth/verify-2fa",
    { method: "POST", body: JSON.stringify(input) },
  );
  saveUser(user);
  return user;
}


// resend OTP
export async function resendOtp(email:string): Promise<void> {
  return apiFetch<void>(
    "/auth/resend-otp",
    {method: "POST", body: JSON.stringify({email}) },
  );
}
// sign out


export async function signOut(): Promise<void> {
  try{
    await apiFetch<void>("/auth/logout", {method: "POST"});
  } finally {
    clearUser();   // clear user from localStorage

    // cookies cleared by Flask response
  }
}