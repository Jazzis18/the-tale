# coding: utf-8

from dext.common.utils.app_settings import app_settings

settings = app_settings('BLOGS',
                        FORUM_CATEGORY_UID='folclor',
                        MIN_TEXT_LENGTH=1000,
                        POSTS_ON_PAGE=15,
                        FORUM_TAGS_THREAD=4437,
                        DEFAULT_TAGS=[1],
                        IS_ABOUT_MAXIMUM=100)
