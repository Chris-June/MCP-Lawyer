import { Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import { ThemeProvider } from '@/components/theme-provider'

import Layout from '@/components/layout'
import HomePage from '@/pages/home'
import RolesPage from '@/pages/roles'
import RoleDetailPage from '@/pages/role-detail'
import ChatPage from '@/pages/chat'
import DocumentsPage from '@/pages/documents'
import DocumentAutomationPage from '@/pages/document-automation'
import ClauseLibraryPage from '@/pages/clause-library'
import LegalToolsPage from '@/pages/legal-tools'
import ClientIntakePage from '@/pages/client-intake'
import PredictiveAnalysisPage from '@/pages/predictive-analysis'

function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="mcp-theme">
      <Toaster />
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="roles" element={<RolesPage />} />
          <Route path="roles/:roleId" element={<RoleDetailPage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="documents" element={<DocumentsPage />} />
          <Route path="document-automation" element={<DocumentAutomationPage />} />
          <Route path="clause-library" element={<ClauseLibraryPage />} />
          <Route path="legal-tools" element={<LegalToolsPage />} />
          <Route path="client-intake" element={<ClientIntakePage />} />
          <Route path="predictive-analysis" element={<PredictiveAnalysisPage />} />
        </Route>
      </Routes>
    </ThemeProvider>
  )
}

export default App
