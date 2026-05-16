import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Nav from './components/Nav.jsx'
import FleetOverview from './pages/FleetOverview.jsx'
import MSNDetail from './pages/MSNDetail.jsx'
import ApplicabilityChecker from './pages/ApplicabilityChecker.jsx'

export default function App() {
  return (
    <BrowserRouter>
      <Nav />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<FleetOverview />} />
          <Route path="/aircraft/:msn" element={<MSNDetail />} />
          <Route path="/applicability" element={<ApplicabilityChecker />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}
