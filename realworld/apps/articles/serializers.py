from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta

from realworld.apps.articles.models import Article, Comment, Tag
from realworld.apps.articles.relations import TagRelatedField
from realworld.apps.profiles.serializers import ProfileSerializer


class ArticleSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)
    description = serializers.CharField(required=False)
    slug = serializers.SlugField(required=False)
    createdAt = serializers.SerializerMethodField(method_name='get_created_at')
    updatedAt = serializers.SerializerMethodField(method_name='get_updated_at')

    tagList = TagRelatedField(many=True, required=False, source='tags')

    favorited = serializers.SerializerMethodField()
    favoritesCount = serializers.SerializerMethodField(
        method_name='get_favorites_count'
    )

    class Meta:
        model = Article
        fields = (
            'author',
            'slug',
            'title',
            'body',
            'description',
            'tagList',
            'favorited',
            'favoritesCount',
            'createdAt',
            'updatedAt',
        )

    def create(self, validated_data):
        author = self.context.get('author', None)
        tags = validated_data.pop('tags', [])
        article = Article.objects.create(author=author, **validated_data)
        for tag in tags:
            article.tags.add(tag)
        return article

    def get_created_at(self, instance):
        return instance.created_at.isoformat()

    def get_updated_at(self, instance):
        return instance.updated_at.isoformat()

    def get_favorited(self, instance) -> bool:
        """
        사용자가 좋아요를 누른 게시글인지? 여부를 반환
        """
        request = self.context.get('request', None)
        if request is None:
            return False

        if not request.user.is_authenticated:
            return False

        return request.user.profile.has_favorited(instance)

    def get_favorites_count(self, instance) -> int:
        return instance.favorited_by.count()


class CommentSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(required=False)
    createdAt = serializers.SerializerMethodField(method_name='get_created_at')
    updatedAt = serializers.SerializerMethodField(method_name='get_updated_at')

    class Meta:
        model = Comment
        fields = (
            'id',
            'author',
            'body',
            'createdAt',
            'updatedAt',
        )

    def create(self, validated_data):
        article = self.context['article']
        author = self.context['author']

        return Comment.objects.create(
            author=author,
            article=article,
            **validated_data
        )

    def get_created_at(self, instance):
        return instance.created_at.isoformat()

    def get_updated_at(self, instance):
        return instance.updated_at.isoformat()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('tag',)

    def to_representation(self, obj):
        return obj.tag
