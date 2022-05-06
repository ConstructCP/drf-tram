from django.db import models
from django.utils.text import slugify


class Stop(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
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
        stops = Stop.objects.filter(route=self.pk).order_by('routestop__number_on_route')
        return f'{stops[0].name} - {stops[len(stops) - 1].name}'

    def __str__(self):
        return str(self.number)


class RouteStop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    number_on_route = models.IntegerField()

    def __str__(self):
        return f'Route {self.route} | stop {self.number_on_route} ({self.stop})'
