const BASE = '/api'

async function req(url, options = {}) {
  const res = await fetch(url, options)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res
}

export const api = {
  // Fleet
  listAircraft: () =>
    req(`${BASE}/aircraft`).then(r => r.json()),

  getAircraft: (msn) =>
    req(`${BASE}/aircraft/${msn}`).then(r => r.json()),

  patchAircraft: (msn, data) =>
    req(`${BASE}/aircraft/${msn}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then(r => r.json()),

  // Components
  updateComponent: (msn, componentId, data) =>
    req(`${BASE}/aircraft/${msn}/component/${componentId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then(r => r.json()),

  // Modifications
  addModification: (msn, data) =>
    req(`${BASE}/aircraft/${msn}/modification`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then(r => r.json()),

  deleteModification: (msn, modId) =>
    req(`${BASE}/aircraft/${msn}/modification/${modId}`, { method: 'DELETE' }).then(r => r.json()),

  // SB records
  addSB: (msn, data) =>
    req(`${BASE}/aircraft/${msn}/sb`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then(r => r.json()),

  updateSB: (msn, sbId, data) =>
    req(`${BASE}/aircraft/${msn}/sb/${sbId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then(r => r.json()),

  deleteSB: (msn, sbId) =>
    req(`${BASE}/aircraft/${msn}/sb/${sbId}`, { method: 'DELETE' }).then(r => r.json()),

  // CSV export — triggers browser download
  exportCSV: async (msn) => {
    const res = await req(`${BASE}/aircraft/${msn}/export-csv`)
    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `SB_Status_${msn}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  },

  // Applicability parser
  parseApplicability: (formData) =>
    req(`${BASE}/sb/parse-applicability`, { method: 'POST', body: formData }).then(r => r.json()),
}
