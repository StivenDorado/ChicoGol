from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Cancha, ResenaCancha


class CanchasViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("jugador", password="ClaveSegura123!")
        self.cancha = Cancha.objects.create(
            nombre="Cancha Popayán Norte",
            ciudad="Popayán",
            barrio="Bolívar",
            direccion="Carrera 6 # 4-20",
            modalidad="f5",
            latitud="2.444800",
            longitud="-76.614700",
        )

    def test_list_renders_existing_courts_without_raw_empty_marker(self):
        response = self.client.get(reverse("canchas:lista"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cancha Popayán Norte")
        self.assertNotContains(response, "{empty}")
        self.assertNotContains(response, "Aún no hay canchas con ese filtro")

    def test_empty_message_only_renders_for_an_empty_filtered_queryset(self):
        response = self.client.get(reverse("canchas:lista"), {"q": "No existe esta cancha"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aún no hay canchas con ese filtro")
        self.assertNotContains(response, "{empty}")

    def test_detail_renders_existing_court(self):
        cancha = Cancha.objects.create(
            nombre="Cancha Sin Coordenadas",
            ciudad="Popayán",
            direccion="Carrera 9 # 8-7",
        )
        response = self.client.get(reverse("canchas:detalle", args=[cancha.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cancha Sin Coordenadas")

    def test_create_requires_authentication(self):
        response = self.client.get(reverse("canchas:crear"))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_create_page_has_map_and_upload_control(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("canchas:crear"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cancha-create-map")
        self.assertContains(response, "data-court-photo")

    def test_authenticated_create_saves_active_court(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("canchas:crear"), {
            "nombre": "Cancha Nueva",
            "direccion": "Calle 5 # 4-20",
            "ciudad": "Popayán",
            "barrio": "Centro",
            "precio_hora": 80000,
            "tipo": "sintetica",
            "modalidad": "f5",
            "servicios": "Duchas, iluminación",
            "descripcion": "Cancha de prueba",
            "latitud": "2.444800",
            "longitud": "-76.614700",
        })
        self.assertEqual(response.status_code, 302)
        cancha = Cancha.objects.get(nombre="Cancha Nueva")
        self.assertTrue(cancha.activa)
        self.assertRedirects(response, reverse("canchas:detalle", args=[cancha.pk]))

    def test_popayan_requires_a_known_neighborhood(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("canchas:crear"), {
            "nombre": "Cancha Inválida", "direccion": "Calle 1", "ciudad": "Popayán",
            "barrio": "Zona Inventada", "precio_hora": 0, "tipo": "natural", "modalidad": "f8",
            "latitud": "2.444800", "longitud": "-76.614700",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Cancha.objects.filter(nombre="Cancha Inválida").exists())

    def test_authenticated_user_can_create_and_update_one_review(self):
        self.client.force_login(self.user)
        url = reverse("canchas:guardar_resena", args=[self.cancha.pk])
        response = self.client.post(url, {"calificacion": 5, "comentario": "Excelente cancha para jugar."})
        self.assertRedirects(response, reverse("canchas:detalle", args=[self.cancha.pk]))
        review = ResenaCancha.objects.get(cancha=self.cancha, usuario=self.user)
        self.assertEqual(review.calificacion, 5)
        self.client.post(url, {"calificacion": 4, "comentario": "Muy buena, volvería a jugar."})
        self.assertEqual(ResenaCancha.objects.filter(cancha=self.cancha, usuario=self.user).count(), 1)
        review.refresh_from_db()
        self.assertEqual(review.calificacion, 4)

    def test_review_requires_authentication(self):
        response = self.client.post(reverse("canchas:guardar_resena", args=[self.cancha.pk]), {"calificacion": 5, "comentario": "Comentario"})
        self.assertEqual(response.status_code, 302)
