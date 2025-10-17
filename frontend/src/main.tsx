import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./lib/queryClient";
import "./styles.css";
import App from "./App";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import ResetPassword from "./pages/ResetPassword";
import Profile from "./pages/Profile";
import UsersTable from "./pages/UsersTable";
import Stats from "./pages/Stats";
import { useAuthStore } from "./auth/store";
import ExcelImport from "./pages/ExcelImport";
import ChangePassword from "./pages/ChangePassword";

function PrivateRoute({ children }: { children: JSX.Element }) {
  const token = useAuthStore((s) => s.accessToken);
  return token ? children : <Navigate to="/login" replace />;
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
            <Route path="/" element={<App />}> 
            <Route index element={<Navigate to="/users" replace />} />
            <Route path="login" element={<Login />} />
            <Route path="signup" element={<Signup />} />
            <Route path="reset-password" element={<ResetPassword />} />
            <Route path="profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
            <Route path="users" element={<PrivateRoute><UsersTable /></PrivateRoute>} />
            <Route path="stats" element={<PrivateRoute><Stats /></PrivateRoute>} />
            <Route path="import-excel" element={<ExcelImport />} />
            <Route path="/users/:id/change-password" element={<ChangePassword />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);
