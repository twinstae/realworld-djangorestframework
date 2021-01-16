from rest_framework import serializers

from realworld.apps.articles.models import Tag


class TagRelatedField(serializers.ReatedField):
    def get_queryset(self):
        return Tag.objects.all()

    def to_internal_value(self, data):
        tag, created = Tag.objects.get_or_create(tag=data, slug=data.lower())
        return tag

    def to_representation(self, value):
        return value.tag
