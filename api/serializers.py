from rest_framework import serializers

from movies.models import FilmWork, PersonFilmWork


class PersonRolesSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField(source='person.full_name')

    class Meta:
        model = PersonFilmWork
        fields = ('full_name', 'role')


def rebuild_dict(type_role: str, roles: dict, names: dict) -> list:
    type_role_list = []
    for one_person in filter(lambda person: person['role'] == type_role, roles):
        type_role_list.append(names[str(one_person['person_id'])])
    return type_role_list


class FilmSerializer(serializers.ModelSerializer):

    genres = serializers.ListSerializer(child=serializers.CharField())
    person = PersonRolesSerializer(source='person_work', many=True)

    def to_representation(self, data):
        persons_full_name = {str(one_person['id']): one_person['full_name'] for one_person in data.person.values()}
        roles = data.person_work.values()
        actors = rebuild_dict('actor', roles, persons_full_name)
        directors = rebuild_dict('director', roles, persons_full_name)
        writers = rebuild_dict('writer', roles, persons_full_name)

        return {'id': data.id,
                'type': data.type,
                'title': data.title,
                'description': data.description,
                'creation_date': data.creation_date,
                'rating': data.rating,
                'actors': actors,
                'directors': directors,
                'writers': writers}

    class Meta:
        model = FilmWork
        fields = ['genres', 'person']
