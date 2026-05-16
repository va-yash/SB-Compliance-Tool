import { useState, useRef } from 'react'
import { api } from '../api.js'

const APPLICABILITY_LABELS = {
  likely_applicable:     { label: 'Likely Applicable',     cls: 'badge--green' },
  likely_not_applicable: { label: 'Likely Not Applicable',  cls: 'badge--gray'  },
  uncertain:             { label: 'Uncertain — Review Req.', cls: 'badge--amber' },
}

const CONFIDENCE_LABELS = {
  high:   { label: 'High',   cls: 'badge--green' },
  medium: { label: 'Medium', cls: 'badge--amber' },
  low:    { label: 'Low',    cls: 'badge--red'   },
}

export default function ApplicabilityChecker() {
  const [mode, setMode]           = useState('text')    // 'pdf' | 'text'
  const [pdfFile, setPdfFile]     = useState(null)
  const [pastedText, setPastedText] = useState('')
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState(null)
  const [result, setResult]       = useState(null)
  const [rawOpen, setRawOpen]     = useState(false)
  const fileRef = useRef()

  async function handleSubmit() {
    setError(null); setResult(null)

    if (mode === 'pdf' && !pdfFile) return setError('Please select a PDF file.')
    if (mode === 'text' && !pastedText.trim()) return setError('Please paste some effectivity text.')

    const formData = new FormData()
    if (mode === 'pdf') {
      formData.append('pdf_file', pdfFile)
    } else {
      formData.append('text', pastedText)
    }

    setLoading(true)
    try {
      const data = await api.parseApplicability(formData)
      setResult(data)
      setRawOpen(false)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  function reset() {
    setResult(null); setError(null)
    setPdfFile(null); setPastedText('')
    if (fileRef.current) fileRef.current.value = ''
  }

  const p = result?.parsed || {}
  const applicableMSNs = result?.results?.filter(r => r.applicability === 'likely_applicable').length ?? 0

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">SB Applicability Checker</h1>
        <p className="page-subtitle">
          Upload a Service Bulletin PDF or paste effectivity text — Claude will extract the applicability rules
          and compare them against all 10 registered MSNs.
        </p>
      </div>

      {!result ? (
        <div className="card checker-card">
          {/* Mode toggle */}
          <div className="mode-toggle">
            <button
              className={`mode-btn ${mode === 'text' ? 'mode-btn--active' : ''}`}
              onClick={() => setMode('text')}>
              Paste Text
            </button>
            <button
              className={`mode-btn ${mode === 'pdf' ? 'mode-btn--active' : ''}`}
              onClick={() => setMode('pdf')}>
              Upload PDF
            </button>
          </div>

          {mode === 'text' && (
            <div className="form-field" style={{marginTop:'16px'}}>
              <label>Effectivity / Applicability Text</label>
              <textarea
                className="effectivity-textarea"
                rows={10}
                placeholder={`Paste the effectivity section from the Service Bulletin here.\n\nExample:\n"Applicable to A320-200 aircraft, MSN 0001 to 5000, except MSN 1234 and 1567.\nNot applicable to aircraft embodying mod 26345."`}
                value={pastedText}
                onChange={e => setPastedText(e.target.value)}
              />
            </div>
          )}

          {mode === 'pdf' && (
            <div className="pdf-upload-area" onClick={() => fileRef.current?.click()}>
              <input
                ref={fileRef}
                type="file"
                accept=".pdf"
                style={{ display: 'none' }}
                onChange={e => setPdfFile(e.target.files[0] || null)}
              />
              {pdfFile ? (
                <div className="pdf-selected">
                  <span className="pdf-icon">📄</span>
                  <div>
                    <div className="pdf-name">{pdfFile.name}</div>
                    <div className="text-secondary text-sm">{(pdfFile.size / 1024).toFixed(0)} KB</div>
                  </div>
                  <button className="btn btn-secondary btn-sm" style={{marginLeft:'auto'}}
                    onClick={e => { e.stopPropagation(); setPdfFile(null); fileRef.current.value = '' }}>
                    Remove
                  </button>
                </div>
              ) : (
                <div className="pdf-placeholder">
                  <span className="pdf-icon">📎</span>
                  <div>Click to select a PDF file</div>
                  <div className="text-secondary text-sm">Maximum 10 MB · PDF only</div>
                </div>
              )}
            </div>
          )}

          {error && <div className="form-error" style={{marginTop:'12px'}}>{error}</div>}

          <div className="form-actions" style={{marginTop:'16px'}}>
            <button className="btn btn-primary" onClick={handleSubmit} disabled={loading} style={{minWidth:'140px'}}>
              {loading ? (
                <><span className="spinner" /> Analysing…</>
              ) : 'Analyse Applicability'}
            </button>
          </div>

          {loading && (
            <div className="analysis-progress">
              <div className="progress-step">Extracting text from document…</div>
              <div className="progress-step">Sending to Claude claude-sonnet-4-20250514…</div>
              <div className="progress-step">Comparing against 10 registered MSNs…</div>
            </div>
          )}
        </div>
      ) : (
        <div>
          {/* Results summary */}
          <div className="results-header">
            <div>
              <h2 className="section-title">Applicability Results</h2>
              <p className="text-secondary">
                Source: <strong>{result.source === 'pdf' ? 'PDF upload' : 'Pasted text'}</strong>
                {' · '}{result.chars_analysed?.toLocaleString()} characters analysed
              </p>
            </div>
            <div className="results-meta">
              <span className="badge badge--green">{applicableMSNs} applicable</span>
              <span className="badge badge--gray">{result.results.length - applicableMSNs} not / uncertain</span>
              {p.confidence && (
                <span className={`badge ${CONFIDENCE_LABELS[p.confidence]?.cls || 'badge--gray'}`}>
                  Confidence: {CONFIDENCE_LABELS[p.confidence]?.label || p.confidence}
                </span>
              )}
            </div>
            <button className="btn btn-secondary" onClick={reset}>← New Analysis</button>
          </div>

          {/* Parsed parameters summary */}
          <div className="card parsed-summary">
            <h3 className="section-title">Extracted Effectivity Parameters</h3>
            <div className="parsed-grid">
              <div className="parsed-item">
                <span className="parsed-label">MSN Range</span>
                <span className="parsed-value">
                  {p.msn_range?.from || p.msn_range?.to
                    ? `${p.msn_range?.from ?? '—'} → ${p.msn_range?.to ?? '—'}`
                    : 'Not specified'}
                </span>
              </div>
              <div className="parsed-item">
                <span className="parsed-label">Excluded MSNs</span>
                <span className="parsed-value">{p.excluded_msns?.length ? p.excluded_msns.join(', ') : 'None'}</span>
              </div>
              <div className="parsed-item">
                <span className="parsed-label">Required Mods</span>
                <span className="parsed-value">{p.required_mod_numbers?.length ? p.required_mod_numbers.join(', ') : 'None'}</span>
              </div>
              <div className="parsed-item">
                <span className="parsed-label">Excluded Mods</span>
                <span className="parsed-value">{p.excluded_mod_numbers?.length ? p.excluded_mod_numbers.join(', ') : 'None'}</span>
              </div>
              {p.notes && (
                <div className="parsed-item parsed-item--wide">
                  <span className="parsed-label">Notes</span>
                  <span className="parsed-value">{p.notes}</span>
                </div>
              )}
              {p.confidence_reason && (
                <div className="parsed-item parsed-item--wide">
                  <span className="parsed-label">Confidence Reason</span>
                  <span className="parsed-value text-secondary">{p.confidence_reason}</span>
                </div>
              )}
            </div>
          </div>

          {/* Per-MSN results table */}
          <div className="card">
            <table className="table">
              <thead>
                <tr>
                  <th>MSN</th>
                  <th>Registration</th>
                  <th>Operator</th>
                  <th>Applicability</th>
                  <th>Reason</th>
                </tr>
              </thead>
              <tbody>
                {result.results.map(r => {
                  const info = APPLICABILITY_LABELS[r.applicability] || { label: r.applicability, cls: 'badge--gray' }
                  return (
                    <tr key={r.msn}>
                      <td><span className="mono">{r.msn}</span></td>
                      <td><strong>{r.registration}</strong></td>
                      <td className="text-secondary">{r.operator}</td>
                      <td><span className={`badge ${info.cls}`}>{info.label}</span></td>
                      <td className="text-secondary text-sm">{r.reason}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          {/* Raw JSON collapsible */}
          <div className="raw-json-section">
            <button className="btn-link" onClick={() => setRawOpen(o => !o)}>
              {rawOpen ? '▼' : '▶'} Raw Claude output (JSON)
            </button>
            {rawOpen && (
              <pre className="raw-json">{JSON.stringify(result.parsed, null, 2)}</pre>
            )}
          </div>

          <div className="checker-disclaimer">
            ⚠ This analysis is AI-generated and indicative only. Always verify applicability against the original
            Service Bulletin effectivity section and confirm with a qualified engineer before making maintenance decisions.
          </div>
        </div>
      )}
    </div>
  )
}
