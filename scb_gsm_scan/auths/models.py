from django.db import models
from scb_gsm_scan.mixins import SlugifyMixin
from smart_selects.db_fields import ChainedManyToManyField

# Create your models here.
from django.contrib.auth.models import(
    AbstractBaseUser, 
    BaseUserManager, 
    PermissionsMixin, 
    Permission, 
    Group
)

class Role(models.Model, SlugifyMixin):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, unique=True, primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
    class Meta:
        unique_together = ('group', 'name')
        ordering = ('name',)

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
    Utilisateur système Django
    Peut être propriétaire d'atelier
    ou tailleur ou admin
    """
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, blank=True)
    roles = ChainedManyToManyField(
        Role,
        chained_field="groups",          # champ sur User
        chained_model_field="group",     # champ sur Role
        blank=True,
    )
    # user_permissions = models.ManyToManyField(Permission, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    
    class Meta:
        ordering = ('-date_joined',)

