from django.db import models
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError


class Stop(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    prepopulated_fields = {"slug": ("title",)}

    def save(self, *args, **kwargs):
        slugified_name = slugify(self.name)
        try:
            colliding_stop = Stop.objects.get(slug=slugified_name)
            raise ValidationError(f'Stop slug name collides with another stop slug name (Stop "{colliding_stop.name}")')
        except Stop.DoesNotExist:
            self.slug = slugified_name
            super(Stop, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class StopConnection(models.Model):
    stop1 = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='+')
    stop2 = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='+')
    time = models.IntegerField(default=2, help_text='Travel time in minutes')

    def __str__(self):
        return f'{self.stop1} - {self.stop2}'


class Route(models.Model):
    number = models.IntegerField(unique=True)
    stops = models.ManyToManyField(Stop, through='RouteStop')

    @property
    def name(self):
        stops_on_route = self.routestop_set.all().order_by('number_on_route')
        if len(stops_on_route) > 1:
            return f'{stops_on_route[0].stop.name} - {stops_on_route[len(stops_on_route) - 1].stop.name}'
        return self.number

    def __str__(self):
        return str(self.number)


class RouteStop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    number_on_route = models.IntegerField()

    def __str__(self):
        return f'Route {self.route} | stop {self.number_on_route} ({self.stop})'
