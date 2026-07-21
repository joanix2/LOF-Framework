import { Routes, Route, Navigate } from 'react-router-dom'
import { Suspense, lazy } from 'react'

const pages = [

  { path: 'client', label: 'Clients', component: lazy(() => import('./pages/ClientListPage')) },

  { path: 'commande', label: 'Commandes', component: lazy(() => import('./pages/CommandeListPage')) },

  { path: 'chantier', label: 'Chantiers', component: lazy(() => import('./pages/ChantierListPage')) },

  { path: 'equipe', label: 'Equipes', component: lazy(() => import('./pages/EquipeListPage')) },

  { path: 'employe', label: 'Employes', component: lazy(() => import('./pages/EmployeListPage')) },

  { path: 'mission', label: 'Missions', component: lazy(() => import('./pages/MissionListPage')) },

  { path: 'equipement', label: 'Equipements', component: lazy(() => import('./pages/EquipementListPage')) },

  { path: 'commentaire-mission', label: 'CommentaireMissions', component: lazy(() => import('./pages/CommentaireMissionListPage')) },

]

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-md border-b px-6 py-3 flex gap-6 items-center">
        <h1 className="text-xl font-bold text-blue-700">ISOCLIM</h1>
        {pages.map((p) => (
          <a key={p.path} href={`/${p.path}`} className="text-gray-600 hover:text-blue-600 text-sm font-medium">
            {p.label}
          </a>
        ))}
      </nav>
      <main className="p-6 max-w-7xl mx-auto">
        <Suspense fallback={<div className="text-center py-20 text-gray-400">Chargement...</div>}>
          <Routes>
            <Route path="/" element={<Navigate to="/client" replace />} />
            {pages.map((p) => (
              <Route key={p.path} path={`/${p.path}`} element={<p.component />} />
            ))}
          </Routes>
        </Suspense>
      </main>
    </div>
  )
}