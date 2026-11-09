# Skin Intelligence MVP — Facial y Moda (Fase 1)

Objetivo: prototipo funcional del módulo Skin Intelligence de la aplicación
"Facial y Moda". Registro, login, perfiles, consentimiento de fotografías,
captura de 3 fotos del rostro, cuestionario de piel, análisis visual en modo
demostración, perfil orientativo de piel, motor de recomendaciones de rutina
(mañana/noche), catálogo de productos/ingredientes, panel de resultados e
historial. Rama: `master` (sin commits todavía). Entrega: monorepo único con
`backend/`, `frontend/`, `mobile/`, `docker-compose.yml`.

Runners: backend `.venv/bin/python -m pytest`; frontend `npm test` / `npm run
lint`; mobile `flutter test`.

## Specs

S1 — Monorepo en `C:\Users\Administrador\Documents\proyect\asesor_ia` con
`backend/` (FastAPI + Python), `frontend/` (React + Vite + TypeScript),
`mobile/` (Flutter), `docker-compose.yml` y `.gitignore` en la raíz.

S2 — Backend FastAPI con arquitectura por capas (`api/`, `services/`,
`repositories/`, `models/`, `schemas/`, `core/`). Arquitectura preparada para
PostgreSQL (DATABASE_URL) con fallback SQLite.

S3 — Módulo de IA desacoplado en `backend/app/services/ai/`:
`SkinAnalysisEngine` con interfaz de proveedor. Proveedor por defecto:
`DemoAnalysisProvider` (status "demo", sin puntuaciones de confianza ni
predicciones simuladas). Interfaz preparada para sustituir por PyTorch/OpenCV
o API multimodal posterior sin cambiar el contrato.

S4 — Modelo de datos relacional en PostgreSQL: usuarios, perfiles,
cuestionarios y respuestas, consentimientos (A y B), fotografías, análisis
visuales, perfiles de piel, productos, ingredientes, rutinas y pasos de rutina.

S5 — Autenticación JWT segura. Endpoints protegidos por usuario. No hay
autenticación en esta fase salvo la infraestructura JWT lista para activar.

S6 — Endpoints REST (prefijo `/api/v1`):
`POST /auth/register`, `POST /auth/login`, `GET /users/me`,
`POST /photos/consent`, `POST /photos/upload`, `GET /photos`,
`POST /questionnaires`, `GET /questionnaires/{id}`,
`POST /analysis`, `GET /analysis/{id}`,
`GET /skin-profile`, `GET /recommendations`,
`GET /products`, `GET /products/{id}`,
`GET /ingredients`, `GET /routines`, `GET /routines/{id}`,
`GET /consentments`, `POST /consentments/withdraw`.

S7 — Consentimiento de fotografías con dos autorizaciones independientes:
Consentimiento A (tratamiento para prestar el servicio) y Consentimiento B
(investigación/entrenamiento, voluntario, no premarcado). El servicio debe
funcionar aunque se rechace B. Registro de consentimiento con:
usuario, tipo, estado, fecha/hora, versión del texto, finalidad. Posibilidad
de retirar consentimiento.

S8 — Captura de fotografías: frontend solicita 3 fotos (frontal, mejilla
izquierda, mejilla derecha) con instrucciones de iluminación, sin filtros, sin
maquillaje preferiblemente, rostro visible. Vista previa antes de confirmar.
Posibilidad de repetir o eliminar cada foto. Validación de tamaño y formato en
backend. Almacenamiento privado, no público.

S9 — Cuestionario de piel dividido en pasos (información general, tipo de piel,
sensibilidad, hábitos, preferencias). Permite "No sé" / "No estoy seguro". No
obliga a responder lo que no se pueda contestar.

S10 — SkinAnalysisEngine en modo demostración retorna respuesta estructurada:
`analysisStatus: "demo"`, `modelVersion: null`, observaciones (`visibleAcne`,
`visibleSpots`, `redness`, `shine`, `texture`) en `null`, `confidence: null`,
`limitations: []`. Texto visible: "Análisis visual de demostración: resultados
orientativos, todavía no generados por un modelo de IA validado".

S11 — SkinProfileService combina respuestas del cuestionario + observaciones
visuales (cuando sean reales) + historial. Perfil orientativo que distinga qué
datos son declarados vs. visuales vs. demostración. No afirma diagnóstico
clínico.

S12 — Catálogo de productos e ingredientes. Productos con: id, nombre, marca,
categoría, descripción, INCI, activos, función, concentración (si declarada),
advertencias, precio, imagen, disponibilidad. Ingredientes con: nombre INCI,
nombre común, función, descripción, precauciones, evidencia, fuentes. Datos de
prueba claramente identificados como ficticios para la demo.

S13 — SkinRecommendationEngine genera rutina de mañana (limpieza, hidratación,
protección solar) y noche (limpieza, tratamiento cuando sea apropiado,
hidratación). Explica por qué cada producto/paso, función del ingrediente,
modo de uso, precauciones, incompatibilidades de activos. No recomienda
tratamientos médicos ni cura de enfermedades. Deriva a profesional sanitario
ante síntomas importantes.

S14 — Panel de resultados moderno, premium y minimalista (blanco, beige, crema,
verde suave, gris cálido). Presenta perfil orientativo, datos declarados,
observaciones visuales, preocupaciones, rutinas mañana/noche, productos,
explicaciones y advertencias. Indicadores visuales que distinguen resultados
reales de demostración.

S15 — Historial: análisis anteriores, cuestionarios, rutinas, productos,
cambios en características declaradas, fotografías (si se autorizó conservación).
No afirma evolución clínica por comparación de fotos.

S16 — Frontend React + Vite + TypeScript + SCSS/CSS modular, responsive,
priorizando móvil. Acceso a cámara del navegador cuando esté disponible.
Pantallas: bienvenida, registro/login, dashboard, perfil, captura de fotos,
consentimiento, cuestionario, procesamiento, resultados, rutina mañana, rutina
noche, catálogo, detalle de producto, historial, configuración y privacidad.

S17 — Seguridad: validación de archivos, límites de tamaño/formato, almacenamiento
privado, cifrado en tránsito (HTTPS en producción), control de acceso a
fotografías, registro de consentimientos, gestión de retirada, política de
conservación. Datos ficticios para pruebas de desarrollo.

## Tasks

| ID | Specs | Ruta | Estado | Evidencia |
|----|-------|------|--------|-----------|
| T1 | S1, S2, S4 | inline | pending | Estructura de carpetas backend/frontend creada |
| T2 | S1, S4 | inline | pending | docker-compose con PostgreSQL + backend; variables de entorno |
| T3 | S4 | inline | pending | Modelos SQLAlchemy y tablas PostgreSQL (usuarios, consentimientos, fotos, cuestionarios, productos, ingredientes, rutinas) |
| T4 | S5, S6 | inline | done | Auth JWT register/login/me; CORS; modelos User/Consent/Photo/Questionnaire |
| T5 | S7, S8 | inline | done | Consentimientos A/B y subida de fotografías con validación |
| T6 | S9 | inline | done | Cuestionario de piel en frontend (pasos, "No sé", multi-respuesta) |
| T7 | S3, S10 | inline | pending | SkinAnalysisEngine con proveedor demo |
| T8 | S11 | inline | pending | SkinProfileService y perfil orientativo |
| T9 | S12 | inline | pending | Catálogo productos/ingredientes (datos de prueba) |
| T10 | S13 | inline | pending | SkinRecommendationEngine y rutinas mañana/noche |
| T11 | S14, S16 | inline | done | Pantallas frontend: login, registro, consentimiento, captura, cuestionario, perfil, dashboard |
| T12 | S15 | inline | pending | Historial del usuario |
| T13 | S16 | inline | done | Navegación y pantallas restantes (bienvenida, perfil) |
| T14 | S17 | inline | pending | Pruebas de seguridad, validación de archivos, retirada de consentimiento |
| T15 | S1-S17 | inline | pending | Pruebas integrales fase por fase; ajuste de errores |

## Log

L1 — Requisitos originales (registrados en la sesión): prototipo funcional de
"Facial y Moda – Skin Intelligence" con registro, consentimiento separado A/B,
3 fotografías del rostro, cuestionario, análisis visual demostración, perfil
orientativo, motor de recomendaciones, catálogo, resultados e historial. Stack:
React + Vite + TypeScript frontend, FastAPI + PostgreSQL backend, Python/PyTorch
preparado para IA futura.
