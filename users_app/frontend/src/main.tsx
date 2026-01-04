import "./lib/i18n";
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import "./styles.css";
import { queryClient } from "./lib/queryClient";
import ProtectedRoute from "./auth/ProtectedRoute";
import App from "./App";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import ResetPassword from "./pages/ResetPassword";
import ProfileEdit from "./pages/ProfileEdit";
import ProfileView from "./pages/ProfileView";
import UsersTable from "./pages/UsersTable";
import Stats from "./pages/Stats";
import { useAuthStore } from "./auth/store";
import ExcelImport from "./pages/ExcelImport";
import ChangePassword from "./pages/ChangePassword";
import UserDeleteConfirm from "./pages/UserDeleteConfirm";
import Settings from "./pages/Settings";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* App layout wrapper */}
          <Route path="/" element={<App />}>
            {/* Public routes */}
            <Route path="login" element={<Login />} />
            <Route path="signup" element={<Signup />} />
            <Route path="reset-password" element={<ResetPassword />} />
            {/* Protected routes */}
            <Route element={<ProtectedRoute />}>
              <Route index element={<Navigate to="/users" replace />} />
              <Route path="profile-edit" element={<ProfileEdit />} />
              <Route path="profile-view" element={<ProfileView />} />
              <Route path="users" element={<UsersTable />} />
              <Route path="stats" element={<Stats />} />
              <Route path="import-excel" element={<ExcelImport />} />
              <Route path="/users/:id/change-password" element={<ChangePassword />} />
              <Route path="/users/confirm-delete" element={<UserDeleteConfirm />} />
              <Route path="settings" element={<Settings />} />
            </Route>
            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);
