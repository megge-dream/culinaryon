# -*- coding: utf-8 -*-

# User role
ADMIN = 0
STAFF = 1
USER = 2
USER_ROLE = {
    ADMIN: 'admin',
    STAFF: 'staff',
    USER: 'user',
}
USER_ROLE_SELECT = [
    (ADMIN, 'admin'),
    (STAFF, 'staff'),
    (USER, 'user')
]
# User status
INACTIVE = 0
NEW = 1
ACTIVE = 2
USER_STATUS = {
    INACTIVE: 'inactive',
    NEW: 'new',
    ACTIVE: 'active',
}
USER_STATUS_SELECT = {
    (INACTIVE, 'inactive'),
    (NEW, 'new'),
    (ACTIVE, 'active')
}
# Providers' list
NO_PROVIDER = 0
VK = 1
FB = 2
TW = 3
PROVIDER_LIST = {
    NO_PROVIDER: 'no_provider',
    VK: 'vkontakte',
    FB: 'facebook',
    TW: 'twitter'
}
PROVIDER_LIST_SELECT = {
    (NO_PROVIDER, 'no_provider'),
    (VK, 'vkontakte'),
    (FB, 'facebook'),
    (TW, 'twitter')

}
# Other
APP_MAIL = "app@culinaryon.com"
# Open sets length
MONTH = 0
FOREVER = 1
OPEN_LENGTH = {
    MONTH: 'month',
    FOREVER: 'forever',
}
OPEN_LENGTH_SELECT = [
    (MONTH, 'month'),
    (FOREVER, 'forever'),
]
# Recipes type
PUBLISHED = 0
PREVIEW = 1
DRAFT = 2
RECIPE_TYPE = {
    PUBLISHED: 'publish',
    PREVIEW: 'preview',
    DRAFT: 'draft',
}
RECIPE_TYPE_SELECT = [
    (PUBLISHED, 'publish'),
    (PREVIEW, 'preview'),
    (DRAFT, 'draft'),
]
# Langs
NOT_COPY = '--'
RU = ''
EN = '_lang_en'
LANG = {
    RU: 'ru',
    EN: 'en',
}
LANG_SELECT = [
    (NOT_COPY, "--don't copy--"),
    (RU, 'ru'),
    (EN, 'en'),
]