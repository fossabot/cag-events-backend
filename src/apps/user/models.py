import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, username, email, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError("The given username must be set")

        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    uuid = models.UUIDField("uuid", primary_key=True, db_index=True, default=uuid.uuid4)
    username = models.CharField("username", unique=True, db_index=True, max_length=50)
    pretty_username = models.CharField("pretty username", unique=True, max_length=50)
    first_name = models.CharField("first name", max_length=50, blank=True)
    last_name = models.CharField("last name", max_length=50, blank=True)
    email = models.EmailField("email address", blank=True)
    # If the user has access to the admin panel
    is_staff = models.BooleanField("staff status", default=False)
    # If the user can log into the site
    is_active = models.BooleanField("active", default=True)
    date_joined = models.DateTimeField("date joined", default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def clean(self):
        self.email = self.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the combined full name.
        """
        full_name = "{0} {1}".format(self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    birth_date = models.DateField("date of birth", null=True, blank=True)
    gender = models.CharField("gender", null=True, blank=True, max_length=50)
    country = models.CharField("country", null=True, blank=True, max_length=50)
    postal_code = models.CharField("postal code", null=True, blank=True, max_length=10)
    street_address = models.CharField("street address", null=True, blank=True, max_length=100)
    phone_number = models.CharField("phone number", null=True, blank=True, max_length=20)
    membership_years = models.CharField("membership years", null=True, blank=True, max_length=500)
    is_member = models.BooleanField("membership status", default=False)

    def __str__(self):
        return self.user.username

    def get_month(self):
        return "{0:02d}".format(self.birth_date.month)

    def get_day(self):
        return "{0:02d}".format(self.birth_date.day)

    def has_address(self):
        return self.street_address and self.postal_code


# class AliasType(models.Model):
#     description = models.CharField("Description", max_length=100, help_text="Short description")
#     profile_url = models.URLField("Profile url", blank=True, null=True, help_text="Url where profile info can be "
#                                   "retrieved. E.g. https://steamcommunity.com/id/")
#     activity = models.ManyToManyField("competition.Activity", related_name="alias_type")
#
#     def __unicode__(self):
#         return self.description
#
#
# class Alias(models.Model):
#     alias_type = models.ForeignKey(AliasType, on_delete=models.CASCADE)
#     nick = models.CharField("nick", max_length=40)
#     userprofile = models.ForeignKey(User, related_name="alias", on_delete=models.CASCADE)
#
#     def __unicode__(self):
#         return self.nick
#
#     class Meta:
#         unique_together = ("userprofile", "alias_type")