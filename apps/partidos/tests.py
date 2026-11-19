from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.canchas.models import Cancha
from apps.equipos.models import Equipo, SolicitudEquipo
from apps.notificaciones.models import Notificacion
from apps.social.models import ChatGrupo

from .models import InscripcionPartido, Partido


class CommunityFlowTests(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user("capitan", "capitan@example.com", "ClaveSegura123!")
        self.player = User.objects.create_user("jugador", "jugador@example.com", "ClaveSegura123!")
        self.cancha = Cancha.objects.create(
            nombre="Cancha Barrio Bolívar", ciudad="Popayán", barrio="Bolívar", direccion="Carrera 6 # 4-20",
            tipo="sintetica", modalidad="f5", latitud="2.444800", longitud="-76.614700",
        )

    def test_team_match_join_roles_capacity_chat_and_notification(self):
        self.client.login(username="capitan", password="ClaveSegura123!")
        response = self.client.post(reverse("equipos:crear"), {
            "nombre": "Barrio Unido", "ciudad": "Popayán", "nivel": "recreativo", "descripcion": "Parche de los miércoles",
        })
        self.assertEqual(response.status_code, 302)
        equipo = Equipo.objects.get(nombre="Barrio Unido")
        self.assertTrue(equipo.miembros.filter(pk=self.creator.pk).exists())

        self.client.logout()
        self.client.login(username="jugador", password="ClaveSegura123!")
        response = self.client.post(reverse("equipos:detalle", args=[equipo.pk]))
        self.assertRedirects(response, reverse("equipos:detalle", args=[equipo.pk]))
        solicitud = SolicitudEquipo.objects.get(equipo=equipo, solicitante=self.player)
        self.assertEqual(solicitud.estado, "pendiente")

        self.client.logout()
        self.client.login(username="capitan", password="ClaveSegura123!")
        self.client.post(reverse("equipos:gestionar_solicitud", args=[equipo.pk, solicitud.pk, "aceptar"]))
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, "aceptada")
        self.assertTrue(equipo.miembros.filter(pk=self.player.pk).exists())

        future = timezone.now() + timedelta(days=2)
        response = self.client.post(reverse("partidos:crear"), {
            "equipo": equipo.pk, "cancha": self.cancha.pk, "fecha": future.strftime("%Y-%m-%dT%H:%M"),
            "nivel": "recreativo", "descripcion": "Partido de prueba de integración",
        })
        self.assertEqual(response.status_code, 302)
        partido = Partido.objects.get(equipo=equipo)
        self.assertEqual(partido.cupos, 11)
        self.assertEqual(InscripcionPartido.objects.get(partido=partido, jugador=self.creator).rol, "titular")
        chat = ChatGrupo.objects.get(partido=partido)
        self.assertTrue(chat.miembros.filter(pk=self.creator.pk).exists())

        self.client.logout()
        self.client.login(username="jugador", password="ClaveSegura123!")
        self.client.post(reverse("partidos:detalle", args=[partido.pk]))
        joined = InscripcionPartido.objects.get(partido=partido, jugador=self.player)
        self.assertEqual(joined.estado, "aceptada")
        self.assertEqual(joined.rol, "titular")
        self.assertEqual(InscripcionPartido.objects.filter(partido=partido).count(), 2)
        self.client.post(reverse("partidos:detalle", args=[partido.pk]))
        self.assertEqual(InscripcionPartido.objects.filter(partido=partido, jugador=self.player).count(), 1)
        self.assertTrue(chat.miembros.filter(pk=self.player.pk).exists())
        self.assertTrue(Notificacion.objects.filter(usuario=self.creator, tipo="partido").exists())
        self.assertContains(self.client.get(reverse("partidos:lista")), "9/11")

        additional_players = []
        for index in range(2, 12):
            user = User.objects.create_user(f"jugador{index}", f"jugador{index}@example.com", "ClaveSegura123!")
            additional_players.append(user)
            self.client.logout()
            self.client.login(username=user.username, password="ClaveSegura123!")
            self.client.post(reverse("partidos:detalle", args=[partido.pk]))

        recambio = InscripcionPartido.objects.get(partido=partido, jugador=additional_players[8])
        self.assertEqual(recambio.rol, "recambio")
        self.assertEqual(InscripcionPartido.objects.filter(partido=partido, estado="aceptada").count(), 11)
        self.assertEqual(partido.cupos_disponibles, 0)

        blocked = additional_players[9]
        self.client.logout()
        self.client.login(username=blocked.username, password="ClaveSegura123!")
        self.client.post(reverse("partidos:detalle", args=[partido.pk]))
        self.assertFalse(InscripcionPartido.objects.filter(partido=partido, jugador=blocked).exists())
        self.assertEqual(self.client.get(reverse("partidos:lista")).status_code, 200)

    def test_private_match_routes_redirect_anonymous_users(self):
        self.assertEqual(self.client.get(reverse("partidos:lista")).status_code, 302)
        self.assertEqual(self.client.get(reverse("partidos:crear")).status_code, 302)

    def test_create_match_shows_only_active_courts(self):
        Cancha.objects.create(nombre="Cancha cerrada", ciudad="Popayán", barrio="Centro", direccion="Calle 1", activa=False)
        equipo = Equipo.objects.create(nombre="Equipo prueba", ciudad="Popayán", nivel="recreativo", creador=self.creator)
        equipo.miembros.add(self.creator)
        self.client.force_login(self.creator)
        response = self.client.get(reverse("partidos:crear"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cancha Barrio Bolívar")
        self.assertNotContains(response, "Cancha cerrada")
        self.assertContains(response, "Cancha disponible")
