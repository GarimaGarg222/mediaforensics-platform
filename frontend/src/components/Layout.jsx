import { NavLink, useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

const NAV = [
  { to: "/",        icon: "⬡",  label: "Analyze"  },
  { to: "/history", icon: "◫",  label: "History"  },
  { to: "/reports", icon: "◈",  label: "Reports"  },
  { to: "/models",  icon: "◉",  label: "Models"   },
]

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => { logout(); navigate("/login") }

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-56 flex-shrink-0 flex flex-col border-r border-surface-800 bg-surface-950/80 backdrop-blur">
        {/* Logo */}
        <div className="px-5 py-5 border-b border-surface-800">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-brand-500/20 flex items-center justify-center text-brand-400 text-lg">🛡</div>
            <div>
              <div className="font-display text-sm font-bold text-surface-50 leading-none">MediaForensics</div>
              <div className="text-[10px] text-surface-500 mt-0.5">AI Detection Platform</div>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV.map(({ to, icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `nav-link ${isActive ? "active" : ""}`
              }
            >
              <span className="text-base w-5 text-center">{icon}</span>
              {label}
            </NavLink>
          ))}
        </nav>

        {/* User */}
        <div className="px-3 py-4 border-t border-surface-800">
          {user ? (
            <div className="flex items-center gap-2.5 px-3 py-2">
              <div className="w-7 h-7 rounded-full bg-brand-500/20 flex items-center justify-center text-brand-400 text-xs font-bold">
                {user.email?.[0]?.toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-medium text-surface-200 truncate">{user.full_name || user.email}</div>
              </div>
              <button onClick={handleLogout} className="text-surface-500 hover:text-surface-300 text-xs">→</button>
            </div>
          ) : (
            <NavLink to="/login" className="nav-link">
              <span>→</span> Login
            </NavLink>
          )}
          <div className="flex items-center gap-1.5 px-3 mt-2">
            <div className="w-1.5 h-1.5 rounded-full bg-brand-400 animate-pulse-slow"></div>
            <span className="text-[10px] text-surface-500">3 models active</span>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  )
}
