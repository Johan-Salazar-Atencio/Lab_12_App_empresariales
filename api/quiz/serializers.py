"""Serializers for the quiz API.

The models keep the names of the original lab (Exam, Question, Choice). The nested answer
options are exposed through ``OptionSerializer``, which is the name the lab uses for them.
"""
from django.db import transaction
from rest_framework import serializers

from .models import Choice, Exam, Question


class OptionSerializer(serializers.ModelSerializer):
    """An answer option nested inside a question; it has no question identifier of its own."""

    class Meta:
        model = Choice
        fields = ["id", "text", "is_correct"]


class ChoiceSerializer(OptionSerializer):
    """Standalone representation of a choice, used by the /choices/ resource."""

    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())

    class Meta(OptionSerializer.Meta):
        fields = ["id", "question", "text", "is_correct"]


class ExamSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ["id", "title", "created_at", "question_count"]
        read_only_fields = ["created_at"]

    def get_question_count(self, exam) -> int:
        # The viewset annotates the count; fall back to a query for fresh instances.
        count = getattr(exam, "question_count", None)
        return count if count is not None else exam.questions.count()


class QuestionSerializer(serializers.ModelSerializer):
    # Choices travel nested inside the question; the exam travels as an identifier.
    choices = OptionSerializer(many=True, allow_empty=False)

    class Meta:
        model = Question
        fields = ["id", "exam", "text", "choices", "created_at"]
        read_only_fields = ["created_at"]

    def validate_choices(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Una pregunta necesita al menos dos opciones.")
        if sum(1 for choice in value if choice.get("is_correct")) != 1:
            raise serializers.ValidationError("Debe haber exactamente una opción correcta.")
        return value

    def create(self, validated_data):
        choices = validated_data.pop("choices")
        with transaction.atomic():
            question = Question.objects.create(**validated_data)
            Choice.objects.bulk_create(Choice(question=question, **choice) for choice in choices)
        return question

    def update(self, instance, validated_data):
        choices = validated_data.pop("choices", None)
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            if choices is not None:  # sent choices replace the old ones
                instance.choices.all().delete()
                Choice.objects.bulk_create(Choice(question=instance, **choice) for choice in choices)
        return instance
