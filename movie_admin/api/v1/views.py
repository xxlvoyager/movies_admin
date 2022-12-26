import logging
import validators
from django.http import Http404
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.db.models.query import QuerySet
from movies.models import FilmWork
from movies.models import PersonFilmWork
from movies.models import Person
from django.shortcuts import get_object_or_404
from django.db import connection
from django.core.paginator import Paginator
from django.forms.models import model_to_dict


logger = logging.getLogger(__name__)

PER_PAGE = 50


def convert_respond(query_set: QuerySet) -> list:
    list_films = list(query_set)
    # Запрашиваем все фильмы из Filmwork в виде словарей
    list_films_uuid = [x.id for x in list_films]
    # Запрашиваем все данные о ролях
    roles = PersonFilmWork.objects.filter(
        filmwork__in=list_films_uuid).order_by('filmwork').values('id', 'filmwork', 'role', 'person')
    list_roles = list(roles)

    used = set()
    # Изменено по рекомндации, время исполнения незначительно увеличилось
    # list_person_uuid = [x['person'] for x in list_roles if
    #                    x['person'] not in used and (used.add(x['person']) or True)]
    list_person_uuid = []
    for x in list_roles:
        if x['person'] not in used:
            list_person_uuid.append(x['person'])
            used.add(x['person'])

    # Запрашивем имена персон и формируем словарь персон
    list_persons = list(Person.objects.filter(id__in=list_person_uuid).values('id', 'full_name'))
    person_dict = {}
    for one_person in list_persons:
        person_dict[str(one_person['id'])] = one_person['full_name']
    # Заполняем недостающие поля во всех фильмах
    respond = []
    for _film in list_films:
        one_film = model_to_dict(_film)
        one_film['id'] = _film.id
        # Получаем списки жанров к конкретному фильму
        list_genres = list(FilmWork.objects.filter(id=one_film['id']).prefetch_related('genres').values('genres__name'))
        # Распределяем роли персон
        one_film_roles = [x for x in list_roles if x['filmwork'] == one_film['id']]
        list_actors_uuid = [str(x['person']) for x in one_film_roles if x['role'] == 'actor']
        list_writers_uuid = [str(x['person']) for x in one_film_roles if x['role'] == 'writer']
        list_directors_uuid = [str(x['person']) for x in one_film_roles if x['role'] == 'director']
        list_actors = [person_dict[x] for x in list_actors_uuid]
        list_directors = [person_dict[x] for x in list_directors_uuid]
        list_writers = [person_dict[x] for x in list_writers_uuid]
        one_film['actors'] = list_actors
        one_film['directors'] = list_directors
        one_film['writers'] = list_writers
        one_film['genres'] = [x['genres__name'] for x in list_genres]
        del one_film['person']
        del one_film['file_path']
        respond.append(one_film)
    return respond


class Movies(BaseListView):
    model = FilmWork
    http_method_names = ['get']

    def get_queryset(self):
        movies_list = FilmWork.objects.all().order_by('id')
        paginator = Paginator(movies_list, PER_PAGE)
        return paginator

    def get_context_data(self, *, object_list=None, **kwargs):
        logger.debug(len(connection.queries))
        paginator = self.get_queryset()
        if 'page' in self.request.GET:
            page_number = self.request.GET.get('page')
            if page_number == 'last':
                page_number = paginator.count
        else:
            page_number = 1

        page_obj = paginator.get_page(page_number)
        if page_obj.has_previous():
            prev_page = page_obj.previous_page_number()
        else:
            prev_page = None
        if page_obj.has_next():
            next_page = page_obj.next_page_number()
        else:
            next_page = None

        respond = {'count': paginator.count,
                   'total_pages': paginator.num_pages,
                   'prev': prev_page,
                   'next': next_page,
                   'page': int(page_number),
                   "results": convert_respond(page_obj)}

        logger.debug(len(connection.queries))

        return respond

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, safe=False)


class MovieDetail(BaseListView):
    model = FilmWork

    def get_queryset(self):
        if not validators.uuid(self.kwargs['uuid']):
            raise Http404("Wrong UUID.")
        respond = FilmWork.objects.filter(id=self.kwargs['uuid']).values(
            'id', 'title', 'description', 'rating', 'creation_date', 'type')
        return respond

    def get_context_data(self, *, object_list=None, **kwargs):
        film = get_object_or_404(self.get_queryset())
        list_genres = list(FilmWork.objects.filter(id=film['id']).prefetch_related('genres').values('genres__name'))
        film['genres'] = [x['genres__name'] for x in list_genres]
        list_actors = list(FilmWork.objects.filter(id=film['id']).filter(person_work__role='actor')
                           .prefetch_related('person').values('person__full_name'))
        film['actors'] = [x['person__full_name'] for x in list_actors]
        list_writers = list(FilmWork.objects.filter(id=film['id']).filter(person_work__role='writer')
                            .prefetch_related('person').values('person__full_name'))
        film['writers'] = [x['person__full_name'] for x in list_writers]
        list_directors = list(FilmWork.objects.filter(id=film['id']).filter(person_work__role='director')
                              .prefetch_related('person').values('person__full_name'))
        film['directors'] = [x['person__full_name'] for x in list_directors]
        return film

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)
