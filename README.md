# Facial y Moda — demo Android

Demo funcional para organizar una rutina cosmética a partir de un cuestionario.
Cliente Flutter, servidor FastAPI y SQLite local. La web React se conserva como
referencia, pero el flujo principal de esta versión es Android.

## Qué funciona

- Registro, inicio de sesión y cierre de sesión. El token solo vive en memoria.
- Cuestionario de siete pasos con opciones desconocidas y posibilidad de omitir.
- Perfil basado en respuestas declaradas, sin transformar incertidumbre en sensibilidad baja.
- Rutinas básicas de mañana/noche, identificadas como reglas de demostración.
- Checklist diario persistente y racha por días con al menos un período completo.
- Captura o selección de tres fotos, vista previa y envío opcional.
- Consentimientos separados para guardar fotos y expresar interés futuro en entrenamiento.
- Fotos privadas: lectura y borrado requieren sesión y propiedad del recurso.
- Historial de capturas en modo demostración, sin predicciones ni porcentajes inventados.
- Registro histórico de decisiones de consentimiento con fecha, finalidad y versión.

El cuestionario y las rutinas funcionan aunque se rechacen ambos consentimientos.
El permiso de entrenamiento nunca es requisito para recibir el servicio.

## Límites de esta versión

No hay un modelo de piel entrenado ni validado. El generador usa reglas básicas;
no prescribe tratamientos, no elige productos concretos ni analiza su seguridad.
Las preferencias de tiempo y presupuesto se muestran, pero todavía no hay una
optimización del catálogo basada en ellas. No hay exportación de dataset ni entrenamiento.

La app no expone las herramientas antiguas de análisis Gemini, comparación e INCI.
Sus rutas del servidor requieren sesión y están desactivadas por defecto mediante
`ENABLE_EXPERIMENTAL_AI=false`. Activarlas es un experimento aparte: requiere
revisar permisos de proveedor, tratamiento de datos y validación de resultados.
No hace falta una clave Gemini para usar esta demo.

## Probar en tu teléfono

Consulta [PROBAR_ANDROID.md](PROBAR_ANDROID.md). El APK necesita un servidor;
no es una app autónoma sin conexión. La dirección se introduce en la pantalla
de acceso, por lo que no es necesario recompilar para cambiar de PC.

## Preparar el servidor en otro PC

Requisitos: Python 3.11 o superior. Verificado aquí con Python 3.12.

```powershell
cd backend
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-verified.txt
Copy-Item .env.example .env
.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

`requirements-verified.txt` fija las versiones usadas durante la comprobación
en Windows/Python 3.12. Los archivos `requirements.txt` y `requirements-dev.txt`
conservan los rangos generales para futuras actualizaciones deliberadas.

La base de datos y los archivos se crean en `backend/data/`. No se requieren
PostgreSQL, Redis ni Docker para la demo. Las tablas nuevas se crean al iniciar;
no se eliminan tablas existentes. Conserva copia de datos antes de actualizar
una instalación que ya contenga información importante.

La configuración local usa una clave de sesión privada generada. Si no hay
`SECRET_KEY` en desarrollo se genera una temporal en memoria: reiniciar el
servidor invalida las sesiones. En producción se exige una clave explícita de
al menos 32 caracteres. Nunca subas `.env`, bases de datos o fotos a GitHub.

## Compilar Android

Requisitos: Flutter 3.41.9 / Dart 3.11.5 o versión compatible, JDK 17 o superior
y herramientas Android. El proyecto conserva sus versiones de Gradle y plugins.

```powershell
cd mobile
flutter pub get
flutter analyze
flutter test
flutter build apk --debug
```

APK: `mobile/build/app/outputs/flutter-apk/app-debug.apk`.
La versión debug permite HTTP para pruebas en red local. El manifiesto principal
desactiva tráfico HTTP en compilaciones de distribución; para internet usa HTTPS.
La app rechaza direcciones HTTP ajenas a localhost o rangos privados.
No se habilitan copias de seguridad de datos de la app en Android.

## Verificación

```powershell
cd backend
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m ruff check .
```

Pruebas del servidor: autenticación, aislamiento entre dos cuentas, consentimiento,
subida inválida, fotos privadas, borrado de archivo, demo visual, perfil/rutinas,
checklist y contratos heredados protegidos. Las pruebas usan SQLite temporal,
imágenes sintéticas y dobles del proveedor: no envían imágenes a Gemini.

Las pruebas Flutter comprueban acceso, cierre de sesión, cuestionario, permisos,
envío del token en HTTP y manejo de sesiones caducadas, además de contratos de datos.
Las vistas previas usan datos ficticios y tamaño de teléfono; no sustituyen
una prueba de cámara e instalación en un Android físico.

## Rutas principales

Todas las rutas personales exigen `Authorization: Bearer <token>`.

| Método | Ruta bajo `/api/v1` | Uso |
|---|---|---|
| POST | `/auth/register`, `/auth/login` | Cuenta y sesión |
| GET | `/users/me` | Mi perfil |
| GET / POST | `/consents` | Decisiones de privacidad |
| GET / POST | `/photos` | Mis fotos / subida con permiso A |
| GET / DELETE | `/photos/{id}/content`, `/photos/{id}` | Leer / eliminar mi foto |
| GET / POST | `/questionnaires/latest`, `/questionnaires` | Cuestionario |
| POST | `/skin-profile/build` | Construir perfil declarado |
| POST | `/recommendations?routine_type=morning` o `night` | Generar guía demo |
| GET | `/recommendations` | Mis rutinas guardadas |
| GET / POST | `/routine/today`, `/routine/checkin` | Seguimiento diario |
| POST / GET | `/analysis`, `/analysis/history` | Registrar / consultar demo visual |
| GET | `/analysis/records/{id}` | Un análisis propio |
| GET | `/catalog/products` | Catálogo de referencia, separado de productos propios |
| GET / POST | `/products` | Mis productos, separado del catálogo |

Estado: `/health`. Documentación interactiva: `/docs`.
`/media/...` ya no publica una carpeta: comprueba sesión y propiedad de cada
archivo del historial heredado.

## Privacidad y próximos pasos

Las fotos permanecen en el servidor configurado hasta que su dueño las elimine.
Retirar el permiso A bloquea nuevas subidas y análisis; el borrado de fotos
existentes se realiza desde la pantalla de privacidad. El permiso B registra
una preferencia futura y no autoriza usos indefinidos: esta demo no exporta datos.

Antes de un piloto externo: desplegar con HTTPS, definir país y política de
conservación, revisar textos de consentimiento y reglas cosméticas, añadir límites
de solicitudes, monitorización, recuperación de cuenta y procedimientos de borrado
de copias de seguridad. Se necesita revisión y validación adicional para convertir
esta demo local en un producto comercial.
