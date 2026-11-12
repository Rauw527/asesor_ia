# Demo Android — estado verificado

Esta especificación sustituye como referencia de la demo a los dos planes anteriores.

- Plataforma principal: Flutter Android. Servidor FastAPI existente.
- Alcance entregado: cuenta, sesión en memoria, cuestionario, perfil declarado,
  rutinas básicas, checklist, fotos opcionales, consentimiento y privacidad.
- Fotografías con sesión y comprobación de dueño; no hay carpeta pública.
- Permiso A obligatorio para subir/analizar fotos, independiente de B.
- Decisiones de consentimiento registradas como eventos históricos.
- IA externa desactivada por defecto; el flujo Android no depende de Gemini.
- Sin entrenamiento, exportación de dataset, predicciones ni métricas clínicas.
- Validación: 37 pruebas del servidor, 13 pruebas Flutter, revisiones de código
  correctas y comprobación HTTP real del recorrido sin fotos.
- APK debug compilado y firma verificada; no publicado en tiendas ni GitHub.
- Pendiente de validación de dispositivo: instalación, cámara/galería y Wi-Fi
  en teléfono físico. No había un Android conectado.

Ver README.md y PROBAR_ANDROID.md para ejecución, contratos y límites.
