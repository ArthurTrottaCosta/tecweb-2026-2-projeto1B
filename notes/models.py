from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True, related_name='notes')

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'{self.id}. {self.title}'
