from django.db import models

class User(models.Model):
    user = models.CharField("User", max_length=150)
    email = models.EmailField()

    def __str__(self):
        return self.user

#next start mocking up a playlist/song collection model to store spot track data
