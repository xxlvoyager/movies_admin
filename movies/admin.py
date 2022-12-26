from django.contrib import admin
from django.contrib.auth.models import Group

from .models import FilmWork, Genre, Person, PersonFilmWork


admin.site.unregister(Group)
admin.site.site_header = 'MOVIES Admin'
admin.site.site_title = 'Movies Admin Portal'
admin.site.index_title = 'Welcome to Movies Portal'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ('name', 'description')


class FilmInline(admin.TabularInline):
    autocomplete_fields = ('filmwork',)
    model = PersonFilmWork
    extra = 0


@admin.register(Person)
class PersAdm(admin.ModelAdmin):
    search_fields = ('full_name',)
    inlines = (FilmInline,)


class PersonInline(admin.TabularInline):
    autocomplete_fields = ('person',)
    model = PersonFilmWork
    extra = 0


@admin.register(FilmWork)
class MovieAdmin(admin.ModelAdmin):
    autocomplete_fields = ('genres', 'person',)
    list_display = ('title', 'creation_date', 'rating')
    list_filter = ('type',)
    search_fields = ('title', 'description')
    inlines = (PersonInline, )  # Model  FlimWorkGenres  django генерирует автоматически
