"""Lab 8 acceptance tests: full CRUD, deliberate errors and pagination.

Every request carries the person's token (staff), so the tests describe the API contract and
not the role rules (those live in test_permissions.py).
"""
from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from quiz.models import Exam, Question

from .helpers import exam_id, seed, valid_body


class CrudTests(APITestCase):
    def setUp(self):
        self.person, _ = seed()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.person}")

    def test_exam_crud_returns_the_expected_status_codes(self):
        create = self.client.post("/api/exams/", {"title": "Examen nuevo"}, format="json")
        self.assertEqual(create.status_code, 201)
        new_id = create.json()["id"]

        self.assertEqual(self.client.get("/api/exams/").status_code, 200)
        detail = self.client.get(f"/api/exams/{new_id}/")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["question_count"], 0)

        patch = self.client.patch(f"/api/exams/{new_id}/", {"title": "Renombrado"}, format="json")
        self.assertEqual(patch.status_code, 200)
        self.assertEqual(patch.json()["title"], "Renombrado")

        self.assertEqual(self.client.delete(f"/api/exams/{new_id}/").status_code, 204)
        self.assertEqual(self.client.get(f"/api/exams/{new_id}/").status_code, 404)

    def test_question_crud_returns_the_expected_status_codes(self):
        create = self.client.post("/api/questions/", valid_body(exam_id()), format="json")
        self.assertEqual(create.status_code, 201)
        created = create.json()
        new_id = created["id"]
        self.assertEqual(len(created["choices"]), 3)
        self.assertEqual(sum(choice["is_correct"] for choice in created["choices"]), 1)

        self.assertEqual(self.client.get("/api/questions/").status_code, 200)
        self.assertEqual(self.client.get(f"/api/questions/{new_id}/").status_code, 200)

        patch = self.client.patch(f"/api/questions/{new_id}/", {"text": "Enunciado corregido"}, format="json")
        self.assertEqual(patch.status_code, 200)
        self.assertEqual(patch.json()["text"], "Enunciado corregido")
        self.assertEqual(len(patch.json()["choices"]), 3)

        self.assertEqual(self.client.delete(f"/api/questions/{new_id}/").status_code, 204)
        self.assertEqual(self.client.get(f"/api/questions/{new_id}/").status_code, 404)

    def test_choice_crud_returns_the_expected_status_codes(self):
        question = Question.objects.first()
        body = {"question": question.id, "text": "Opcion nueva", "is_correct": False}

        create = self.client.post("/api/choices/", body, format="json")
        self.assertEqual(create.status_code, 201)
        new_id = create.json()["id"]

        self.assertEqual(self.client.get("/api/choices/").status_code, 200)
        self.assertEqual(self.client.get(f"/api/choices/{new_id}/").status_code, 200)

        patch = self.client.patch(f"/api/choices/{new_id}/", {"text": "Opcion editada"}, format="json")
        self.assertEqual(patch.status_code, 200)
        self.assertEqual(patch.json()["text"], "Opcion editada")

        self.assertEqual(self.client.delete(f"/api/choices/{new_id}/").status_code, 204)
        self.assertEqual(self.client.get(f"/api/choices/{new_id}/").status_code, 404)


class DeliberateErrorTests(APITestCase):
    def setUp(self):
        self.person, _ = seed()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.person}")

    def test_a_missing_required_field_is_400(self):
        body = valid_body(exam_id())
        del body["text"]
        response = self.client.post("/api/questions/", body, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("text", response.json())

    def test_a_wrong_data_type_is_400(self):
        body = valid_body(exam_id())
        body["exam"] = "no-es-un-numero"
        response = self.client.post("/api/questions/", body, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("exam", response.json())

    def test_zero_correct_options_is_400_and_saves_nothing(self):
        body = valid_body(exam_id())
        for choice in body["choices"]:
            choice["is_correct"] = False
        response = self.client.post("/api/questions/", body, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("exactamente una", str(response.json()))
        self.assertEqual(Question.objects.count(), 8)

    def test_two_correct_options_is_400_and_saves_nothing(self):
        body = valid_body(exam_id())
        body["choices"][1]["is_correct"] = True
        response = self.client.post("/api/questions/", body, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("exactamente una", str(response.json()))
        self.assertEqual(Question.objects.count(), 8)

    def test_a_missing_resource_is_404(self):
        for path in ("/api/exams/99999/", "/api/questions/99999/", "/api/choices/99999/"):
            self.assertEqual(self.client.get(path).status_code, 404, path)

    def test_delete_is_204_and_then_detail_is_404(self):
        question = Question.objects.first()
        self.assertEqual(self.client.delete(f"/api/questions/{question.id}/").status_code, 204)
        self.assertEqual(self.client.get(f"/api/questions/{question.id}/").status_code, 404)

    def test_an_anonymous_read_is_public_but_a_write_is_401(self):
        self.client.credentials()
        self.assertEqual(self.client.get("/api/questions/").status_code, 200)
        response = self.client.post("/api/questions/", valid_body(exam_id()), format="json")
        self.assertEqual(response.status_code, 401)


class BrowsableApiTests(APITestCase):
    def setUp(self):
        seed()

    def test_the_login_page_is_available(self):
        self.assertEqual(self.client.get("/api-auth/login/").status_code, 200)

    def test_an_anonymous_get_returns_the_api(self):
        response = self.client.get("/api/questions/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 8)

    def test_a_session_login_can_read_the_api(self):
        User.objects.create_user(username="navegador", password="clave-de-prueba")
        self.assertTrue(self.client.login(username="navegador", password="clave-de-prueba"))
        self.assertEqual(self.client.get("/api/questions/").status_code, 200)


class PaginationAndFilterTests(APITestCase):
    def setUp(self):
        self.person, _ = seed()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.person}")

    def test_pagination_splits_the_results_and_links_the_pages(self):
        first = self.client.get("/api/questions/").json()
        self.assertEqual(first["count"], 8)
        self.assertEqual(len(first["results"]), 5)
        self.assertIsNotNone(first["next"])
        self.assertIsNone(first["previous"])

        second = self.client.get("/api/questions/", {"page": 2}).json()
        self.assertEqual(len(second["results"]), 3)
        self.assertIsNotNone(second["previous"])
        self.assertIsNone(second["next"])

    def test_page_size_can_be_requested_by_the_client(self):
        data = self.client.get("/api/questions/", {"page_size": 8}).json()
        self.assertEqual((data["count"], len(data["results"])), (8, 8))

    def test_questions_can_be_filtered_by_exam(self):
        target = Exam.objects.get(title__contains="Plantillas").id
        self.assertEqual(self.client.get("/api/questions/", {"exam": target}).json()["count"], 4)

    def test_exam_id_is_accepted_as_an_alias(self):
        target = Exam.objects.get(title__contains="Plantillas").id
        self.assertEqual(self.client.get("/api/questions/", {"exam_id": target}).json()["count"], 4)

    def test_questions_can_be_searched_by_text(self):
        data = self.client.get("/api/questions/", {"search": "prefetch_related"}).json()
        self.assertEqual(data["count"], 1)
