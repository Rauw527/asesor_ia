import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "No se pudo iniciar sesión. Intenta de nuevo."
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
          <p className="text-skin-sage mt-2">Skin Intelligence — Iniciar sesión</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded-2xl shadow-sm border border-skin-beige">
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
              Contraseña
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
          {error && (
            <p className="text-sm text-red-600 text-center">{error}</p>
          )}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-skin-sage text-white font-medium rounded-lg disabled:opacity-50 hover:bg-skin-warm-gray transition"
          >
            {loading ? "Entrando..." : "Ingresar"}
          </button>
        </form>
        <p className="text-center text-sm text-skin-warm-gray mt-6">
          ¿No tienes cuenta?{" "}
          <a href="/registro" className="text-skin-sage font-medium">
            Regístrate
          </a>
        </p>
      </div>
    </div>
  );
}
