import { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { authService } from "@/services/api";

export default function Profile() {
  const { user, logout } = useAuth();
  const [consents, setConsents] = useState<any[]>([]);
  const [photos, setPhotos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [c, p] = await Promise.all([
          authService.getConsents(),
          authService.getPhotos(),
        ]);
        setConsents(c);
        setPhotos(p);
      } catch {
        // ignorar si falla en desarrollo sin backend
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <div className="p-4">Cargando perfil...</div>;

  return (
    <div className="min-h-screen bg-skin-cream p-4">
      <div className="max-w-lg mx-auto">
        <div className="mb-6 flex items-center gap-3">
          <h1 className="text-2xl font-bold text-skin-warm-gray">Tu perfil</h1>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-skin-beige mb-6">
          <h2 className="font-bold text-skin-warm-gray mb-4">Datos personales</h2>
          <p className="text-sm text-skin-warm-gray mb-1">
            <span className="font-semibold">Nombre:</span> {user?.full_name || "—"}
          </p>
          <p className="text-sm text-skin-warm-gray">
            <span className="font-semibold">Correo:</span> {user?.email || "—"}
          </p>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-skin-beige mb-6">
          <h2 className="font-bold text-skin-warm-gray mb-4">Tus consentimientos</h2>
          {consents.length === 0 ? (
            <p className="text-sm text-skin-warm-gray">No hay consentimientos registrados.</p>
          ) : (
            <ul className="space-y-3">
              {consents.map((c) => (
                <li key={c.id} className="p-3 rounded-lg border border-skin-beige bg-skin-beige/30">
                  <p className="text-sm font-medium text-skin-warm-gray">
                    {c.consent_type === "service" ? "A — Servicio" : "B — Entrenamiento IA"}
                  </p>
                  <p className="text-xs text-skin-sage">
                    {c.granted ? "Otorgado" : "Rechazado"} — v{c.version}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-skin-beige mb-6">
          <h2 className="font-bold text-skin-warm-gray mb-4">Tus fotografías</h2>
          {photos.length === 0 ? (
            <p className="text-sm text-skin-warm-gray">No hay fotografías subidas.</p>
          ) : (
            <ul className="space-y-3">
              {photos.map((p) => (
                <li key={p.id} className="p-3 rounded-lg border border-skin-beige flex items-center gap-3">
                  <span className="text-xs font-medium text-skin-warm-gray uppercase">
                    {p.photo_type}
                  </span>
                  <span className="text-xs text-skin-sage flex-1">{p.original_filename || "foto"}</span>
                  <span className="text-xs text-skin-sage">{Math.round((p.size_bytes || 0) / 1024)} KB</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <button
          onClick={logout}
          className="w-full py-3 bg-white border border-skin-beige text-red-600 font-medium rounded-lg hover:bg-red-50 transition"
        >
          Cerrar sesión
        </button>
      </div>
    </div>
  );
}
