import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.fields import AutoCreatedField, AutoLastModifiedField


class TimeStampedModel(models.Model):
    created_at = AutoCreatedField()
    updated_at = AutoLastModifiedField()

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedModel):
    name = models.CharField(_('название'), max_length=255)
    description = models.TextField(_('описание'), blank=True, null=True)

    class Meta:
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedModel):
    full_name = models.CharField(max_length=100, default=None)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = _('Персона')
        verbose_name_plural = _('Персоны')


class PersonFilmWork(UUIDMixin, models.Model):

    class Role(models.TextChoices):
        ACTOR = 'actor'
        DIRECTOR = 'director'
        WRITER = 'writer'
    filmwork = models.ForeignKey('FilmWork', related_name='person_work', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE, verbose_name=_('Полное имя'))
    role = models.CharField(max_length=50, choices=Role.choices, verbose_name=_('Вид участия'))
    created_at = AutoCreatedField()

    class Meta:
        unique_together = ('filmwork', 'person', 'role')
        verbose_name = _('Персона')
        verbose_name_plural = _('Персоны')
        db_table = 'movies_filmwork_persons'

    def __str__(self):
        return self.role


class FilmWork(UUIDMixin, TimeStampedModel):

    class Type(models.TextChoices):
        SERIES = 'series'
        MOVIE = 'movie'

    type = models.CharField(_('тип'), max_length=50, choices=Type.choices)
    title = models.CharField(_('название'), max_length=255, default=None)
    description = models.TextField(_('описание'), blank=True, default=None, null=True)
    creation_date = models.DateField(_('создан'), blank=True, default=None, null=True)
    rating = models.FloatField(_('рейтинг'), validators=[MinValueValidator(0), MaxValueValidator(10)], blank=True,
                               default=None, null=True)
    person = models.ManyToManyField(Person, through=PersonFilmWork, verbose_name=_('Вид участия'), blank=True)
    genres = models.ManyToManyField(Genre)
    file_path = models.FileField(_('файл'), upload_to='film_works/', blank=True, default=None, null=True)

    class Meta:
        verbose_name = _('Фильм')
        verbose_name_plural = _('Фильмы')

    def __str__(self):
        return self.title
