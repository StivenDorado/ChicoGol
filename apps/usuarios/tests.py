from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Perfil


class CuentaFlowTests(TestCase):
    def setUp(self):
        self.password = "Ritmo!Cancha#48"
        self.registration = {
            "first_name": "Ana",
            "last_name": "Jugadora",
            "username": "ana_jugadora",
            "email": "ana@example.com",
            "password1": self.password,
            "password2": self.password,
            "fecha_nacimiento": "2000-05-10",
        }

    def test_registration_creates_hashed_user_and_profile(self):
        response = self.client.post(reverse("usuarios:registro"), self.registration)

        self.assertRedirects(response, reverse("inicio"))
        user = User.objects.get(username="ana_jugadora")
        profile = Perfil.objects.get(usuario=user)

        self.assertTrue(user.check_password(self.password))
        self.assertNotEqual(user.password, self.password)
        self.assertEqual(user.email, "ana@example.com")
        self.assertEqual(profile.fecha_nacimiento, date(2000, 5, 10))
        self.assertEqual(self.client.session.get("_auth_user_id"), str(user.pk))

    def test_login_logout_and_private_match_redirect(self):
        User.objects.create_user(username="jugador", email="jugador@example.com", password=self.password)

        self.client.post(reverse("usuarios:logout"))
        private_response = self.client.get(reverse("partidos:lista"))
        self.assertRedirects(
            private_response,
            f"{reverse('usuarios:login')}?next={reverse('partidos:lista')}",
        )

        self.assertTrue(self.client.login(username="jugador", password=self.password))
        self.assertEqual(self.client.get(reverse("partidos:lista")).status_code, 200)
        self.client.post(reverse("usuarios:logout"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_profile_updates_persist_after_login_again(self):
        user = User.objects.create_user(
            username="persistente",
            email="persistente@example.com",
            password=self.password,
            first_name="Antes",
            last_name="Usuario",
        )
        profile = Perfil.objects.get(usuario=user)
        profile.fecha_nacimiento = date(2000, 5, 10)
        profile.save()

        self.assertTrue(self.client.login(username="persistente", password=self.password))
        response = self.client.post(
            reverse("usuarios:mi_cancha"),
            {
                "datos-first_name": "Después",
                "datos-last_name": "Persistente",
                "datos-email": "persistente@example.com",
                "ciudad": "Popayán",
                "barrio": "Centro",
                "fecha_nacimiento": "2000-05-10",
                "telefono": "3000000000",
                "posicion": "medio",
                "nivel": "intermedio",
                "bio": "Perfil guardado",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.client.post(reverse("usuarios:logout"))
        self.assertTrue(self.client.login(username="persistente", password=self.password))

        user.refresh_from_db()
        profile.refresh_from_db()
        self.assertEqual(user.get_full_name(), "Después Persistente")
        self.assertEqual(profile.bio, "Perfil guardado")
        self.assertEqual(profile.ciudad, "Popayán")
        self.assertContains(self.client.get(reverse("usuarios:perfil")), "Después Persistente")
