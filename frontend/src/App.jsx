import { Routes, Route, Link, Navigate, useNavigate } from 'react-router-dom'
import Login from './pages/Login.jsx'
import Signup from './pages/Signup.jsx'
import Profile from './pages/Profile.jsx'
import ResetPassword from './pages/ResetPassword.jsx'
import Users from './pages/Users.jsx'
import Stats from './pages/Stats.jsx'

const isAuthed = () => !!localStorage.getItem('token')

const Nav = () => {
  const navigate = useNavigate()
  const logout = () => { localStorage.removeItem('token'); localStorage.removeItem('refresh'); navigate('/login') }
  return (
    <header className="bg-white/70 backdrop-blur sticky top-0 z-10 border-b">
      <div className="max-w-6xl mx-auto p-4 flex items-center gap-4">
        <Link to="/" className="font-bold text-xl">UserHub</Link>
        <nav className="flex gap-4">
          {isAuthed() && <Link className="link" to="/users">Users</Link>}
          {isAuthed() && <Link className="link" to="/stats">Stats</Link>}
          {isAuthed() && <Link className="link" to="/profile">Profile</Link>}
          {!isAuthed() && <Link className="link" to="/login">Login</Link>}
          {!isAuthed() && <Link className="link" to="/signup">Signup</Link>}
          {isAuthed() && <button className="link" onClick={logout}>Logout</button>}
        </nav>
      </div>
    </header>
  )
}

const Protected = ({ children }) => isAuthed() ? children : <Navigate to="/login" replace />

export default function App() {
  return (
    <div>
      <Nav />
      <main className="page">
        <Routes>
          <Route path="/" element={isAuthed() ? <Navigate to="/users" /> : <Navigate to="/login" />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/reset-password" element={<Protected><ResetPassword /></Protected>} />
          <Route path="/profile" element={<Protected><Profile /></Protected>} />
          <Route path="/users" element={<Protected><Users /></Protected>} />
          <Route path="/stats" element={<Protected><Stats /></Protected>} />
        </Routes>
      </main>
    </div>
  )
}
