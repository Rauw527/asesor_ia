import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "@/services/api";

export default function Consent() {
  const [serviceGranted, setServiceGranted] = useState(false);
  const [trainingGranted, setTrainingGranted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const saveConsent = async (type: string, granted: boolean) => {
    setLoading(true);
    try {
      await authService.saveConsent({
        consent_type: type,
        granted,
        version: "1.0",
        purpose:
          type === "service"
            ? "Tratamiento de fotografías para prestar el servicio de análisis de piel."
            : "Investigación y entrenamiento de modelos de IA (opcional).",
      });
    } catch (err: any) {
      setError("No se pudo guardar el consentimiento. Intenta de nuevo.");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveAndContinue = async () => {
    setError("");
    setLoading(true);
    try {
      await saveConsent("service", serviceGranted);
      await saveConsent("training", trainingGranted);
      if (!serviceGranted) {
        setError("Debes aceptar el consentimiento A para continuar.");
        return;
      }
      navigate("/captura-fotos");
    } catch (err: any) {
      setError("No se pudo guardar el consentimiento. Intenta de nuevo.");
    } finally {
      setLoading(false);
    }
  };

  const continueToPhotos = () => {
    if (!serviceGranted) {
      setError("Debes aceptar el consentimiento A para continuar.");
      return;
    }
    navigate("/captura-fotos");
  };

  return (
    <div className="min-h-screen bg-skin-cream p-4">
      <div className="max-w-xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-skin-warm-gray">Privacidad y consentimiento</h1>
          <p className="text-skin-sage mt-2">
            Antes de capturar tus fotos, necesitamos tu autorización.
          </p>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-skin-beige space-y-6">
          <div>
            <h2 className="font-bold text-skin-warm-gray mb-2">Consentimiento A — Tratamiento para prestar el servicio</h2>
            <p className="text-sm text-skin-warm-gray mb-3">
              Autorizas el uso de tus fotografías para realizar el análisis de piel y generar
              recomendaciones personalizadas. Sin este consentimiento no puedes usar la app.
            </p>
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={serviceGranted}
                onChange={(e) => setServiceGranted(e.target.checked)}
                className="mt-1 text-skin-sage"
              />
              <span> Acepto el tratamiento de mis fotografías para prestarme el servicio.</span>
            </label>
          </div>

          <div className="border-t pt-4">
            <h2 className="font-bold text-skin-warm-gray mb-2">Consentimiento B — Investigación y entrenamiento de IA</h2>
            <p className="text-sm text-skin-warm-gray mb-3">
              Autorizas el uso de tus fotografías para investigación y entrenamiento de nuestros
              propios modelos de IA. Es voluntario, independiente y no premarcado. Puedes usar el
              servicio aunque lo rechaces.
            </p>
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={trainingGranted}
                onChange={(e) => setTrainingGranted(e.target.checked)}
                className="mt-1 text-skin-sage"
              />
              <span> Acepto que mis imágenes se usen para investigación y entrenamiento de IA.</span>
            </label>
          </div>

          {error && <p className="text-sm text-red-600 text-center">{error}</p>}

          <div className="flex gap-3">
            <button
              onClick={handleSaveAndContinue}
              disabled={loading}
              className="flex-1 py-3 bg-skin-sage text-white font-medium rounded-lg disabled:opacity-50 hover:bg-skin-warm-gray transition"
            >
              {loading ? "Guardando..." : "Guardar y continuar"}
            </button>
            <button
              onClick={continueToPhotos}
              disabled={loading || !serviceGranted}
              className="flex-1 py-3 bg-white border border-skin-beige text-skin-warm-gray font-medium rounded-lg hover:bg-skin-beige transition"
            >
              Solo consentimiento A (saltar B)
            </button>
          </div>

          <p className="text-xs text-skin-warm-gray text-center">
            Puedes retirar cualquier consentimiento desde Configuración y Privacidad en cualquier momento.
          </p>
        </div>
      </div>
    </div>
  );
}
