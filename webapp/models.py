from django.db import models
from django.contrib.auth.models import User





class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    orgao = models.ForeignKey("webapp.Orgao", on_delete=models.SET_NULL, null=True, blank=True)
    departamento = models.ForeignKey("webapp.Departamento", on_delete=models.SET_NULL, null=True, blank=True)
    secretaria = models.ForeignKey("webapp.Secretaria", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.secretaria or self.departamento or self.orgao}"




class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    class Meta:
        ordering = ['nome']
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nome


class Orgao(models.Model):
    nome = models.CharField(max_length=100)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Departamento(models.Model):
    orgao = models.ForeignKey(Orgao, on_delete=models.CASCADE, related_name='departamentos')
    nome = models.CharField(max_length=100)

    class Meta:
        ordering = ['orgao__nome', 'nome']

    def __str__(self):
        return f"{self.nome} ({self.orgao.nome})"


class Secretaria(models.Model):
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='secretarias')
    nome = models.CharField(max_length=100)

    class Meta:
        ordering = ['departamento__orgao__nome', 'departamento__nome', 'nome']

    def __str__(self):
        return f"{self.nome} ({self.departamento.nome})"


from django.contrib.auth.models import User

class Documento(models.Model):
    titulo = models.CharField(max_length=200)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    orgao = models.ForeignKey(Orgao, on_delete=models.SET_NULL, null=True, blank=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True)
    secretaria = models.ForeignKey(Secretaria, on_delete=models.SET_NULL, null=True, blank=True)
    arquivo = models.FileField(upload_to='documentos/')
    data_envio = models.DateTimeField(auto_now_add=True)
    observacoes = models.TextField(blank=True)

    # ⚠️ Novo campo obrigatório
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-data_envio']

    def __str__(self):
        return self.titulo



class Favorito(models.Model):
    nome = models.CharField(max_length=255)
    url = models.URLField()
    criado_em = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # <-- CONFIRA!

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return self.nome


class DocumentoDigitalizado(models.Model):
    titulo = models.CharField(max_length=200)
    arquivo = models.FileField(upload_to='digitalizados/')
    observacoes = models.TextField(blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_criacao']

    def __str__(self):
        return self.titulo



# models.py

from django.db import models
from django.contrib.auth.models import User

class Tramitacao(models.Model):
    documento = models.ForeignKey('Documento', on_delete=models.CASCADE)
    documento_retorno = models.FileField(upload_to='documentos_retornados/', null=True, blank=True)
    remetente = models.ForeignKey(User, related_name='remetente_tramitacoes', on_delete=models.SET_NULL, null=True)
    destinatario = models.ForeignKey(User, related_name='destinatario_tramitacoes', on_delete=models.SET_NULL, null=True)
    mensagem = models.TextField(blank=True)
    data_envio = models.DateTimeField(auto_now_add=True)
    data_resposta = models.DateTimeField(null=True, blank=True)
    resposta = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('aberto', 'Aberto'),
        ('respondido', 'Respondido'),
        ('finalizado', 'Finalizado')
    ], default='aberto')

    def __str__(self):
        return f"{self.documento.titulo} → {self.destinatario}"
