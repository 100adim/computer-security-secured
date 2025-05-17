from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    salt = models.BinaryField()
    password_hash = models.CharField(max_length=64)

    # היסטוריית סיסמאות אחרונות
    previous_password_hash1 = models.CharField(max_length=64, blank=True)
    previous_password_hash2 = models.CharField(max_length=64, blank=True)
    previous_password_hash3 = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return self.username


class Package(models.Model):
    name = models.CharField(max_length=100)
    speed = models.CharField(max_length=50)  # לדוגמה: "100 Mbps"
    price = models.DecimalField(max_digits=6, decimal_places=2)
    sector = models.CharField(max_length=50)  # לדוגמה: "Business" או "Private"

    def __str__(self):
        return f"{self.name} ({self.speed})"


class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    id_number = models.CharField(max_length=20, unique=True)
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
