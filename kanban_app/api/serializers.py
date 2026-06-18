from rest_framework import serializers
from django.contrib.auth import get_user_model
from auth_app.api.serializers import UserSerializer
from kanban_app.models import Board, Task


User = get_user_model()

class BoardSerializer(serializers.ModelSerializer):
    """Serializes a board with computed counts; accepts members on create."""

    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True
    )

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "members",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()

    def create(self, validated_data):
        members = validated_data.pop("members")
        owner = self.context["request"].user
        board = Board.objects.create(owner=owner, **validated_data)
        board.members.set(members)
        board.members.add(owner)
        return board

class TaskSerializer(serializers.ModelSerializer):
    """Serializes a task with nested user objects for reading."""

    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()

class BoardDetailSerializer(serializers.ModelSerializer):
    """Serializes a single board with nested members and tasks."""

    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    members = UserSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "owner_id",
            "members",
            "tasks",
        ]

class BoardUpdateSerializer(serializers.ModelSerializer):
    """Updates a board's title and members and returns nested owner and members."""

    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True
    )
    owner_data = UserSerializer(source="owner", read_only=True)
    members_data = UserSerializer(source="members", many=True, read_only=True)

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "members",
            "owner_data",
            "members_data",
        ]

    def update(self, instance, validated_data):
        members = validated_data.pop("members", None)
        instance.title = validated_data.get("title", instance.title)
        instance.save()
        if members is not None:
            instance.members.set(members)
        return instance