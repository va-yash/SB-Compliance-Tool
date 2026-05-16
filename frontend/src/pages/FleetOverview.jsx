import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api.js'

function trafficLight(ac) {
  if (ac.ad_open > 0) return { color: 'red', label: 'AD Open' }
  if (ac.open_sbs > 0 || ac.due_soon_count > 0) return { color: 'amber', label: ac.due_soon_count > 0 ? 'Due Soon' : 'Open SBs' }
  return { color: 'green', label: 'Compliant' }
}

export default function FleetOverview() {
  const [fleet, setFleet] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    api.listAircraft()
      .then(setFleet)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="page-loading">Loading fleet data…</div>
  if (error)   return <div className="page-error">Error: {error}</div>

  const totalOpen    = fleet.reduce((s, a) => s + a.open_sbs, 0)
  const totalAdOpen  = fleet.reduce((s, a) => s + a.ad_open, 0)
  const totalDueSoon = fleet.reduce((s, a) => s + a.due_soon_count, 0)

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Fleet Overview</h1>
        <div className="fleet-stats">
          <div className="stat-card">
            <span className="stat-value">{fleet.length}</span>
            <span className="stat-label">Aircraft</span>
          </div>
          <div className="stat-card stat-card--danger">
            <span className="stat-value">{totalAdOpen}</span>
            <span className="stat-label">AD Open</span>
          </div>
          <div className="stat-card stat-card--warning">
            <span className="stat-value">{totalDueSoon}</span>
            <span className="stat-label">Due Soon</span>
          </div>
          <div className="stat-card stat-card--info">
            <span className="stat-value">{totalOpen}</span>
            <span className="stat-label">Open SBs</span>
          </div>
        </div>
      </div>

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Status</th>
              <th>MSN</th>
              <th>Registration</th>
              <th>Operator</th>
              <th>Type</th>
              <th className="text-right">Open SBs</th>
              <th className="text-right">AD Open</th>
              <th className="text-right">Due Soon</th>
              <th>Delivery</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {fleet.map(ac => {
              const tl = trafficLight(ac)
              return (
                <tr key={ac.msn} className="table-row-hover" onClick={() => navigate(`/aircraft/${ac.msn}`)}>
                  <td>
                    <span className={`traffic-light traffic-light--${tl.color}`} title={tl.label} />
                  </td>
                  <td><span className="mono">{ac.msn}</span></td>
                  <td><strong>{ac.registration}</strong></td>
                  <td className="text-secondary">{ac.operator}</td>
                  <td className="text-secondary">{ac.type_variant}</td>
                  <td className="text-right">
                    {ac.open_sbs > 0
                      ? <span className="badge badge--blue">{ac.open_sbs}</span>
                      : <span className="text-muted">—</span>}
                  </td>
                  <td className="text-right">
                    {ac.ad_open > 0
                      ? <span className="badge badge--red">{ac.ad_open}</span>
                      : <span className="text-muted">—</span>}
                  </td>
                  <td className="text-right">
                    {ac.due_soon_count > 0
                      ? <span className="badge badge--amber">{ac.due_soon_count}</span>
                      : <span className="text-muted">—</span>}
                  </td>
                  <td className="text-secondary">{ac.delivery_date || '—'}</td>
                  <td>
                    <button className="btn btn-sm btn-secondary"
                      onClick={e => { e.stopPropagation(); navigate(`/aircraft/${ac.msn}`) }}>
                      View →
                    </button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
