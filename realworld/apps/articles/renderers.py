from realworld.apps.core.renderers import RealworldJSONRenderer


class ArticleJSONRenderer(RealworldJSONRenderer):
    object_label = 'article'
    pagination_object_label = 'articles'
    pagination_count_label = 'articlesCount'
