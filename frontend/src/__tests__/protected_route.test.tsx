import { MemoryRouter, Route, Routes } from "react-router-dom";
import { render, screen } from "@testing-library/react";
import ProtectedRoute from "../auth/ProtectedRoute";
import { useAuthStore } from "../auth/store";

vi.mock("jwt-decode", () => ({ jwtDecode: () => ({ exp: Math.floor(Date.now()/1000)+60 }) }));

function Login() { return <div>Login Page</div>; }
function Secret() { return <div>Secret Page</div>; }

describe("ProtectedRoute", () => {
  it("redirects to /login when no token", async () => {
    // Clear any auth
    useAuthStore.setState({ access: null, refresh: null, me: null, setTokens: () => {}, signOut: () => {} } as any);

    render(
      <MemoryRouter initialEntries={["/secret"]}>
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/secret" element={<Secret />} />
          </Route>
          <Route path="/login" element={<Login />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText(/login page/i)).toBeInTheDocument();
  });
});
