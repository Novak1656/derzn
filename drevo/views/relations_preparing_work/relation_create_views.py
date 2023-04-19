from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from pip._vendor import requests

from drevo.forms import RelationStatusesForm, AdditionalKnowledgeForm
from drevo.models import Znanie, Author, Tr, Relation, RelationStatuses
from drevo.utils.preparing_relations import PreparingRelationsMixin


class PreparingRelationsCreateView(LoginRequiredMixin, TemplateView, PreparingRelationsMixin):
    """
        Страница подготовки связей.
        Этап - Создание связей (create)
    """
    template_name = 'drevo/relations_preparing_page/preparing_relations_page.html'
    login_url = reverse_lazy('login')
    extra_context = {'stage_name': 'Создание связей', 'related_widgets': 'create delete'}

    def get_context_data(self, **kwargs):
        context = super(PreparingRelationsCreateView, self).get_context_data(**kwargs)
        context['knowledge'] = self.get_queryset(user=self.request.user, stage='create')
        statuses = [(None, '------')]
        context['statuses_form'] = RelationStatusesForm(statuses=statuses)
        return context


class RelationCreatePageView(LoginRequiredMixin, TemplateView):
    """
        Страница создания связей
    """
    template_name = 'drevo/relations_preparing_page/relation_create_page.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super(RelationCreatePageView, self).get_context_data(**kwargs)
        bz_pk = self.request.GET.get('base_kn')
        base_knowledge = get_object_or_404(Znanie, pk=bz_pk)
        context['base_knowledge'] = base_knowledge

        url = self.request.build_absolute_uri(reverse('get_required_tr'))
        resp = requests.get(url=url, params={'bz_id': bz_pk})
        rt_data = resp.json().get('required_tr')
        context['rt_data'] = [(type_data.get('id'), type_data.get('name')) for type_data in rt_data] if rt_data else []
        context['create_form'] = AdditionalKnowledgeForm()

        required_statuses = {
            'user': [('WORK_PRE', 'ПредСвязь в работе'), ('PRE_FIN', 'Завершенная ПредСвязь')],
            'expert': [('WORK', 'Связь в работе'), ('FIN', 'Завершенная Связь')]
        }
        context['relation_statuses'] = (
            required_statuses.get('expert') if self.request.user.is_expert else required_statuses.get('user')
        )
        return context


@login_required
@require_http_methods(['POST'])
@transaction.atomic
def relation_create_view(request):
    """
        Создание связи
    """
    req_data = request.POST
    bz = get_object_or_404(Znanie, pk=req_data.get('base_kn'))
    tr = get_object_or_404(Tr, pk=req_data.get('relation_type'))
    rz = get_object_or_404(Znanie, pk=req_data.get('related_knowledge'))
    rel_status = req_data.get('relation_status')
    user = request.user
    authors = Author.objects.filter(user_author=user)
    if authors.exists():
        author = authors.first()
    else:
        author = Author.objects.create(name=user.get_full_name, user_author=user)
    relation = Relation.objects.create(bz=bz, tr=tr, rz=rz, author=author, user=user)
    RelationStatuses.objects.create(relation=relation, status=rel_status, user=user)
    return redirect('preparing_relations_create_page')
