from django import forms
from .models import Documento

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['titulo', 'categoria', 'arquivo', 'observacoes']


from django import forms
from django.contrib.auth.models import User
from .models import PerfilUsuario, Orgao, Departamento, Secretaria

class CadastroUsuarioForm(forms.ModelForm):
    orgao = forms.ModelChoiceField(queryset=Orgao.objects.all(), required=False, label='Órgão')
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all(), required=False, label='Departamento')
    secretaria = forms.ModelChoiceField(queryset=Secretaria.objects.all(), required=False, label='Secretaria')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        user = super().save(commit=commit)

        # Garante que perfil seja criado ou atualizado corretamente
        perfil, created = PerfilUsuario.objects.get_or_create(user=user)
        perfil.orgao = self.cleaned_data.get('orgao')
        perfil.departamento = self.cleaned_data.get('departamento')
        perfil.secretaria = self.cleaned_data.get('secretaria')

        if commit:
            perfil.save()

        return user
