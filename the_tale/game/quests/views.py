# coding: utf-8

from dext.views import handler

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.decorators import login_required
from the_tale.common.postponed_tasks.prototypes import PostponedTaskPrototype
from the_tale.common.utils import api

from the_tale.amqp_environment import environment

from the_tale.game.quests.postponed_tasks import MakeChoiceTask


class QuestsResource(Resource):

    @login_required
    def initialize(self, *argv, **kwargs):
        super(QuestsResource, self).initialize(*argv, **kwargs)

    @api.handler(versions=('1.0',))
    @handler('api', 'choose', name='api-choose', method='post')
    def api_choose(self, option_uid, api_version):
        u'''
Изменение пути выполнения задания героем

- **адрес:** /game/quests/api/choose/
- **http-метод:** POST
- **версии:** 1.0
- **параметры:**
    * GET: option_uid — уникальный идентификатор выбора в задании (получается с информацией о состоянии игры)
- **возможные ошибки**: нет

Метод является «неблокирующей операцией» (см. документацию), формат ответа соответствует ответу для всех «неблокирующих операций».
        '''
        choose_task = MakeChoiceTask(account_id=self.account.id, option_uid=option_uid)

        task = PostponedTaskPrototype.create(choose_task)

        environment.workers.supervisor.cmd_logic_task(self.account.id, task.id)

        return self.processing(status_url=task.status_url)
