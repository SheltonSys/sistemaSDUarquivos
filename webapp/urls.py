from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.pagina_inicial, name='pagina_inicial'),  # Página inicial pública
    path('base/', views.BASE, name='base'),                  # Template base (opcional)

    # === Painel principal (index com cards) ===
    path('arquivos/', views.index, name='arquivos_index'),

    # === Dashboard geral (caso use outro painel) ===
    path('dashboard/', views.dashboard, name='dashboard'),

    # === Documentos ===
    path('documentos/listar/', views.listar_arquivos, name='listar_arquivos'),
    path('documentos/', views.listar_documentos, name='listar_documentos'),  # <- cuidado com duplicidade
    path('novo/', views.cadastrar_arquivo, name='cadastrar_arquivo'),

    # === Login/Logout ===
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    # === Categorias ===
    path('categorias/', views.listar_categorias, name='listar_categorias'),
    path('categorias/nova/', views.nova_categoria, name='nova_categoria'),
    path('categorias/excluir/<int:id>/', views.excluir_categoria, name='excluir_categoria'),

    # === Favoritos ===
    path('favoritos/', views.listar_favoritos, name='listar_favoritos'),
    path('favoritos/novo/', views.adicionar_favorito, name='adicionar_favorito'),

    # === Órgãos, Departamentos e Secretarias ===
    path('orgaos/', views.listar_orgaos, name='listar_orgaos'),
    path('orgaos/novo/', views.novo_orgao, name='novo_orgao'),

    path('departamentos/', views.listar_departamentos, name='listar_departamentos'),
    path('departamentos/novo/', views.novo_departamento, name='novo_departamento'),

    path('secretarias/', views.listar_secretarias, name='listar_secretarias'),
    path('secretarias/nova/', views.nova_secretaria, name='nova_secretaria'),

    # === Digitalização ===
    path('digitalizar/', views.listar_digitalizacoes, name='listar_digitalizacoes'),
    path('digitalizar/nova/', views.digitalizar_documento, name='digitalizar_documento'),
    path('upload-digitalizacao/', views.upload_digitalizacao, name='upload_digitalizacao'),

    # === Tramitação e Encaminhamentos ===
    path('documentos/<int:doc_id>/encaminhar/', views.encaminhar_documento, name='encaminhar_documento'),
    path('documentos-com-encaminhamento/', views.lista_documentos_encaminhados, name='documentos_com_encaminhamento'),
    path('tramite/<int:tramite_id>/responder/', views.responder_tramitacao, name='responder_tramitacao'),
    path('tramitacao/<int:tramite_id>/upload-retorno/', views.enviar_documento_retorno, name='enviar_documento_retorno'),
    path('historico-tramitacao/<int:tramite_id>/', views.historico_tramitacao, name='historico_tramitacao'),

    # === Usuários ===
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/cadastrar/', views.cadastrar_usuario, name='cadastrar_usuario'),
]
