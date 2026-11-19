# ChicoGol — contrato UX inicial

## Alcance

Esta fase cubre portada, registro, inicio de sesión, cierre de sesión, perfil de jugador, catálogo/detalle de canchas, equipos, partidos y la primera capa social. Parental, torneos, rankings y patrocinadores quedan fuera hasta validar esta base.

## Flujos

- Registro válido: valida fecha de nacimiento con mínimo 13 años, crea usuario con contraseña hasheada por Django, guarda la edad calculada, inicia sesión y vuelve a inicio.
- Registro inválido: conserva valores, muestra errores junto al campo y no pierde el formulario.
- Inicio de sesión válido: redirige a inicio; inválido: muestra un error genérico sin revelar si el usuario existe.
- Cierre de sesión: termina la sesión y vuelve a inicio.
- Perfil: una persona autenticada puede completar y actualizar datos personales, fotografía, ciudad colombiana, barrio, fecha de nacimiento, posición, nivel y bio; Popayán prioriza barrios propios y la fecha exige mínimo 13 años. El guardado muestra confirmación inline.
- Canchas: el catálogo muestra solo canchas activas, permite filtrar por texto y modalidad, y enlaza al detalle. Un visitante anónimo puede consultar canchas; el perfil requiere autenticación.
- Mapa: el detalle conserva la información de la cancha a la derecha y muestra un mapa compacto a la izquierda; el mapa grande se abre en OpenStreetMap en una pestaña externa.
- Equipos: cualquier usuario autenticado puede crear un equipo y queda como miembro inicial; el detalle permite a otros usuarios autenticados unirse.
- Partidos: un usuario publica un partido asociado a uno de sus equipos y una cancha activa; el creador queda inscrito y otros jugadores pueden ocupar cupos disponibles.
- Social: una persona puede buscar jugadores, enviar/aceptar amistades, consultar avisos y escribir en chats asociados a equipos o partidos.
- Plantilla: un partido admite como máximo 11 inscripciones: 10 titulares y 1 recambio. El detalle expone posiciones y cupos.

## Shells de navegación

- La landing pública es la única ruta que muestra los anclajes “Cómo funciona” y “Para quién”.
- Las rutas de aplicación muestran navegación operativa: Canchas, Equipos, Partidos, Jugadores, Chats, Notificaciones, Mi perfil y Salir. Las acciones privadas conservan el destino solicitado mediante `next` al pedir inicio de sesión.
- El perfil es una pantalla propia de usuario; su edición vive en “Editar perfil”. Las pantallas internas no enlazan de vuelta a secciones de marketing.

## Seguridad

Los formularios incluyen CSRF. La sesión usa HttpOnly y SameSite=Lax; en producción activa Secure, HSTS, hosts explícitos y `DEBUG=False`. No se almacenan secretos en el navegador ni en el repositorio.

## Accesibilidad y responsive

WCAG 2.2 AA como objetivo: HTML semántico, labels asociados, foco visible, navegación por teclado, reduced motion y menú móvil accesible. El contenido se apila por debajo de 800px sin scroll horizontal.
