import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuthStore } from "../auth/store";
type Props = { children: React.ReactNode };
import { shallow } from "zustand/shallow";

export default function RequireAuth({ children }: Props) {
  const location = useLocation();
  const { user, accessToken, refreshToken } = useAuthStore(
    (s) => ({
      user: s.user,
      accessToken: s.accessToken,
      refreshToken: s.refreshToken,
    }),
    shallow
  );
  const isAuthenticated = Boolean(user || accessToken);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  return <>{children}</>;
}
