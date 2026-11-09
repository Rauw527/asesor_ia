import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "@/services/api";

const QUESTIONS = [
  {
    key: "age",
    text: "¿Qué edad tienes?",
    type: "text",
  },
  {
    key: "main_concern",
    text: "¿Cuál es tu principal preocupación respecto a tu piel?",
    type: "single",
    options: [
      "Acné", "Manchas", "Brillo excesivo", "Sequedad", "Enrojecimiento",
      "Textura irregular", "Líneas de expresión", "Sensibilidad", "Otras",
    ],
  },
  {
    key: "skin_feeling",
    text: "¿Cómo sientes tu piel durante el día?",
    type: "single",
    options: ["Grasa", "Seca", "Mixta", "Normal", "No estoy seguro"],
  },
  {
    key: "after_wash",
    text: "¿Cómo se comporta tu piel después de lavarte el rostro?",
    type: "single",
    options: [
      "Se siente tirante o seca",
      "Se siente normal",
      "Comienza a producir grasa rápidamente",
      "Algunas zonas están secas y otras grasas",
      "No estoy seguro",
    ],
  },
  {
    key: "oily_zones",
    text: "¿En qué zonas notas mayor producción de grasa?",
    type: "multi",
    options: ["Frente", "Nariz", "Mentón", "Mejillas", "Todo el rostro", "No noto exceso de grasa"],
  },
  {
    key: "irritates_easily",
    text: "¿Tu piel suele irritarse con facilidad?",
    type: "single",
    options: ["Sí", "No", "Algunas veces", "No estoy seguro"],
  },
  {
    key: "sunscreen",
    text: "¿Utilizas protector solar?",
    type: "single",
    options: ["Sí", "No", "Algunas veces"],
  },
  {
    key: "cleanser",
    text: "¿Utilizas productos para limpiar tu rostro?",
    type: "single",
    options: ["Sí", "No", "Algunas veces"],
  },
  {
    key: "moisturizer",
    text: "¿Utilizas cremas hidratantes?",
    type: "single",
    options: ["Sí", "No", "Algunas veces"],
  },
  {
    key: "actives",
    text: "¿Actualmente utilizas productos con activos como retinol, vitamina C, niacinamida o ácido salicílico?",
    type: "single",
    options: ["Sí", "No", "No estoy seguro"],
  },
  {
    key: "routine",
    text: "¿Tienes una rutina de skincare establecida?",
    type: "single",
    options: ["Sí", "No", "No estoy seguro"],
  },
  {
    key: "goal",
    text: "¿Qué resultado te gustaría conseguir?",
    type: "text",
  },
  {
    key: "time",
    text: "¿Cuánto tiempo deseas dedicar a tu rutina?",
    type: "single",
    options: ["Menos de 5 minutos", "5-10 minutos", "10-20 minutos", "Más de 20 minutos"],
  },
  {
    key: "budget",
    text: "¿Cuál es tu presupuesto aproximado para productos?",
    type: "single",
    options: ["Bajo", "Medio", "Alto", "No tengo presupuesto definido"],
  },
];

export default function Questionnaire() {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const current = QUESTIONS[step];

  const isMulti = current.type === "multi";
  const currentValue = answers[current.key] || "";

  const handleSelect = (value: string) => {
    if (isMulti) {
      const currentList = currentValue ? currentValue.split(",") : [];
      const idx = currentList.indexOf(value);
      if (idx >= 0) {
        currentList.splice(idx, 1);
      } else {
        currentList.push(value);
      }
      setAnswers({ ...answers, [current.key]: currentList.join(",") });
    } else {
      setAnswers({ ...answers, [current.key]: value });
    }
  };

  const handleTextChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setAnswers({ ...answers, [current.key]: e.target.value });
  };

  const isAnswered = () => {
    if (!currentValue) return false;
    if (isMulti) return currentValue.split(",").length > 0;
    return true;
  };

  const goNext = () => {
    if (step < QUESTIONS.length - 1) {
      setStep(step + 1);
    } else {
      submit();
    }
  };

  const goPrev = () => {
    if (step > 0) setStep(step - 1);
  };

  const submit = async () => {
    setLoading(true);
    try {
      const payload = {
        answers: Object.entries(answers).map(([key, value]) => ({
          question_key: key,
          answer_value: value,
          answer_type: QUESTIONS.find((q) => q.key === key)?.type || "single",
        })),
      };
      await authService.saveQuestionnaire(payload);
      navigate("/resultados");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Error al guardar el cuestionario.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-skin-cream p-4">
      <div className="max-w-md mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-skin-warm-gray">Cuestionario de piel</h1>
          <p className="text-skin-sage text-sm">
            Paso {step + 1} de {QUESTIONS.length}
          </p>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-skin-beige">
          <div className="text-skin-sage text-xs mb-4">
            Puedes responder "No estoy seguro" o dejar en blanco si no sabes la respuesta.
          </div>

          <div className="mb-6">
            <h2 className="font-bold text-skin-warm-gray text-lg mb-4">{current.text}</h2>

            {current.type === "text" ? (
              <textarea
                required
                rows={3}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-skin-sage outline-none"
                value={currentValue}
                onChange={handleTextChange}
                placeholder="Escribe tu respuesta..."
              />
            ) : current.type === "multi" ? (
              <div className="space-y-2">
                {(current.options ?? []).map((opt) => {
                  const selected = currentValue.split(",").includes(opt);
                  return (
                    <button
                      key={opt}
                      type="button"
                      onClick={() => handleSelect(opt)}
                      className={`w-full text-left px-3 py-2 rounded-lg border transition ${
                        selected
                          ? "bg-skin-sage text-white border-skin-sage"
                          : "text-skin-warm-gray border-skin-beige hover:bg-skin-beige"
                      }`}
                    >
                      {opt}
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className="space-y-2">
                {(current.options ?? []).map((opt) => (
                  <button
                    key={opt}
                    type="button"
                    onClick={() => handleSelect(opt)}
                    className={`w-full text-left px-3 py-2 rounded-lg border transition ${
                      currentValue === opt
                        ? "bg-skin-sage text-white border-skin-sage"
                        : "text-skin-warm-gray border-skin-beige hover:bg-skin-beige"
                    }`}
                  >
                    {opt}
                  </button>
                ))}
              </div>
            )}
          </div>

          {error && <p className="text-sm text-red-600 text-center mb-4">{error}</p>}

          <div className="flex justify-between gap-3">
            {step > 0 && (
              <button
                onClick={goPrev}
                className="flex-1 py-3 bg-white border border-skin-beige text-skin-warm-gray font-medium rounded-lg hover:bg-skin-beige transition"
              >
                Anterior
              </button>
            )}
            <button
              onClick={goNext}
              disabled={loading || !isAnswered()}
              className={`flex-1 py-3 font-medium rounded-lg transition disabled:opacity-50 ${
                loading || !isAnswered()
                  ? "bg-skin-beige text-skin-warm-gray disabled:cursor-not-allowed"
                  : "bg-skin-sage text-white hover:bg-skin-warm-gray"
              }`}
            >
              {loading ? "Guardando..." : step === QUESTIONS.length - 1 ? "Finalizar" : "Siguiente"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
