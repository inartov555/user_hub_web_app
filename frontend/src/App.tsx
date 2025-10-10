import { BrowserRouter, Route, Routes, Navigate, Link } from 'react-router-dom';
import Login from './pages/Login';
import Signup from './pages/Signup';
import ResetPassword from './pages/ResetPassword';
import Profile from './pages/Profile';
import Users from './pages/Users';
import Stats from './pages/Stats';

const Private = ({ children }: { children: JSX.Element }) => {
  const authed = !!localStorage.getItem('access');
  return authed ? children : <Navigate to="/login"/>;
};

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 text-slate-800">
        <header className="px-6 py-3 sticky top-0 backdrop-blur border-b bg-white/70 flex gap-4">
          <Link to="/users" className="font-semibold">Users</Link>
          <Link to="/stats">Stats</Link>
          <Link to="/profile">Profile</Link>
        </header>
        <main className="max-w-6xl mx-auto py-8">
          <Routes>
            <Route path="/login" element={<Login/>} />
            <Route path="/signup" element={<Signup/>} />
            <Route path="/reset" element={<ResetPassword/>} />

            <Route path="/users" element={<Private><Users/></Private>} />
            <Route path="/stats" element={<Private><Stats/></Private>} />
            <Route path="/profile" element={<Private><Profile/></Private>} />
            <Route path="*" element={<Navigate to="/users" />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
