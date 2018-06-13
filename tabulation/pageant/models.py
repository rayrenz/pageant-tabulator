from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    roles = (
        ('j', 'judge'),
        ('t', 'tabulator')
    )
    role = models.TextField(max_length=10, choices=roles)


class Category(models.Model):
    title = models.TextField(max_length=20)
    name = models.SlugField(max_length=50)
    readonly = models.BooleanField(default=False)
    order = models.IntegerField()
    weight = models.FloatField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('order',)


class Candidate(models.Model):
    title = models.TextField(max_length=50)
    name = models.TextField(max_length=50)
    number = models.IntegerField(unique=True)
    id = models.TextField(unique=True, max_length=5, primary_key=True)
    finalist = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

class Score(models.Model):
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    judge = models.ForeignKey(to=User,on_delete=models.CASCADE, limit_choices_to={'role': 'j'})
    candidate = models.ForeignKey(to=Candidate, on_delete=models.CASCADE)
    points = models.FloatField()

    def __str__(self):
        return '#' + self.candidate.__str__() + ' ' + self.category.title + ' ' + self.judge.__str__() + ' (' + str(self.points) + ')'

    class Meta:
        unique_together = ('category', 'judge', 'candidate')


class Talent(models.Model):
    candidate = models.OneToOneField(to=Candidate, on_delete=models.CASCADE)
    points = models.FloatField()
    weight = models.FloatField(default=0.2)

class Final(models.Model):
    rank = models.FloatField()
    candidate = models.ForeignKey(to=Candidate, on_delete=models.CASCADE)
    judge = models.ForeignKey(to=User, limit_choices_to={'role': 'j'}, on_delete= models.CASCADE)

    class Meta:
        unique_together= (('candidate', 'judge'),('judge', 'rank'))
