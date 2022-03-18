from django.contrib import admin
from .models import UserStat, Profile

# Register your models here.
class UserStatAdmin(admin.ModelAdmin):
    fields = ["username",
            "last_name",
            "first_name"]

class ProfileAdmin(admin.ModelAdmin):
    fields = ["spotify_username"]

admin.site.register(Profile, ProfileAdmin)    


admin.site.register(UserStat, UserStatAdmin)
