from django import forms
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView, RedirectView, UpdateView

from drevo import models as orm
from drevo.views.expert_work.data_loaders import load_interview


class QuestionExpertWorkPage(TemplateView):
    """
    Работа эксперта по конкретному вопросу интервью.
    Формируем страницу с:
    - базовой информацией по интервью и вопросу
    - со всеми опубликованными ответами на этот вопрос
    - со всеми вариантами предложений текущего (request.user.expert) эксперта для каждого варианта ответа
    - со всеми новыми ответами, которые создал эксперт
    """

    template_name = "drevo/expert_work_page/expert_work_page.html"

    def get_context_data(self, interview_pk: int, question_pk, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Экспертиза"
        if context.get("new_answer_form") is None:
            context["new_answer_form"] = NewAnswerFromExpertForm()
        context["interview"] = load_interview(interview_pk)

        max_agreed = (
            orm.Relation.objects.filter(
                bz_id=question_pk,
                tr_id=orm.Tr.objects.get(name="Число ответов").id,
                #user_id=self.request.user.id
            )
            .order_by()
            .last()
        )
        max_agreed = get_object_or_404(orm.Znanie, id=max_agreed.rz_id).name
        context["max_agreed"] = int(max_agreed)

        # забираем все ответы по вопросу
        question_raw = get_object_or_404(orm.Znanie, pk=question_pk)
        answers_links = question_raw.base.filter(
            tr_id=orm.Tr.objects.get(name="Ответ [ы]").id
        ).select_related("rz").prefetch_related('rz__answ_sub_answers')

        answers = {}
        for answer_link in answers_links:
            answer = answer_link.rz
            answers[answer.pk] = dict(
                id=answer.pk,
                text=answer.name,
                sub_answers=answer.answ_sub_answers.all().values_list('sub_answer', flat=True)
            )

        # собираем предложения
        proposals = orm.InterviewAnswerExpertProposal.objects.filter(
            interview_id=interview_pk,
            question_id=question_pk,
            expert_id=self.request.user.pk,
        ).order_by("id")

        # разделяем предложения на две группы,
        # те которе уже прошли проверку администратором 'reviewed' и которые в ожидании 'pending'
        expert_proposals = {'reviewed': list(), 'pending': list()}
        for prop in proposals:
            # предложение к существующему вопросу
            if prop.status:
                expert_proposals['reviewed'].append(prop)
            else:
                expert_proposals['pending'].append(prop)
        context['backup_url'] = reverse('interview', kwargs={'pk': interview_pk})
        context["answers"] = answers.values()
        context["expert_proposals"] = expert_proposals
        context["question"] = dict(id=question_pk, title=question_raw.name)
        return context


class NewAnswerFromExpertForm(forms.Form):
    text = forms.CharField()
    is_agreed = forms.BooleanField(required=False)
    is_incorrect_answer = forms.BooleanField(required=False)
    comment = forms.JSONField(required=False)


@require_http_methods(["POST"])
def propose_answer(req: HttpRequest, interview_pk: int, question_pk: int, **kwargs):
    """
    Эксперт предлагает новый ответ в качестве предложения
    """
    form = NewAnswerFromExpertForm(req.POST)
    context = dict(interview=dict(id=interview_pk), question=dict(id=question_pk))

    if form.is_valid():
        status = 201
        prop = orm.InterviewAnswerExpertProposal()
        prop.expert_user = req.user
        prop.interview_id = interview_pk
        prop.question_id = question_pk
        can_agreed = orm.InterviewAnswerExpertProposal.check_max_agreed(prop)
        if not can_agreed:
            form.cleaned_data["is_agreed"] = False

        context["proposal"] = orm.InterviewAnswerExpertProposal.create_new_proposal(
            expert_user=req.user,
            interview_id=interview_pk,
            question_id=question_pk,
            **form.cleaned_data,
        )
    else:
        status = 400

    context["form"] = form
    return TemplateResponse(
        req, "drevo/expert_work_page/proposed_answer_block.html", context, status=status
    )


class AnswerProposalForm(forms.Form):
    is_agreed = forms.BooleanField(required=False)
    is_incorrect_answer = forms.BooleanField(required=False)
    answer_pk = forms.IntegerField(required=False)
    proposal_pk = forms.IntegerField(required=False)


@require_http_methods(["POST"])
def update_answer_proposal(
    req: HttpRequest, interview_pk: int, question_pk: int, answer_pk: int
):
    """
    Добавление/обновление мнения к определенному ответу.
    """

    form = AnswerProposalForm(req.POST)
    if form.is_valid():
        proposal_pk = form.cleaned_data.get("proposal_pk")
        if proposal_pk:
            prop = orm.InterviewAnswerExpertProposal.objects.get(id=proposal_pk)

            form.cleaned_data["id"] = form.cleaned_data.pop("proposal_pk")
        else:
            prop, _ = orm.InterviewAnswerExpertProposal.objects.get_or_create(
                expert=req.user,
                interview_id=interview_pk,
                answer_id=answer_pk,
                question_id=question_pk,
            )
            form.cleaned_data.pop("proposal_pk")
            form.cleaned_data["id"] = prop.pk
        can_agreed = orm.InterviewAnswerExpertProposal.check_max_agreed(prop)
        if can_agreed:
            prop.is_agreed = form.cleaned_data.get("is_agreed", False)
        else:
            if not form.cleaned_data.get("is_agreed"):
                prop.is_agreed = False

        prop.is_incorrect_answer = form.cleaned_data.get("is_incorrect_answer", False)
        prop.save()

    proposal_data = form.cleaned_data
    answer_pk = proposal_data.pop("answer_pk", None)
    context = dict(
        answer=dict(id=answer_pk),
        interview=dict(id=interview_pk),
        question=dict(id=question_pk),
        proposal=proposal_data,
        form=form,
    )

    return TemplateResponse(
        req, "drevo/expert_work_page/proposal_form_body.html", context=context
    )


@require_http_methods(["POST"])
def update_proposed_answer(req: HttpRequest, proposal_pk: int):
    """
    Метод обновления предложенного ответа
    """
    form = AnswerProposalForm(req.POST)
    prop = orm.InterviewAnswerExpertProposal.objects.get(id=proposal_pk)
    context = dict(
        answer=prop.answer,
        interview=dict(id=prop.interview.pk),
        question=dict(id=prop.question.pk),
        form=form,
        proposal=prop,
    )
    if form.is_valid():
        form_data = form.cleaned_data
        can_agreed = orm.InterviewAnswerExpertProposal.check_max_agreed(prop)

        if can_agreed:
            prop.is_agreed = form.cleaned_data.get("is_agreed", False)
        else:
            if not form.cleaned_data.get("is_agreed"):
                prop.is_agreed = False

        prop.is_incorrect_answer = form_data.get("is_incorrect_answer", False)
        prop.save()

        form_data["id"] = form_data.pop("proposal_pk", None)

    return TemplateResponse(
        req, "drevo/expert_work_page/proposed_answer_block.html", context=context
    )


@require_http_methods(['POST'])
def sub_answer_create_view(request: HttpRequest, quest_pk: int, answer_pk: int):
    """
        Добавление подответа к ответу на вопрос интервью
    """
    sub_answer = request.POST.get('subanswer')
    question = orm.Znanie.objects.get(pk=quest_pk)
    answer = orm.Znanie.objects.get(pk=answer_pk)
    orm.SubAnswers.objects.create(expert=request.user, question=question, answer=answer, sub_answer=sub_answer)
    return redirect(request.META.get('HTTP_REFERER'))


class ExpertProposalDeleteView(RedirectView):
    """
        Удаление предложения эксперта по вопросу интервью
    """
    def get_redirect_url(self, *args, **kwargs):
        return self.request.META.get('HTTP_REFERER')

    def get(self, request, *args, **kwargs):
        proposal_pk = request.GET.get('proposal_pk')
        queryset = orm.InterviewAnswerExpertProposal.objects.filter(pk=proposal_pk, expert=request.user)
        if queryset.exists():
            queryset.first().delete()
        return super(ExpertProposalDeleteView, self).get(request, *args, **kwargs)
