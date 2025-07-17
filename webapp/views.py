from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Orgao, Departamento, Secretaria, PerfilUsuario
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render
from .models import Documento, Orgao
from .models import (
    Documento, Categoria, Favorito,
    Orgao, Departamento, Secretaria,
    DocumentoDigitalizado
)
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from .models import Documento, Favorito

from django.utils.timezone import now
from django.contrib.auth.models import User
from datetime import datetime
from .models import Documento, Favorito
from datetime import timedelta
from django.utils import timezone




# ========================================================================================================================



from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Documento, Favorito
from django.contrib.auth.models import User

@login_required
def index(request):
    usuario = request.user
    hoje = now()
    primeiro_dia_mes = hoje.replace(day=1)

    total_documentos = Documento.objects.filter(usuario=usuario).count()
    total_favoritos = Favorito.objects.filter(usuario=usuario).count()
    ultimo_documento = Documento.objects.filter(usuario=usuario).order_by('-data_envio').first()
    uploads_mes = Documento.objects.filter(usuario=usuario, data_envio__gte=primeiro_dia_mes).count()
    usuarios_ativos = User.objects.filter(is_active=True).count()
    atividades = Documento.objects.filter(usuario=usuario).order_by('-data_envio')[:5]
    documentos_recentes = Documento.objects.filter(usuario=usuario).order_by('-data_envio')[:10]

    dias_desde_ultimo = None
    if ultimo_documento:
        dias_desde_ultimo = (hoje - ultimo_documento.data_envio).days

    # Indicadores de progresso (valores estáticos por enquanto)
    uso_armazenamento = 65
    meta_uploads = 82
    backup_concluido = 100

    return render(request, 'arquivos/index.html', {
        'total_documentos': total_documentos,
        'total_favoritos': total_favoritos,
        'dias_desde_ultimo': dias_desde_ultimo,
        'uploads_mes': uploads_mes,
        'usuarios_ativos': usuarios_ativos,
        'arquivos_protegidos': total_documentos,  # provisório
        'compartilhamentos': 9,
        'atividades': atividades,
        'documentos_recentes': documentos_recentes,
        'uso_armazenamento': uso_armazenamento,
        'meta_uploads': meta_uploads,
        'backup_concluido': backup_concluido,
    })




# ========================================================================================================================


def BASE(request):
    return render(request, 'base.html')
# ========================================================================================================================

def pagina_inicial(request):
    return render(request, 'arquivos/index.html')

# === ARQUIVOS =====================================================================================

from django.contrib.auth.models import User

def listar_arquivos(request):
    busca = request.GET.get('q', '')
    if request.user.is_superuser:
        arquivos = Documento.objects.filter(titulo__icontains=busca).order_by('-data_envio')
    else:
        arquivos = Documento.objects.filter(titulo__icontains=busca, usuario=request.user).order_by('-data_envio')
    paginator = Paginator(arquivos, 10)
    page = request.GET.get('page')
    arquivos_paginados = paginator.get_page(page)

    orgaos = Orgao.objects.prefetch_related('departamentos__secretarias').all()
    usuarios = User.objects.filter(is_active=True).order_by('first_name')  # <-- Adicione isto

    return render(request, 'arquivos/listar.html', {
        'arquivos': arquivos_paginados,
        'busca': busca,
        'orgaos': orgaos,
        'usuarios': usuarios  # <-- ESSENCIAL!
    })

# ========================================================================================================================

def cadastrar_arquivo(request):
    categorias = Categoria.objects.all()
    orgaos = Orgao.objects.all()
    departamentos = Departamento.objects.select_related('orgao').all()
    secretarias = Secretaria.objects.select_related('departamento').all()

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        categoria_id = request.POST.get('categoria')
        orgao_id = request.POST.get('orgao') or None
        departamento_id = request.POST.get('departamento') or None
        secretaria_id = request.POST.get('secretaria') or None
        observacoes = request.POST.get('observacoes', '')
        arquivo = request.FILES.get('arquivo')

        Documento.objects.create(
            titulo=titulo,
            categoria_id=categoria_id,
            orgao_id=orgao_id,
            departamento_id=departamento_id,
            secretaria_id=secretaria_id,
            observacoes=observacoes,
            arquivo=arquivo,
            usuario=request.user  # <-- adiciona o vínculo com o usuário logado
        )


        return redirect('listar_arquivos')

    return render(request, 'arquivos/cadastrar.html', {
        'categorias': categorias,
        'orgaos': orgaos,
        'departamentos': departamentos,
        'secretarias': secretarias
    })

# === CATEGORIAS =====================================================================================

def listar_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'categorias/listar.html', {'categorias': categorias})
# ========================================================================================================================

def nova_categoria(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        Categoria.objects.create(nome=nome)
        return redirect('listar_categorias')
    return render(request, 'categorias/nova.html')
# ========================================================================================================================

def excluir_categoria(request, id):
    Categoria.objects.get(id=id).delete()
    return redirect('listar_categorias')

# === FAVORITOS =====================================================================================

def listar_favoritos(request):
    favoritos = Favorito.objects.all().order_by('-criado_em')
    return render(request, 'favoritos/listar.html', {'favoritos': favoritos})
# ========================================================================================================================

def adicionar_favorito(request):
    if request.method == 'POST':
        nome = request.POST['nome']
        url = request.POST['url']
        Favorito.objects.create(
            nome=nome,
            url=url,
            usuario=request.user  # <-- adiciona o vínculo corretamente
        )
        return redirect('listar_favoritos')
    return render(request, 'favoritos/novo.html')


# === ÓRGÃOS, DEPARTAMENTOS E SECRETARIAS ===========================================================

def listar_orgaos(request):
    orgaos = Orgao.objects.all()
    return render(request, 'orgaos/listar.html', {'orgaos': orgaos})
# ========================================================================================================================

def novo_orgao(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        if nome:
            Orgao.objects.create(nome=nome)
            return redirect('listar_orgaos')
    return render(request, 'orgaos/novo.html')
# ========================================================================================================================

def listar_departamentos(request):
    departamentos = Departamento.objects.select_related('orgao').all()
    return render(request, 'departamentos/listar.html', {'departamentos': departamentos})
# ========================================================================================================================

def novo_departamento(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        orgao_id = request.POST.get('orgao')
        if nome and orgao_id:
            Departamento.objects.create(nome=nome, orgao_id=orgao_id)
            return redirect('listar_departamentos')
    orgaos = Orgao.objects.all()
    return render(request, 'departamentos/novo.html', {'orgaos': orgaos})
# ========================================================================================================================

def listar_secretarias(request):
    secretarias = Secretaria.objects.select_related('departamento', 'departamento__orgao').all()
    return render(request, 'secretarias/listar.html', {'secretarias': secretarias})
# ========================================================================================================================

def nova_secretaria(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        departamento_id = request.POST.get('departamento')
        if nome and departamento_id:
            departamento = Departamento.objects.get(id=departamento_id)
            Secretaria.objects.create(nome=nome, departamento=departamento)
            return redirect('listar_secretarias')
    departamentos = Departamento.objects.select_related('orgao').all()
    return render(request, 'secretarias/nova.html', {'departamentos': departamentos})

# === DIGITALIZAÇÃO =====================================================================================

def listar_digitalizacoes(request):
    documentos = DocumentoDigitalizado.objects.all().order_by('-data_criacao')
    return render(request, 'digitalizar/listar.html', {'documentos': documentos})
# ========================================================================================================================

def digitalizar_documento(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        arquivo = request.FILES.get('arquivo')
        observacoes = request.POST.get('observacoes', '')

        if titulo and arquivo:
            DocumentoDigitalizado.objects.create(
                titulo=titulo,
                arquivo=arquivo,
                observacoes=observacoes
            )
            messages.success(request, "Documento digitalizado com sucesso.")
            return redirect('listar_digitalizacoes')
        else:
            messages.error(request, "Preencha todos os campos obrigatórios.")

    return render(request, 'digitalizar/form.html')

# === DOCUMENTOS COM ENCAMINHAMENTO =======================================================================

from django.contrib.auth.models import User

def listar_documentos(request):
    busca = request.GET.get('q', '')
    if request.user.is_superuser:
        documentos = Documento.objects.all()
    else:
        documentos = Documento.objects.filter(usuario=request.user)


    if busca:
        documentos = documentos.filter(
            Q(titulo__icontains=busca) |
            Q(categoria__nome__icontains=busca) |
            Q(observacoes__icontains=busca)
        )

    orgaos = Orgao.objects.prefetch_related('departamentos__secretarias').all()

    # ✅ Adicione esta linha
    usuarios = User.objects.filter(is_active=True).order_by('first_name')

    context = {
        'arquivos': documentos,
        'orgaos': orgaos,
        'usuarios': usuarios,  # <-- ESSENCIAL
        'busca': busca,
    }
    return render(request, 'digitalizar/listar.html', context)



# ========================================================================================================================

from .models import Tramitacao

def encaminhar_documento(request, doc_id):
    if request.method == "POST":
        departamento_id = request.POST.get("departamento_id")
        secretaria_id = request.POST.get("secretaria_id")
        usuario_destino_id = request.POST.get("usuario_destino_id")
        mensagem = request.POST.get("mensagem")

        documento = get_object_or_404(Documento, id=doc_id)
        destino = None

        if usuario_destino_id:
            destinatario = get_object_or_404(User, id=usuario_destino_id)
        else:
            return HttpResponse("Usuário de destino não informado.", status=400)

        if secretaria_id:
            destino = get_object_or_404(Secretaria, id=secretaria_id)
        elif departamento_id:
            destino = get_object_or_404(Departamento, id=departamento_id)

        # Criar registro de tramitação
        Tramitacao.objects.create(
            documento=documento,
            remetente=request.user,
            destinatario=destinatario,
            mensagem=mensagem,
            status='aberto'
        )

        messages.success(request, "Documento encaminhado com sucesso.")
        return redirect(request.META.get('HTTP_REFERER', reverse('listar_documentos')))

    return HttpResponse("Método não permitido", status=405)

# ========================================================================================================================

def cadastrar_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Usuário já existe.")
            return redirect('cadastrar_usuario')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        orgao_id = request.POST.get('orgao') or None
        departamento_id = request.POST.get('departamento') or None
        secretaria_id = request.POST.get('secretaria') or None

        # Converte IDs
        orgao_id = int(orgao_id) if orgao_id else None
        departamento_id = int(departamento_id) if departamento_id else None
        secretaria_id = int(secretaria_id) if secretaria_id else None

        # Cria ou atualiza o perfil
        perfil, created = PerfilUsuario.objects.get_or_create(
            user=user,
            defaults={
                'orgao_id': orgao_id,
                'departamento_id': departamento_id,
                'secretaria_id': secretaria_id
            }
        )

        if not created:
            perfil.orgao_id = orgao_id
            perfil.departamento_id = departamento_id
            perfil.secretaria_id = secretaria_id
            perfil.save()

        messages.success(request, "Usuário cadastrado com sucesso.")
        return redirect('listar_usuarios')

    context = {
        'orgaos': Orgao.objects.all(),
        'departamentos': Departamento.objects.all(),
        'secretarias': Secretaria.objects.all()
    }
    return render(request, 'usuarios/cadastrar.html', context)
# ========================================================================================================================

def listar_usuarios(request):
    usuarios = PerfilUsuario.objects.select_related('user', 'orgao', 'departamento', 'secretaria')
    return render(request, 'usuarios/listar.html', {'usuarios': usuarios})
# ========================================================================================================================

@csrf_exempt
def upload_digitalizacao(request):
    if request.method == "POST":
        titulo = request.POST.get("titulo")
        observacoes = request.POST.get("observacoes", "")
        arquivo = request.FILES.get("file")  # Aspose envia como "file"

        if titulo and arquivo:
            DocumentoDigitalizado.objects.create(
                titulo=titulo,
                observacoes=observacoes,
                arquivo=arquivo
            )
            return JsonResponse({"status": "ok"})
        else:
            return JsonResponse({"status": "error"}, status=400)
# ========================================================================================================================

from django.contrib.auth import authenticate, login
from webapp.models import Tramitacao

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Busca trâmites abertos para esse usuário
            tramitacoes = Tramitacao.objects.filter(destinatario=user, status='aberto')
            return render(request, 'login/login.html', {
                'login_sucesso': True,
                'tramitacoes': tramitacoes
            })
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    
    return render(request, 'login/login.html')


# ========================================================================================================================

from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


from django.contrib.auth.models import User

def documentos_arquivados(request):
    documentos = Documento.objects.all()
    orgaos = Orgao.objects.prefetch_related('departamentos__secretarias')

    # Exemplo: listar todos os usuários ativos
    usuarios = User.objects.filter(is_active=True).order_by('first_name')

    return render(request, 'documentos/listar.html', {
        'documentos': documentos,
        'orgaos': orgaos,
        'usuarios': usuarios,
    })


from django.utils.timezone import now

@login_required
def responder_tramitacao(request, tramitacao_id):
    tramitacao = get_object_or_404(Tramitacao, id=tramitacao_id, destinatario=request.user)

    if request.method == 'POST':
        resposta = request.POST.get('resposta')
        acao = request.POST.get('acao')  # 'responder' ou 'finalizar'

        tramitacao.resposta = resposta
        tramitacao.data_resposta = now()
        tramitacao.status = 'finalizado' if acao == 'finalizar' else 'respondido'
        tramitacao.save()

        messages.success(request, 'Tramitação respondida com sucesso.')
        return redirect('listar_documentos')  # ou painel de trâmites

    return render(request, 'tramitacoes/responder.html', {'tramitacao': tramitacao})


@login_required
def minhas_tramitacoes(request):
    tramitacoes = Tramitacao.objects.filter(destinatario=request.user, status='aberto').order_by('-data_envio')
    return render(request, 'tramitacoes/minhas_tramitacoes.html', {'tramitacoes': tramitacoes})


# webapp/context_processors.py
from .models import Tramitacao

def notificacoes_documentos(request):
    if request.user.is_authenticated:
        tramitacoes = Tramitacao.objects.filter(
            destinatario=request.user,
            respondido=False
        ).order_by('-data_envio')
        return {'tramitacoes_pendentes': tramitacoes}
    return {}


from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Tramitacao
from django.utils.timezone import now

@login_required
def responder_tramitacao(request, tramite_id):
    tramite = get_object_or_404(Tramitacao, id=tramite_id, destinatario=request.user)

    if request.method == 'POST':
        resposta = request.POST.get('resposta')
        status = request.POST.get('status')

        tramite.resposta = resposta
        tramite.status = status
        tramite.data_resposta = now()
        tramite.save()

        return redirect('dashboard')  # ou onde preferir

    return redirect('dashboard')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Tramitacao

@login_required
def lista_documentos_encaminhados(request):
    tramitacoes = Tramitacao.objects.filter(destinatario=request.user).order_by('-data_envio')
    return render(request, 'documentos/documentos_encaminhados.html', {'tramitacoes': tramitacoes})



from django.shortcuts import render, get_object_or_404
from .models import Tramitacao

def historico_tramitacao(request, tramite_id):
    tramite = get_object_or_404(Tramitacao, id=tramite_id)
    historico = Tramitacao.objects.filter(documento=tramite.documento).order_by('-data_envio')

    return render(request, 'tramitacao/historico_tramitacao.html', {
        'tramite': tramite,
        'historico': historico,
    })



def enviar_documento_retorno(request, tramite_id):
    tramite = get_object_or_404(Tramitacao, id=tramite_id)

    if request.method == 'POST' and request.FILES.get('documento_retorno'):
        documento = request.FILES['documento_retorno']
        tramite.documento_retorno = documento
        tramite.save()
        messages.success(request, "Documento retornado enviado com sucesso.")
    else:
        messages.error(request, "Você deve selecionar um documento válido.")

    return redirect('listar_arquivos')  # ou sua view de origem

