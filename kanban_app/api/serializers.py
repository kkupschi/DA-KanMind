from rest_framework import serializers
from django.contrib.auth import get_user_model
from auth_app.api.serializers import UserSerializer
from kanban_app.models import Board, Task, Comment


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
    """Serializes a task with nested user objects and writable assignee/reviewer ids."""

    STATUS_VALUES = ["to-do", "in-progress", "review", "done"]
    PRIORITY_VALUES = ["low", "medium", "high"]

    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assignee",
        write_only=True,
        required=False,
        allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="reviewer",
        write_only=True,
        required=False,
        allow_null=True,
    )
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
            "assignee_id",
            "reviewer",
            "reviewer_id",
            "due_date",
            "comments_count",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is not None:
            self.fields["board"].read_only = True

    def get_comments_count(self, obj):
        return obj.comments.count()

    def validate_status(self, value):
        if value not in self.STATUS_VALUES:
            raise serializers.ValidationError("Invalid status value.")
        return value

    def validate_priority(self, value):
        if value not in self.PRIORITY_VALUES:
            raise serializers.ValidationError("Invalid priority value.")
        return value

    def validate(self, attrs):
        board = attrs.get("board") or getattr(self.instance, "board", None)
        for user in (attrs.get("assignee"), attrs.get("reviewer")):
            if user and not board.members.filter(id=user.id).exists():
                raise serializers.ValidationError(
                    "Assignee and reviewer must be members of the board."
                )
        return attrs

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return Task.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("board", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

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

class CommentSerializer(serializers.ModelSerializer):
    """Serializes a task comment with the author's full name."""

    author = serializers.CharField(source="author.fullname", read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "created_at",
            "author",
            "content",
        ]