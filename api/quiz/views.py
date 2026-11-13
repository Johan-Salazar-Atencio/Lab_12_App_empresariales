from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import filters, viewsets

from .models import Choice, Exam, Question
from .serializers import ChoiceSerializer, ExamSerializer, QuestionSerializer


class ExamViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSerializer
    queryset = Exam.objects.annotate(question_count=Count("questions")).order_by("id")


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter("exam", int, description="Solo las preguntas de este examen."),
            OpenApiParameter("exam_id", int, description="Alias de `exam`."),
            OpenApiParameter("search", str, description="Texto buscado en el enunciado."),
        ]
    )
)
class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["exam"]
    search_fields = ["text"]

    def get_queryset(self):
        queryset = Question.objects.select_related("exam").prefetch_related("choices")
        exam_id = self.request.query_params.get("exam_id")
        if exam_id and exam_id.isdigit():
            queryset = queryset.filter(exam_id=int(exam_id))
        return queryset


class ChoiceViewSet(viewsets.ModelViewSet):
    serializer_class = ChoiceSerializer
    queryset = Choice.objects.select_related("question").order_by("id")
