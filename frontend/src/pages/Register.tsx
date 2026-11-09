import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";

export default function Register() {
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(email, fullName, password);
      navigate("/consentimiento");
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "No se pudo crear la cuenta. Intenta de nuevo."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-skin-cream p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-skin-warm-gray">Facial y Moda</h1>
          <p className="text-skin-sage mt-2">Crear tu cuenta</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded-2xl shadow-sm border border-skin-beige">
          <div>
            <label className="block text-sm font-medium text-skin-warm-gray mb-1">
              Nombre completo
            </label>
            <input
              type="text"
              required
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-skin-sage outline-none"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-skin-warm-gray mb-1">
              Correo electrónico
            </label>
            <input
              type="email"
              required
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-skin-sage outline-none"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-skin-warm-gray mb-1">
              Contraseña (mínimo 8 caracteres)
            </label>
            <input
              type="password"
              required
              minLength={8}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-skin-sage outline-none"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          {error && <p className="text-sm text-red-600 text-center">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-skin-sage text-white font-medium rounded-lg disabled:opacity-50 hover:bg-skin-warm-gray transition"
          >
            {loading ? "Creando..." : "Crear cuenta"}
          </button>
        </form>
        <p className="text-center text-sm text-skin-warm-gray mt-6">
          ¿Ya tienes cuenta?{" "}
          <a href="/login" className="text-skin-sage font-medium">
            Inicia sesión
          </a>
        </p>
      </div>
    </div>
  );
}
