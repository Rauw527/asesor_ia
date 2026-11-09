import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "@/services/api";

type PhotoType = "frontal" | "left_cheek" | "right_cheek";

const PHOTO_LABELS: Record<PhotoType, string> = {
  frontal: "Fotografía frontal",
  left_cheek: "Mejilla izquierda",
  right_cheek: "Mejilla derecha",
};

const INSTRUCTIONS = [
  "Busca una iluminación uniforme, sin sombras fuertes.",
  "Evita usar filtros o retoques.",
  "Evita fotografías borrosas o con movimiento.",
  "Mantén el rostro completamente visible.",
  "Evita maquillaje cuando sea posible.",
  "Mantén una distancia adecuada de la cámara (unos 30–40 cm).",
];

export default function PhotoCapture() {
  const [photos, setPhotos] = useState<Record<PhotoType, File | null>>({
    frontal: null,
    left_cheek: null,
    right_cheek: null,
  });
  const [previews, setPreviews] = useState<Record<PhotoType, string | null>>({
    frontal: null,
    left_cheek: null,
    right_cheek: null,
  });
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleFileChange = (type: PhotoType, e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setPhotos((prev) => ({ ...prev, [type]: file }));
    setPreviews((prev) => ({ ...prev, [type]: URL.createObjectURL(file) }));
  };

  const removePhoto = (type: PhotoType) => {
    setPhotos((prev) => ({ ...prev, [type]: null }));
    setPreviews((prev) => ({ ...prev, [type]: null }));
  };

  const allCaptured = Object.values(photos).every(Boolean);

  const handleUpload = async () => {
    setUploading(true);
    setMessage("");
    try {
      for (const [type, file] of Object.entries(photos) as [PhotoType, File | null][]) {
        if (file) {
          await authService.uploadPhoto(type, file);
        }
      }
      setMessage("Tus fotos se subieron correctamente.");
      setTimeout(() => navigate("/cuestionario"), 1200);
    } catch (err: any) {
      setMessage(
        err.response?.data?.detail || "Error al subir las fotos. Intenta de nuevo."
      );
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-skin-cream p-4">
      <div className="max-w-lg mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-skin-warm-gray">Captura de fotografías</h1>
          <p className="text-skin-sage text-sm">Tómate 3 fotos del rostro</p>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-skin-beige mb-6">
          <h3 className="font-bold text-skin-warm-gray mb-3">Instrucciones antes de capturar</h3>
          <ul className="text-sm text-skin-warm-gray space-y-2 list-disc pl-5">
            {INSTRUCTIONS.map((inst, i) => (
              <li key={i}>{inst}</li>
            ))}
          </ul>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {["frontal", "left_cheek", "right_cheek"].map((type) => {
            const label = PHOTO_LABELS[type as PhotoType];
            const preview = previews[type as PhotoType];
            return (
              <div key={type} className="flex flex-col items-center gap-2">
                <label className="text-xs font-medium text-skin-warm-gray uppercase tracking-wider">
                  {label}
                </label>
                <div className="w-32 h-32 rounded-xl border-2 border-skin-beige overflow-hidden relative bg-skin-beige/30 flex items-center justify-center">
                  {preview ? (
                    <>
                      <img src={preview} alt={label} className="w-full h-full object-cover" />
                      <button
                        type="button"
                        onClick={() => removePhoto(type as PhotoType)}
                        className="absolute top-1 right-1 bg-red-500 text-white rounded-full w-6 h-6 text-xs flex items-center justify-center"
                      >
                        ×
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => (document.getElementById(`input-${type}`) as HTMLInputElement).click()}
                      className="w-full h-full flex flex-col items-center justify-center text-skin-sage hover:text-skin-warm-gray transition"
                    >
                      <span className="text-xl">📷</span>
                      <span className="text-xs mt-1">Capturar</span>
                    </button>
                  )}
                  <input
                    id={`input-${type}`}
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={(e) => handleFileChange(type as PhotoType, e)}
                  />
                </div>
              </div>
            );
          })}
        </div>

        {message && (
          <div className={`mb-4 p-3 rounded-lg text-sm font-medium ${
            message.includes("correctamente") ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
          }`}>
            {message}
          </div>
        )}

        <div className="flex gap-3">
          <button
            onClick={handleUpload}
            disabled={uploading || !allCaptured}
            className="flex-1 py-3 bg-skin-sage text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-skin-warm-gray transition"
          >
            {uploading ? "Subiendo..." : "Confirmar y continuar"}
          </button>
          <button
            onClick={() => navigate("/cuestionario")}
            className="flex-1 py-3 bg-white border border-skin-beige text-skin-warm-gray font-medium rounded-lg hover:bg-skin-beige transition"
          >
            Omitir por ahora
          </button>
        </div>

        <p className="text-xs text-skin-warm-gray text-center mt-4">
          Tus fotos se almacenan de forma privada y solo tú puedes acceder a ellas.
        </p>
      </div>
    </div>
  );
}
