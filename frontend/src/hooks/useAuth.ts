import { useMemo } from "react";

const TOKEN_KEYS = ["access_token", "access", "jwt"]; // adjust to your app

export function useAuth() {
  const isAuthenticated = useMemo(() => {
    // simplest check: presence of any known token key in localStorage
    return TOKEN_KEYS.some((k) => !!localStorage.getItem(k));
  }, []);
  return { isAuthenticated };
}
