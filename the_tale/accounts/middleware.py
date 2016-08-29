# coding: utf-8

from rels.django import DjangoEnum

from the_tale.common.postponed_tasks.prototypes import PostponedTaskPrototype

from the_tale.accounts.conf import accounts_settings
from the_tale.accounts.logic import login_user


class HANDLE_REGISTRATION_RESULT(DjangoEnum):
    records = ( ('NOT_ANONYMOUS', 0, u'пользователь уже зарегистрирован'),
                 ('NO_TASK_ID', 1, u'нет идентификатора задач'),
                 ('TASK_NOT_FOUND', 2, u'задача не найдена'),
                 ('TASK_NOT_PROCESSED', 4, u'задача не обработана'),
                 ('USER_LOGINED', 5, u'пользователь залогинен'))


class HANDLE_REFERER_RESULT(DjangoEnum):
    records = ( ('NOT_ANONYMOUS', 0, u'пользователь уже зарегистрирован'),
                 ('SAVED', 1, u'реферер сохранён'),
                 ('ALREADY_SAVED', 2, u'реферер уже сохранён'),
                 ('NO_REFERER', 4, u'нет реферера'))


class HANDLE_REFERRAL_RESULT(DjangoEnum):
    records = ( ('NOT_ANONYMOUS', 0, u'пользователь уже зарегистрирован'),
                 ('NO_REFERRAL', 1, u'владелец реферала не указан'),
                 ('ALREADY_SAVED', 2, u'владелец реферала уже сохранён'),
                 ('SAVED', 4, u'владелец реферала сохранён'))


class HANDLE_ACTION_RESULT(DjangoEnum):
    records = ( ('NOT_ANONYMOUS', 0, u'пользователь уже зарегистрирован'),
                ('NO_ACTION', 1, u'акция не указана'),
                ('ALREADY_SAVED', 2, u'акция уже сохранёна'),
                ('SAVED', 4, u'акция сохранена'))


class RegistrationMiddleware(object):

    def handle_registration(self, request):

        if not request.user.is_anonymous():
            return HANDLE_REGISTRATION_RESULT.NOT_ANONYMOUS

        if accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY not in request.session:
            return HANDLE_REGISTRATION_RESULT.NO_TASK_ID

        task_id = request.session[accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY]
        task = PostponedTaskPrototype.get_by_id(task_id)

        if task is None:
            return HANDLE_REGISTRATION_RESULT.TASK_NOT_FOUND

        if not task.state.is_processed:
            return HANDLE_REGISTRATION_RESULT.TASK_NOT_PROCESSED

        login_user(request, nick=task.internal_logic.account.nick, password=accounts_settings.FAST_REGISTRATION_USER_PASSWORD)
        return HANDLE_REGISTRATION_RESULT.USER_LOGINED

    def handle_referer(self, request):
        if not request.user.is_anonymous():
            return HANDLE_REFERER_RESULT.NOT_ANONYMOUS

        referer = request.META.get('HTTP_REFERER')

        if referer is None:
            return HANDLE_REFERER_RESULT.NO_REFERER

        if accounts_settings.SESSION_REGISTRATION_REFERER_KEY in request.session:
            return HANDLE_REFERER_RESULT.ALREADY_SAVED

        request.session[accounts_settings.SESSION_REGISTRATION_REFERER_KEY] = referer
        return HANDLE_REFERER_RESULT.SAVED

    def handle_referral(self, request):

        if not request.user.is_anonymous():
            return HANDLE_REFERRAL_RESULT.NOT_ANONYMOUS

        if accounts_settings.REFERRAL_URL_ARGUMENT not in request.GET:
            return HANDLE_REFERRAL_RESULT.NO_REFERRAL

        referral_id = request.GET[accounts_settings.REFERRAL_URL_ARGUMENT]

        if accounts_settings.SESSION_REGISTRATION_REFERRAL_KEY in request.session:
            return HANDLE_REFERRAL_RESULT.ALREADY_SAVED

        request.session[accounts_settings.SESSION_REGISTRATION_REFERRAL_KEY] = referral_id
        return HANDLE_REFERRAL_RESULT.SAVED


    def handle_action(self, request):

        if not request.user.is_anonymous():
            return HANDLE_ACTION_RESULT.NOT_ANONYMOUS

        if accounts_settings.ACTION_URL_ARGUMENT not in request.GET:
            return HANDLE_ACTION_RESULT.NO_ACTION

        action_id = request.GET[accounts_settings.ACTION_URL_ARGUMENT]

        if accounts_settings.SESSION_REGISTRATION_ACTION_KEY in request.session:
            return HANDLE_ACTION_RESULT.ALREADY_SAVED

        request.session[accounts_settings.SESSION_REGISTRATION_ACTION_KEY] = action_id
        return HANDLE_ACTION_RESULT.SAVED


    def process_request(self, request):
        self.handle_registration(request)
        self.handle_referer(request)
        self.handle_referral(request)
        self.handle_action(request)



class FirstTimeVisitMiddleware(object):

    def process_request(self, request):
        if not request.session.get(accounts_settings.SESSION_FIRST_TIME_VISIT_VISITED_KEY):
            request.session[accounts_settings.SESSION_FIRST_TIME_VISIT_KEY] = True
            request.session[accounts_settings.SESSION_FIRST_TIME_VISIT_VISITED_KEY] = True
        else:
            if request.session.get(accounts_settings.SESSION_FIRST_TIME_VISIT_KEY):
                request.session[accounts_settings.SESSION_FIRST_TIME_VISIT_KEY] = False
