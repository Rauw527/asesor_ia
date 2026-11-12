# Probar Facial y Moda en Android

## En este PC

1. Abre `C:\Users\User\Desktop\proyecto\asesor_ia`.
2. Haz doble clic en `INICIAR_DEMO.cmd`. Deja esa ventana abierta: es el servidor.
3. Conecta tu teléfono al mismo Wi-Fi que el PC.
4. Copia `facial-y-moda-demo.apk` al teléfono y ábrelo para instalarlo.
5. En la pantalla de acceso despliega **Conexión con el servidor** e introduce
   `http://192.168.0.241:8000`.
6. Pulsa **Quiero crear una cuenta**, completa tus datos y entra.

La IP indicada se observó en este PC durante la preparación y puede cambiar.
Si no conecta, ejecuta `ipconfig` en el PC y busca la IPv4 de tu conexión Wi-Fi
o Ethernet. En un teléfono físico no uses `localhost` ni `10.0.2.2`.
Si Windows pregunta por acceso de red al servidor, la prueba necesita permitir
la conexión desde tu red privada. No hace falta abrirlo a internet.

El APK está firmado como versión de prueba; no está publicado en Google Play.
Si ya hay una instalación anterior con una firma distinta, Android puede impedir
actualizarla. Desinstalar esa versión borra sus datos locales; consérvalos primero
si los necesitas. No se comprobó ese caso en tu teléfono.

## Recorrido sugerido

1. Completa **Cuéntanos sobre tu piel**. Puedes omitir preguntas o indicar que no sabes.
2. Abre **Mi perfil y mis rutinas** para ver la guía de mañana y noche.
3. Marca los pasos realizados en **Seguimiento diario**. Sal y vuelve a entrar para
   comprobar que el servidor conserva el registro.
4. Opcionalmente abre **Mis fotografías**, selecciona frente y ambas mejillas,
   revisa la vista previa y pulsa guardar. Se solicitará permiso A si aún no existe.
5. En **Privacidad y fotografías** comprueba tus fotos, elimina una y gestiona
   tus autorizaciones. Dejar B desactivado no bloquea el servicio.

Las fotos no se envían a Gemini. No hay mediciones reales de hidratación o mejora,
entrenamiento ni diagnóstico dermatológico. La guía se basa en respuestas declaradas
y reglas básicas de demostración. El consentimiento B solo registra interés futuro.

## Qué está comprobado y qué falta

Se compilaron el APK y su firma. Se comprobaron permisos, servidor y pantallas
mediante pruebas automatizadas y vistas previas con datos ficticios. Falta probar
la instalación, cámara, galería y conectividad en su teléfono Android físico:
no había un dispositivo conectado durante la preparación.

El PC debe seguir encendido y el servidor abierto. Para funcionar fuera de su Wi-Fi
necesitarán un servidor HTTPS accesible; esta entrega no publica uno en internet.
Las sesiones se guardan solo en memoria: cerrar la app exige volver a entrar.

El código está en la rama local `mejora-demo-android`. No se enviaron cambios a GitHub.
El archivo de código fuente permite compartir la versión con tu amigo sin incluir
contraseñas, fotos, bases de datos ni herramientas instaladas.
