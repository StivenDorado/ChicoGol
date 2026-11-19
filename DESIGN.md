---
version: alpha
name: ChicoGol
description: "Producto deportivo local: una brújula cálida para encontrar cancha, equipo y partido cerca."
colors:
  ink: "#10201D"
  night: "#0B1514"
  paper: "#F5F2E9"
  primary: "#C6F35B"
  accent: "#FF8066"
  muted: "#71807B"
typography:
  display:
    fontFamily: "Space Grotesk, system-ui, sans-serif"
  sans:
    fontFamily: "Manrope, system-ui, sans-serif"
  utility:
    fontFamily: "DM Mono, ui-monospace, monospace"
rounded:
  DEFAULT: "22px"
  pill: "999px"
spacing:
  page-max: "1240px"
  section-gap: "124px"
components:
  button: { radius: "999px", height: "48px" }
  card: { radius: "22px" }
---

# ChicoGol Design System

## Overview

ChicoGol es una interfaz híbrida: la portada expresa la energía del fútbol local; los flujos de cuenta priorizan claridad, confianza y familiaridad. La referencia visual es una cancha de barrio al final de la tarde: líneas blancas, verde de césped y carteles impresos con tinta coral. La firma es la cancha inclinada en el hero, que convierte el campo en brújula y no en decoración.

La primera entrega habla a jugadores y capitanes en Colombia, en móvil y desktop, con español colombiano como idioma base. No debe parecer un marketplace frío, un panel corporativo ni una app de apuestas. La utilidad gana en formularios y navegación.

## Colors

El papel cálido es la superficie principal; `ink` y `night` sostienen el contraste. El verde lima es la acción primaria y el coral indica energía y atención, nunca error por sí solo. Errores usan texto coral oscuro y una superficie pálida para no depender del color únicamente.

## Typography

Space Grotesk lleva titulares y cifras expresivas; Manrope mantiene los textos y formularios legibles; DM Mono etiqueta datos cortos, fechas y metadatos. Los titulares usan tracking apretado, pero los controles y párrafos conservan medidas cómodas.

## Layout

La grilla pública llega a 1240px con gutters de 32px en desktop y 20px en móvil. Los bloques de marca tienen ritmo generoso; los formularios reducen la densidad para permitir completar sin fatiga. El breakpoint principal es 800px, donde la navegación pasa a menú y las tarjetas se apilan.

## Elevation & Depth

La profundidad se comunica con contraste tonal y una sola sombra suave (`--shadow`) para tarjetas flotantes. El fondo no usa blur ni superficies transparentes como estructura principal.

## Shapes

Las tarjetas usan 22px y los botones son cápsulas. El hero es la excepción expresiva, con una silueta de cancha redondeada. Bordes de inputs son discretos y aumentan contraste en foco.

## Components

Los botones tienen énfasis sólido y estados hover, focus-visible y disabled nativos. Los formularios tienen labels reales, `novalidate`, errores inline y protección CSRF. La navegación usa enlaces semánticos; el menú móvil es un botón con estado `aria-expanded`. El movimiento se reduce con `prefers-reduced-motion`.

## Do's and Don'ts

- **Do:** conservar acciones con verbos concretos: “Crear cuenta”, “Ingresar”, “Ver canchas”.
- **Do:** mantener el contraste y los targets táctiles cómodos.
- **Don't:** añadir mapas, rankings o torneos antes de validar la base de usuarios.
- **Don't:** usar una tarjeta oscura genérica para cada dato; la cancha debe seguir siendo el gesto visual distintivo.
