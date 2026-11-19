# ChicoGol

Base inicial de la plataforma de fútbol local: Django modular, templates server-rendered y MongoDB Atlas preparado para producción.

## Ejecutar en local

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py runserver 127.0.0.1:8080
```

Abre el proyecto en `http://127.0.0.1:8080/`.

Sin `MONGODB_URI`, el proyecto usa SQLite únicamente como fallback de desarrollo. Con una URI válida configurada explícitamente, `config/settings.py` cambia al backend oficial `django_mongodb_backend`.

La política CSP bloquea scripts, formularios, fuentes e imágenes de terceros por defecto. Si se añade un proveedor externo, debe declararse de forma explícita en `config/security.py`.

## Rutas disponibles

- `/` — portada pública.
- `/cuenta/registro/` e `/cuenta/iniciar-sesion/` — autenticación.
- `/cuenta/mi-cancha/` — perfil del jugador, requiere sesión.
- `/cuenta/perfil/` — vista del perfil del jugador, requiere sesión.
- `/canchas/` — catálogo con búsqueda y filtro por modalidad.
- `/canchas/<id>/` — detalle, servicios, precio y enlace de mapa.
- `/equipos/` — equipos activos, creación y detalle con integrantes.
- `/partidos/` — partidos abiertos, publicación e inscripción.
- `/social/jugadores/`, `/social/amigos/`, `/social/chats/` — comunidad, amistades y coordinación.
- `/notificaciones/` — avisos y marcado como leído.

La base local incluye tres canchas, un equipo y un partido de ejemplo para revisar el front. Los partidos tienen 11 cupos máximos: 10 titulares y 1 recambio. El detalle de cancha muestra un mapa pequeño embebido de OpenStreetMap y mantiene un enlace para abrirlo en grande. En producción, las canchas se gestionarán inicialmente desde `/admin/` y después se añadirá el flujo para propietarios.

## Estado funcional actual

- La navegación pública se limita a la landing; el resto de módulos requiere sesión y conserva el destino solicitado después del login.
- El perfil permite editar datos personales, datos deportivos y fotografía, con validaciones de tamaño y tipo.
- Notificaciones, solicitudes de amistad, perfiles públicos y chats asociados a equipos/partidos están disponibles.
- Cada partido admite como máximo 11 integrantes: 10 titulares y 1 recambio.

La protección parental y los flujos de autorización de acudiente deben mantenerse como una fase específica antes de habilitar participación de menores en producción.

No guardar imágenes o documentos en el disco de Vercel. Las credenciales deben vivir como variables de entorno.
