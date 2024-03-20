from django.db import models


class AdminModel(models.Model):
    """
    Model representing an admin of the travel agency's system.

    Attributes:
        admin_name (CharField): The name of the admin.
        password (CharField): The password of the admin.
    """
    admin_name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = 'admin_data'

    def __str__(self):
        return self.admin_name

# Create your models here.
