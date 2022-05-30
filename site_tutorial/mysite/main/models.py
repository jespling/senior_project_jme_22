from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.

# this class may or may not be in use...
class UserStat(models.Model):
    first_name = models.CharField(max_length=100, default='first')
    last_name = models.CharField(max_length=100, default='last')
    username = models.CharField(max_length=200, default='user')

    def __str__(self):
        return self.username


# this class links the userform to profileform for storing spotify username for data access
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    spotify_username = models.CharField(help_text="Spotify Username", max_length=200, blank=True)
    playlist_id = models.CharField(max_length=200, blank=True)
    friends = models.ManyToManyField("Profile", blank=True)

    def __str__(self):
        return self.user.username


class Friend_Request(models.Model):
    from_user = models.ForeignKey(Profile, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(Profile, related_name='to_user', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('from_user', 'to_user')


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class SongStat(models.Model):
    artist = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    artist_id = models.CharField(max_length=200, default='none')
    track_id = models.CharField(max_length=200, default='none')
    img_url = models.CharField(max_length=200, default='none')

    def __str__(self):
        return self.artist


class TrackStat(models.Model):
    user = models.IntegerField(blank=True, null=True)
    artist = models.CharField(max_length=200, default='none')
    title = models.CharField(max_length=200, default='none')
    track_id = models.CharField(max_length=200, default='none')
    img_url = models.CharField(max_length=200, default='none')
    release_date = models.CharField(max_length=200, default='none')
    # duration = models.BigIntegerField()
    duration = models.DecimalField(max_digits=5, decimal_places=2)
    snippet = models.URLField(max_length=200, default='none')
    rating = models.IntegerField(default=0, blank=True, null=True,
                                 validators=[
                                     MaxValueValidator(5),
                                     MinValueValidator(1)
                                 ])

    def __str__(self):
        return self.title


class ChartStat(models.Model):
    user = models.IntegerField(blank=True, null=True)
    artist = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    rank = models.BigIntegerField(default=0)
    track_id = models.CharField(max_length=200, default='none')

    def __str__(self):
        return self.title


class ChartStatUser(models.Model):
    artist = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    rank = models.BigIntegerField(default=0)
    track_id = models.CharField(max_length=200, default='none')

    def __str__(self):
        return self.title
