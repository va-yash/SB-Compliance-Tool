import { NavLink } from 'react-router-dom'

export default function Nav() {
  return (
    <nav className="nav">
      <div className="nav-brand">
        <span className="nav-icon">✈</span>
        <span className="nav-title">SB Compliance Tool</span>
        <span className="nav-sub">A320 Fleet</span>
      </div>
      <div className="nav-links">
        <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          Fleet Overview
        </NavLink>
        <NavLink to="/applicability" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          SB Applicability Checker
        </NavLink>
      </div>
    </nav>
  )
}
