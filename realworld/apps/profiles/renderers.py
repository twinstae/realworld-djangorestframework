from realworld.apps.core.renderers import RealworldJSONRenderer


class ProfileJSONRenderer(RealworldJSONRenderer):
    charset = 'utf-8'
    object_label = 'proflie'
    pagination_object_label = 'profiles'
    pagination_count_label = 'profilesCount'