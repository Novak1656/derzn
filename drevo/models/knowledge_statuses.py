from django.db import models

from drevo.models import Znanie


class KnowledgeStatuses(models.Model):
    """
    Класс для описания сущности "Статус знания"
    """
    class Status(models.TextChoices):
        PUB_PRE = 'PUB_PRE', 'Опубликованное ПредЗнание'
        PUB = 'PUB', 'Опубликованное Знание'
        WORK_PRE = 'WORK_PRE', 'ПредЗнание в работе'
        RET_PRE_TO_EDIT = 'RET_PRE_EDIT', 'Возврат ПредЗнания на доработку'
        PRE_FINISH = 'PRE_FIN', 'Готовое ПредЗнание'
        PRE_EXPERTISE = 'PRE_EXP', 'Экспертиза ПредЗнания'
        PRE_REJECT = 'PRE_REJ', 'Отклоненное ПредЗнание'
        PRE_REFUND_EXPERTISE = 'PRE_REF_EXP', 'Возврат ПредЗнания на экспертизу'
        PRE_FINISH_EXPERTISE = 'PRE_FIN_EXP', 'Завершенное ПредЗнание'
        WORK = 'WORK', 'Знание в работе'
        RET_TO_EDIT = 'RET_TO_EDIT', 'Возврат Знания на доработку'
        FINISH = 'FIN', 'Завершенное Знание'
        PRE_REDACT = 'PRE_REDACT', 'ПредЗнание на редактировании'
        PRE_REFUND_REDACT = 'PRE_REF_RED', 'Возврат ПредЗнания редактору'
        PRE_FINISH_REDACT = 'PRE_FIN_RED', 'ПредЗнание к публикации'
        REDACT = 'REDACT', 'Знание на редактировании'
        REFUND_REDACT = 'REF_RED', 'Возврат Знания редактору'
        FINISH_REDACT = 'FIN_RED', 'Знание к публикации'
        PRE_KLZ = 'PRE_KLZ', 'ПредЗнание в КЛЗ'
        PRE_EXPERTISE_2 = 'PRE_EXP_2', 'Экспертиза-2 ПредЗнания'
        KLZ = 'KLZ', 'Знание в КЛЗ'
        EXPERTISE_2 = 'EXP_2', 'Экспертиза-2 Знания'

    knowledge = models.ForeignKey(Znanie, on_delete=models.CASCADE,
                                  related_name='knowledge_status', verbose_name='Знание')
    status = models.CharField(max_length=12, choices=Status.choices, default=None, verbose_name='Статус')


