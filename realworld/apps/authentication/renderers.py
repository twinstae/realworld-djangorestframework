from realworld.apps.core.renderers import RealworldJSONRenderer


class JwtUserJSONRenderer(RealworldJSONRenderer):
    charset = 'utf-8'
    object_label = 'user'
    pagination_object_label = 'users'
    pagination_count_label = 'usersCount'
