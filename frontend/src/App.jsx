import { Routes, Route } from "react-router-dom"
import { AuthProvider } from "./context/AuthContext"
import Layout from "./components/Layout"
import AnalyzePage  from "./pages/AnalyzePage"
import HistoryPage  from "./pages/HistoryPage"
import ReportsPage  from "./pages/ReportsPage"
import ModelsPage   from "./pages/ModelsPage"
import LoginPage    from "./pages/LoginPage"

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={
          <Layout>
            <Routes>
              <Route index          element={<AnalyzePage  />} />
              <Route path="history" element={<HistoryPage  />} />
              <Route path="reports" element={<ReportsPage  />} />
              <Route path="models"  element={<ModelsPage   />} />
            </Routes>
          </Layout>
        } />
      </Routes>
    </AuthProvider>
  )
}
