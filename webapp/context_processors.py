from .models import Tramitacao

def notificacoes_documentos(request):
    if request.user.is_authenticated:
        tramitacoes = Tramitacao.objects.filter(
            destinatario=request.user,
            status='aberto'  # CORRETO conforme seu model
        ).order_by('-data_envio')
        return {'tramitacoes_pendentes': tramitacoes}
    return {}
