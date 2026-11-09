import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/context/AuthContext";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import Consent from "@/pages/Consent";
import PhotoCapture from "@/pages/PhotoCapture";
import Questionnaire from "@/pages/Questionnaire";
import Profile from "@/pages/Profile";

function Welcome() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-skin-cream p-4 text-center">
      <h1 className="text-4xl font-bold text-skin-warm-gray mb-2">Facial y Moda</h1>
      <p className="text-skin-sage text-lg mb-8">Skin Intelligence — Tu asesor cosmético personal</p>
      <div className="flex gap-3">
        <a
          href="/login"
          className="px-6 py-3 bg-skin-sage text-white font-medium rounded-xl hover:bg-skin-warm-gray transition"
        >
          Iniciar sesión
        </a>
        <a
          href="/registro"
          className="px-6 py-3 bg-white border border-skin-beige text-skin-warm-gray font-medium rounded-xl hover:bg-skin-beige transition"
        >
          Crear cuenta
        </a>
      </div>
    </div>
  );
}

function Dashboard() {
  return (
    <div className="min-h-screen bg-skin-cream p-4">
      <div className="max-w-xl mx-auto">
        <h1 className="text-2xl font-bold text-skin-warm-gray mb-6">Dashboard</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <a
            href="/cuestionario"
            className="p-6 bg-white border border-skin-beige rounded-2xl text-skin-warm-gray hover:bg-skin-beige transition"
          >
            <h3 className="font-bold mb-2">Cuestionario de piel</h3>
            <p className="text-sm text-skin-sage">Responde sobre tu piel y hábitos</p>
          </a>
          <a
            href="/captura-fotos"
            className="p-6 bg-white border border-skin-beige rounded-2xl text-skin-warm-gray hover:bg-skin-beige transition"
          >
            <h3 className="font-bold mb-2">Capturar fotografías</h3>
            <p className="text-sm text-skin-sage">Tómate 3 fotos del rostro</p>
          </a>
          <a
            href="/resultados"
            className="p-6 bg-white border border-skin-beige rounded-2xl text-skin-warm-gray hover:bg-skin-beige transition"
          >
            <h3 className="font-bold mb-2">Ver resultados</h3>
            <p className="text-sm text-skin-sage">Perfil y rutina recomendada</p>
          </a>
          <a
            href="/perfil"
            className="p-6 bg-white border border-skin-beige rounded-2xl text-skin-warm-gray hover:bg-skin-beige transition"
          >
            <h3 className="font-bold mb-2">Mi perfil</h3>
            <p className="text-sm text-skin-sage">Datos, consentimientos y fotos</p>
          </a>
        </div>
      </div>
    </div>
  );
}

function RequireAuth({ children }: { children: any }) {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return null;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/welcome" replace />} />
          <Route path="/welcome" element={<Welcome />} />
          <Route path="/login" element={<Login />} />
          <Route path="/registro" element={<Register />} />
          <Route path="/consentimiento" element={<Consent />} />
          <Route
            path="/captura-fotos"
            element={
              <RequireAuth>
                <PhotoCapture />
              </RequireAuth>
            }
          />
          <Route
            path="/cuestionario"
            element={
              <RequireAuth>
                <Questionnaire />
              </RequireAuth>
            }
          />
          <Route path="/resultados" element={<div>Resultados (Fase 4)</div>} />
          <Route
            path="/perfil"
            element={
              <RequireAuth>
                <Profile />
              </RequireAuth>
            }
          />
          <Route
            path="/dashboard"
            element={
              <RequireAuth>
                <Dashboard />
              </RequireAuth>
            }
          />
          <Route path="*" element={<Navigate to="/welcome" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
