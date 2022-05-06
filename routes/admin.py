from django.contrib import admin

from .models import Route, RouteStop, Stop, StopConnection


class StopAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Route)
admin.site.register(RouteStop)
admin.site.register(Stop, StopAdmin)
admin.site.register(StopConnection)
