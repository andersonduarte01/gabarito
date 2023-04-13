from django import forms
from django.forms import TextInput
from django.forms.widgets import CheckboxSelectMultiple
from .models import Avaliacao
from ..avaliacao.models import Resposta, Questao
from ..escola.models import UnidadeEscolar

class RespostaForm(forms.ModelForm):
    class Meta:
        model = Resposta
        fields = ('resposta',)

        widgets = {
            'resposta': TextInput(
                attrs={
                    'size': '4px',
                    'style': 'margin-right: 6px; border: 1px solid #ccc; border-radius: 5px; padding: 4px 15px; margin: 4px; text-align: center;'
                }),
        }


class AvaliacaoQuestaoForm(forms.ModelForm):

    class Meta:
        model = Questao
        fields = ('texto', 'questao', 'opcao_um', 'opcao_dois', 'opcao_tres', 'opcao_quatro')


class AvaliacaoForm(forms.ModelForm):
    escolas = UnidadeEscolar.objects.all()
    escola = forms.ModelMultipleChoiceField(
        queryset=escolas,
        widget=CheckboxSelectMultiple(),
        required=False,
    )

    class Meta:
        model = Avaliacao
        fields = ['descricao', 'ano', 'escola']


class AvaliacaoUpdateForm(forms.ModelForm):
    escola = forms.ModelMultipleChoiceField(
        queryset=UnidadeEscolar.objects.all(),
        widget=CheckboxSelectMultiple(),
        required=False,
    )

    class Meta:
        model = Avaliacao
        fields = ['descricao', 'ano', 'escola']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['escola'].initial = self.instance.escola.all()

    def save(self, commit=True):
        avaliacao = super().save(commit=False)
        if commit:
            avaliacao.save()
        if self.cleaned_data.get('escola'):
            avaliacao.escola.set(self.cleaned_data['escola'])
        else:
            avaliacao.escola.clear()
        return avaliacao
