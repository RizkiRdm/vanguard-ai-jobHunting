from tortoise import fields, models
from core.security import mask_email


class User(models.Model):
    id = fields.UUIDField(primary_key=True)
    email = fields.CharField(max_length=100, unique=True, db_index=True)
    hashed_password = fields.CharField(max_length=255, null=True)
    auth_provider = fields.CharField(max_length=20, default="LOCAL")  # LOCAL, GOOGLE
    version = fields.IntField(default=1)  # Optimistic Locking
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    @property
    def masked_email(self):
        return mask_email(self.email)

    class Meta:
        table = "users"


class UserProfile(models.Model):
    id = fields.UUIDField(primary_key=True)
    user = fields.OneToOneField(
        "models.User", related_name="profile", on_delete=fields.CASCADE
    )
    starter_cv_path = fields.CharField(max_length=512, null=True)
    summary = fields.TextField(null=True)
    target_role = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "user_profiles"
