import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api.js'
import Modal from '../components/Modal.jsx'

// ── Helpers ───────────────────────────────────────────────────────────────────

const STATUS_OPTIONS = [
  'open', 'accomplished', 'deferred', 'not_applicable',
  'superseded', 'post_mod_embodied', 'amoc_applied'
]
const CATEGORY_OPTIONS = ['mandatory', 'recommended', 'optional']
const ATA_OPTIONS = ['05','21','24','25','27','28','29','32','34','52','53','57','71']

function statusBadge(s) {
  const map = {
    open: 'blue', accomplished: 'green', deferred: 'amber',
    not_applicable: 'gray', superseded: 'gray-light',
    post_mod_embodied: 'indigo', amoc_applied: 'teal'
  }
  return <span className={`badge badge--${map[s] || 'gray'}`}>{s.replace(/_/g, ' ')}</span>
}

function categoryBadge(c) {
  const map = { mandatory: 'red', recommended: 'amber', optional: 'gray' }
  return <span className={`badge badge--${map[c] || 'gray'}`}>{c}</span>
}

function groupComponents(components) {
  const groups = { Engines: [], APU: [], 'Landing Gear': [], Avionics: [] }
  for (const c of components) {
    if (c.position.startsWith('Engine')) groups['Engines'].push(c)
    else if (c.position === 'APU') groups['APU'].push(c)
    else if (c.position.startsWith('NLG') || c.position.startsWith('MLG')) groups['Landing Gear'].push(c)
    else groups['Avionics'].push(c)
  }
  return groups
}

const BLANK_SB = {
  sb_number: '', title: '', ata_chapter: '27', category: 'mandatory',
  latest_revision: 'Rev 01', status: 'open', ad_flag: false,
  interval_type: 'one_time', notes: '',
  revision_accomplished: '', accomplishment_date: '', work_order_ref: '',
  deferred_expiry_date: '', deferred_limit_fh: '', deferred_limit_fc: '',
  interval_fh: '', interval_fc: '', interval_days: '',
  next_due_date: '', next_due_fh: '', next_due_fc: '',
}

function toApiPayload(form) {
  const n = v => (v === '' || v === null || v === undefined) ? null : v
  return {
    sb_number: form.sb_number, title: form.title,
    ata_chapter: form.ata_chapter, category: form.category,
    latest_revision: form.latest_revision, status: form.status,
    ad_flag: Boolean(form.ad_flag),
    interval_type: form.interval_type,
    revision_accomplished: n(form.revision_accomplished),
    accomplishment_date: n(form.accomplishment_date),
    work_order_ref: n(form.work_order_ref),
    deferred_expiry_date: n(form.deferred_expiry_date),
    deferred_limit_fh: form.deferred_limit_fh !== '' ? Number(form.deferred_limit_fh) : null,
    deferred_limit_fc: form.deferred_limit_fc !== '' ? Number(form.deferred_limit_fc) : null,
    interval_fh: form.interval_fh !== '' ? Number(form.interval_fh) : null,
    interval_fc: form.interval_fc !== '' ? Number(form.interval_fc) : null,
    interval_days: form.interval_days !== '' ? Number(form.interval_days) : null,
    next_due_date: n(form.next_due_date),
    next_due_fh: form.next_due_fh !== '' ? Number(form.next_due_fh) : null,
    next_due_fc: form.next_due_fc !== '' ? Number(form.next_due_fc) : null,
    notes: n(form.notes),
  }
}

function fromRecord(sb) {
  const s = v => (v == null ? '' : String(v))
  return {
    sb_number: sb.sb_number, title: sb.title,
    ata_chapter: sb.ata_chapter, category: sb.category,
    latest_revision: sb.latest_revision, status: sb.status,
    ad_flag: sb.ad_flag, interval_type: sb.interval_type,
    revision_accomplished: s(sb.revision_accomplished),
    accomplishment_date: s(sb.accomplishment_date),
    work_order_ref: s(sb.work_order_ref),
    deferred_expiry_date: s(sb.deferred_expiry_date),
    deferred_limit_fh: s(sb.deferred_limit_fh),
    deferred_limit_fc: s(sb.deferred_limit_fc),
    interval_fh: s(sb.interval_fh), interval_fc: s(sb.interval_fc),
    interval_days: s(sb.interval_days), next_due_date: s(sb.next_due_date),
    next_due_fh: s(sb.next_due_fh), next_due_fc: s(sb.next_due_fc),
    notes: s(sb.notes),
  }
}

// ── SB Form (used in modal) ───────────────────────────────────────────────────

function SBForm({ form, onChange, onSubmit, onCancel, saving, error, isEdit }) {
  const f = (field) => ({
    value: form[field],
    onChange: e => onChange({ ...form, [field]: e.target.value })
  })
  const check = (field) => ({
    checked: Boolean(form[field]),
    onChange: e => onChange({ ...form, [field]: e.target.checked })
  })

  return (
    <form onSubmit={e => { e.preventDefault(); onSubmit() }}>
      {error && <div className="form-error">{error}</div>}
      <div className="form-grid">
        <div className="form-field">
          <label>SB Number *</label>
          <input {...f('sb_number')} placeholder="A320-27-1098" required />
        </div>
        <div className="form-field form-field--wide">
          <label>Title *</label>
          <input {...f('title')} placeholder="Short description" required />
        </div>
        <div className="form-field">
          <label>ATA Chapter</label>
          <select {...f('ata_chapter')}>
            {ATA_OPTIONS.map(a => <option key={a} value={a}>{a}</option>)}
          </select>
        </div>
        <div className="form-field">
          <label>Category</label>
          <select {...f('category')}>
            {CATEGORY_OPTIONS.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div className="form-field">
          <label>Latest Revision</label>
          <input {...f('latest_revision')} placeholder="Rev 01" />
        </div>
        <div className="form-field">
          <label>Status</label>
          <select {...f('status')}>
            {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s.replace(/_/g,' ')}</option>)}
          </select>
        </div>
        <div className="form-field">
          <label>Interval Type</label>
          <select {...f('interval_type')}>
            <option value="one_time">One-time</option>
            <option value="recurring">Recurring</option>
          </select>
        </div>
        <div className="form-field form-field--checkbox">
          <label><input type="checkbox" {...check('ad_flag')} /> AD Mandated</label>
        </div>
      </div>

      {/* Accomplished fields */}
      {form.status === 'accomplished' && (
        <div className="form-section">
          <div className="form-section-title">Accomplishment Details</div>
          <div className="form-grid">
            <div className="form-field">
              <label>Revision Accomplished</label>
              <input {...f('revision_accomplished')} placeholder="Rev 01" />
            </div>
            <div className="form-field">
              <label>Accomplishment Date</label>
              <input type="date" {...f('accomplishment_date')} />
            </div>
            <div className="form-field">
              <label>Work Order Ref</label>
              <input {...f('work_order_ref')} placeholder="WO-12345" />
            </div>
          </div>
        </div>
      )}

      {/* Deferred fields */}
      {form.status === 'deferred' && (
        <div className="form-section">
          <div className="form-section-title">Deferral Limits</div>
          <div className="form-grid">
            <div className="form-field">
              <label>Expiry Date</label>
              <input type="date" {...f('deferred_expiry_date')} />
            </div>
            <div className="form-field">
              <label>Limit FH</label>
              <input type="number" {...f('deferred_limit_fh')} placeholder="e.g. 47000" />
            </div>
            <div className="form-field">
              <label>Limit FC</label>
              <input type="number" {...f('deferred_limit_fc')} placeholder="e.g. 33500" />
            </div>
          </div>
        </div>
      )}

      {/* Recurring fields */}
      {form.interval_type === 'recurring' && (
        <div className="form-section">
          <div className="form-section-title">Recurrence Intervals</div>
          <div className="form-grid">
            <div className="form-field">
              <label>Interval FH</label>
              <input type="number" {...f('interval_fh')} placeholder="e.g. 3000" />
            </div>
            <div className="form-field">
              <label>Interval FC</label>
              <input type="number" {...f('interval_fc')} placeholder="e.g. 2000" />
            </div>
            <div className="form-field">
              <label>Interval Days</label>
              <input type="number" {...f('interval_days')} placeholder="e.g. 365" />
            </div>
            <div className="form-section-title" style={{marginTop:'8px'}}>Next Due</div>
            <div className="form-field">
              <label>Next Due Date</label>
              <input type="date" {...f('next_due_date')} />
            </div>
            <div className="form-field">
              <label>Next Due FH</label>
              <input type="number" step="0.1" {...f('next_due_fh')} placeholder="e.g. 47800" />
            </div>
            <div className="form-field">
              <label>Next Due FC</label>
              <input type="number" {...f('next_due_fc')} placeholder="e.g. 33900" />
            </div>
          </div>
        </div>
      )}

      <div className="form-field" style={{marginTop:'12px'}}>
        <label>Notes</label>
        <textarea {...f('notes')} rows={2} placeholder="Optional notes…" />
      </div>

      <div className="form-actions">
        <button type="button" className="btn btn-secondary" onClick={onCancel}>Cancel</button>
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? 'Saving…' : isEdit ? 'Update SB' : 'Add SB'}
        </button>
      </div>
    </form>
  )
}

// ── Config Tab ────────────────────────────────────────────────────────────────

function ConfigTab({ aircraft, onRefresh }) {
  const [editingComp, setEditingComp] = useState(null)  // component being edited
  const [compForm, setCompForm]       = useState({})
  const [saving, setSaving]           = useState(false)
  const [compError, setCompError]     = useState(null)

  const [showAddMod, setShowAddMod]   = useState(false)
  const [modForm, setModForm]         = useState({ mod_number: '', description: '', embodied_date: '' })
  const [modError, setModError]       = useState(null)
  const [modSaving, setModSaving]     = useState(false)

  const groups = groupComponents(aircraft.components)

  async function saveComponent() {
    setSaving(true); setCompError(null)
    try {
      await api.updateComponent(aircraft.msn, editingComp.id, compForm)
      setEditingComp(null)
      onRefresh()
    } catch (e) { setCompError(e.message) }
    finally { setSaving(false) }
  }

  async function addMod() {
    if (!modForm.mod_number.trim()) return setModError('Mod number required')
    if (!modForm.embodied_date)     return setModError('Date required')
    setModSaving(true); setModError(null)
    try {
      await api.addModification(aircraft.msn, modForm)
      setModForm({ mod_number: '', description: '', embodied_date: '' })
      setShowAddMod(false)
      onRefresh()
    } catch (e) { setModError(e.message) }
    finally { setModSaving(false) }
  }

  async function deleteMod(id) {
    if (!confirm('Delete this modification?')) return
    try { await api.deleteModification(aircraft.msn, id); onRefresh() }
    catch (e) { alert(e.message) }
  }

  return (
    <div className="tab-content">
      {/* Components */}
      {Object.entries(groups).map(([group, comps]) => (
        comps.length > 0 && (
          <div key={group} className="section">
            <h3 className="section-title">{group}</h3>
            <table className="table table-compact">
              <thead>
                <tr>
                  <th>Position</th>
                  <th>Part Number</th>
                  <th>Serial Number</th>
                  {group === 'Avionics' && <th>Software PN</th>}
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {comps.map(c => (
                  <tr key={c.id}>
                    <td className="text-secondary">{c.position}</td>
                    <td><span className="mono">{c.part_number}</span></td>
                    <td><span className="mono">{c.serial_number}</span></td>
                    {group === 'Avionics' && <td><span className="mono">{c.software_pn || '—'}</span></td>}
                    <td>
                      <button className="btn btn-sm btn-secondary"
                        onClick={() => { setEditingComp(c); setCompForm({ position: c.position, part_number: c.part_number, serial_number: c.serial_number, software_pn: c.software_pn || '' }); setCompError(null) }}>
                        Edit
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      ))}

      {/* Component edit modal */}
      {editingComp && (
        <Modal title={`Edit — ${editingComp.position}`} onClose={() => setEditingComp(null)}>
          {compError && <div className="form-error">{compError}</div>}
          <div className="form-grid">
            {['part_number', 'serial_number', 'software_pn'].map(field => (
              <div key={field} className="form-field">
                <label>{field.replace(/_/g, ' ')}</label>
                <input value={compForm[field] || ''} onChange={e => setCompForm({ ...compForm, [field]: e.target.value })} />
              </div>
            ))}
          </div>
          <div className="form-actions">
            <button className="btn btn-secondary" onClick={() => setEditingComp(null)}>Cancel</button>
            <button className="btn btn-primary" disabled={saving} onClick={saveComponent}>
              {saving ? 'Saving…' : 'Save'}
            </button>
          </div>
        </Modal>
      )}

      {/* Modifications */}
      <div className="section">
        <div className="section-header">
          <h3 className="section-title">Embodied Modifications</h3>
          <button className="btn btn-primary btn-sm" onClick={() => { setShowAddMod(true); setModError(null) }}>
            + Add Modification
          </button>
        </div>
        {aircraft.modifications.length === 0
          ? <p className="text-muted" style={{padding:'12px 0'}}>No modifications recorded.</p>
          : (
            <table className="table table-compact">
              <thead>
                <tr><th>Mod Number</th><th>Description</th><th>Date Embodied</th><th></th></tr>
              </thead>
              <tbody>
                {[...aircraft.modifications].sort((a,b) => b.embodied_date.localeCompare(a.embodied_date)).map(m => (
                  <tr key={m.id}>
                    <td><span className="mono">{m.mod_number}</span></td>
                    <td className="text-secondary">{m.description}</td>
                    <td className="text-secondary">{m.embodied_date}</td>
                    <td>
                      <button className="btn btn-sm btn-danger" onClick={() => deleteMod(m.id)}>✕</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
        }
      </div>

      {/* Add mod modal */}
      {showAddMod && (
        <Modal title="Add Modification" onClose={() => setShowAddMod(false)}>
          {modError && <div className="form-error">{modError}</div>}
          <div className="form-grid">
            <div className="form-field">
              <label>Mod Number *</label>
              <input value={modForm.mod_number} onChange={e => setModForm({...modForm, mod_number: e.target.value})} placeholder="SB A320-27-1098 or MOD 12345" />
            </div>
            <div className="form-field form-field--wide">
              <label>Description</label>
              <input value={modForm.description} onChange={e => setModForm({...modForm, description: e.target.value})} placeholder="Brief description" />
            </div>
            <div className="form-field">
              <label>Date Embodied *</label>
              <input type="date" value={modForm.embodied_date} onChange={e => setModForm({...modForm, embodied_date: e.target.value})} />
            </div>
          </div>
          <div className="form-actions">
            <button className="btn btn-secondary" onClick={() => setShowAddMod(false)}>Cancel</button>
            <button className="btn btn-primary" disabled={modSaving} onClick={addMod}>
              {modSaving ? 'Adding…' : 'Add Modification'}
            </button>
          </div>
        </Modal>
      )}
    </div>
  )
}

// ── SB Status Board Tab ───────────────────────────────────────────────────────

function SBTab({ aircraft, onRefresh }) {
  const [filters, setFilters] = useState({ status: '', category: '', ata: '', adOnly: false, dueSoonOnly: false, search: '' })
  const [sbModal, setSbModal]   = useState(null)  // null | { mode: 'add'|'edit', record? }
  const [sbForm, setSbForm]     = useState(BLANK_SB)
  const [saving, setSaving]     = useState(false)
  const [sbError, setSbError]   = useState(null)

  const sbs = aircraft.sb_records || []

  const filtered = sbs.filter(sb => {
    if (filters.status   && sb.status      !== filters.status)   return false
    if (filters.category && sb.category    !== filters.category) return false
    if (filters.ata      && sb.ata_chapter !== filters.ata)      return false
    if (filters.adOnly   && !sb.ad_flag)                         return false
    if (filters.dueSoonOnly && !sb.due_soon)                     return false
    if (filters.search) {
      const q = filters.search.toLowerCase()
      if (!sb.sb_number.toLowerCase().includes(q) && !sb.title.toLowerCase().includes(q)) return false
    }
    return true
  })

  // Summary counts
  const counts = sbs.reduce((acc, sb) => {
    acc[sb.status] = (acc[sb.status] || 0) + 1
    return acc
  }, {})
  const dueSoonCount = sbs.filter(sb => sb.due_soon).length

  function openAdd() {
    setSbForm(BLANK_SB); setSbError(null); setSbModal({ mode: 'add' })
  }
  function openEdit(sb) {
    setSbForm(fromRecord(sb)); setSbError(null); setSbModal({ mode: 'edit', record: sb })
  }

  async function saveSB() {
    if (!sbForm.sb_number.trim()) return setSbError('SB number is required')
    if (!sbForm.title.trim())     return setSbError('Title is required')
    setSaving(true); setSbError(null)
    try {
      const payload = toApiPayload(sbForm)
      if (sbModal.mode === 'add') {
        await api.addSB(aircraft.msn, payload)
      } else {
        await api.updateSB(aircraft.msn, sbModal.record.id, payload)
      }
      setSbModal(null)
      onRefresh()
    } catch (e) { setSbError(e.message) }
    finally { setSaving(false) }
  }

  async function deleteSB(sb) {
    if (!confirm(`Delete SB ${sb.sb_number}? This cannot be undone.`)) return
    try { await api.deleteSB(aircraft.msn, sb.id); onRefresh() }
    catch (e) { alert(e.message) }
  }

  return (
    <div className="tab-content">
      {/* Summary bar */}
      <div className="sb-summary">
        {Object.entries(counts).sort().map(([s, n]) => (
          <div key={s} className="sb-summary-item">
            {statusBadge(s)} <span className="sb-summary-count">{n}</span>
          </div>
        ))}
        {dueSoonCount > 0 && (
          <div className="sb-summary-item">
            <span className="badge badge--amber">⚠ due soon</span>
            <span className="sb-summary-count">{dueSoonCount}</span>
          </div>
        )}
      </div>

      {/* Filters + actions */}
      <div className="filter-row">
        <input className="filter-search" placeholder="Search SB number or title…"
          value={filters.search} onChange={e => setFilters({...filters, search: e.target.value})} />
        <select value={filters.status} onChange={e => setFilters({...filters, status: e.target.value})}>
          <option value="">All statuses</option>
          {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s.replace(/_/g,' ')}</option>)}
        </select>
        <select value={filters.category} onChange={e => setFilters({...filters, category: e.target.value})}>
          <option value="">All categories</option>
          {CATEGORY_OPTIONS.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <select value={filters.ata} onChange={e => setFilters({...filters, ata: e.target.value})}>
          <option value="">All ATA</option>
          {ATA_OPTIONS.map(a => <option key={a} value={a}>ATA {a}</option>)}
        </select>
        <label className="filter-checkbox">
          <input type="checkbox" checked={filters.adOnly} onChange={e => setFilters({...filters, adOnly: e.target.checked})} />
          AD only
        </label>
        <label className="filter-checkbox">
          <input type="checkbox" checked={filters.dueSoonOnly} onChange={e => setFilters({...filters, dueSoonOnly: e.target.checked})} />
          Due soon
        </label>
        <div style={{flex:1}} />
        <button className="btn btn-secondary btn-sm" onClick={() => api.exportCSV(aircraft.msn)}>
          ↓ Export CSV
        </button>
        <button className="btn btn-primary btn-sm" onClick={openAdd}>+ Add SB</button>
      </div>

      <div className="card" style={{marginTop:'0'}}>
        <table className="table">
          <thead>
            <tr>
              <th>SB Number</th>
              <th>Title</th>
              <th>ATA</th>
              <th>Category</th>
              <th>Status</th>
              <th>AD</th>
              <th>⚠</th>
              <th>Accomplished</th>
              <th>Next Due</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0
              ? <tr><td colSpan={10} className="text-center text-muted" style={{padding:'24px'}}>No SBs match the current filters.</td></tr>
              : filtered.map(sb => (
                <tr key={sb.id} className={sb.due_soon ? 'row-due-soon' : ''}>
                  <td><span className="mono sb-number">{sb.sb_number}</span></td>
                  <td className="sb-title">{sb.title}</td>
                  <td className="text-secondary">{sb.ata_chapter}</td>
                  <td>{categoryBadge(sb.category)}</td>
                  <td>{statusBadge(sb.status)}</td>
                  <td>{sb.ad_flag ? <span className="badge badge--red">AD</span> : <span className="text-muted">—</span>}</td>
                  <td>{sb.due_soon ? <span title="Due soon">⚠️</span> : ''}</td>
                  <td className="text-secondary text-sm">
                    {sb.accomplishment_date
                      ? <>{sb.revision_accomplished} · {sb.accomplishment_date}</>
                      : sb.deferred_expiry_date
                        ? <span className="text-amber">Def. to {sb.deferred_expiry_date}</span>
                        : '—'}
                  </td>
                  <td className="text-secondary text-sm">
                    {sb.next_due_fh  && <div>{Number(sb.next_due_fh).toLocaleString()} FH</div>}
                    {sb.next_due_fc  && <div>{Number(sb.next_due_fc).toLocaleString()} FC</div>}
                    {sb.next_due_date && <div>{sb.next_due_date}</div>}
                    {!sb.next_due_fh && !sb.next_due_fc && !sb.next_due_date && '—'}
                  </td>
                  <td>
                    <div className="row-actions">
                      <button className="btn btn-sm btn-secondary" onClick={() => openEdit(sb)}>Edit</button>
                      <button className="btn btn-sm btn-danger" onClick={() => deleteSB(sb)}>✕</button>
                    </div>
                  </td>
                </tr>
              ))
            }
          </tbody>
        </table>
      </div>
      <div className="text-muted text-sm" style={{marginTop:'8px'}}>
        Showing {filtered.length} of {sbs.length} SBs
      </div>

      {sbModal && (
        <Modal title={sbModal.mode === 'add' ? 'Add SB Record' : `Edit — ${sbModal.record.sb_number}`}
          onClose={() => setSbModal(null)} wide>
          <SBForm form={sbForm} onChange={setSbForm} onSubmit={saveSB}
            onCancel={() => setSbModal(null)} saving={saving} error={sbError}
            isEdit={sbModal.mode === 'edit'} />
        </Modal>
      )}
    </div>
  )
}

// ── Main MSNDetail component ──────────────────────────────────────────────────

export default function MSNDetail() {
  const { msn }  = useParams()
  const navigate = useNavigate()
  const [aircraft, setAircraft] = useState(null)
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState(null)
  const [activeTab, setActiveTab] = useState('sb')

  const load = useCallback(() => {
    setLoading(true)
    api.getAircraft(msn)
      .then(setAircraft)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [msn])

  useEffect(() => { load() }, [load])

  if (loading) return <div className="page-loading">Loading MSN {msn}…</div>
  if (error)   return <div className="page-error">Error: {error}</div>
  if (!aircraft) return null

  const openSBs    = aircraft.sb_records.filter(s => s.status === 'open').length
  const adOpen     = aircraft.sb_records.filter(s => s.status === 'open' && s.ad_flag).length
  const dueSoon    = aircraft.sb_records.filter(s => s.due_soon).length

  return (
    <div className="page">
      <div className="page-header">
        <div className="breadcrumb">
          <button className="btn-link" onClick={() => navigate('/')}>Fleet Overview</button>
          <span className="breadcrumb-sep">›</span>
          <span>MSN {aircraft.msn}</span>
        </div>
        <h1 className="page-title">
          {aircraft.registration}
          <span className="page-title-sub">MSN {aircraft.msn} · {aircraft.operator} · {aircraft.type_variant}</span>
        </h1>
        <div className="aircraft-stats">
          <div className="stat-pill"><span className="stat-pill-label">FH</span>{aircraft.current_fh.toLocaleString()}</div>
          <div className="stat-pill"><span className="stat-pill-label">FC</span>{aircraft.current_fc.toLocaleString()}</div>
          {adOpen  > 0 && <div className="stat-pill stat-pill--danger">AD Open: {adOpen}</div>}
          {dueSoon > 0 && <div className="stat-pill stat-pill--warning">Due Soon: {dueSoon}</div>}
          {openSBs > 0 && <div className="stat-pill stat-pill--info">Open SBs: {openSBs}</div>}
        </div>
      </div>

      <div className="tabs">
        <button className={`tab ${activeTab === 'config' ? 'tab--active' : ''}`}
          onClick={() => setActiveTab('config')}>Configuration</button>
        <button className={`tab ${activeTab === 'sb' ? 'tab--active' : ''}`}
          onClick={() => setActiveTab('sb')}>SB Status Board</button>
      </div>

      {activeTab === 'config'
        ? <ConfigTab aircraft={aircraft} onRefresh={load} />
        : <SBTab    aircraft={aircraft} onRefresh={load} />
      }
    </div>
  )
}
