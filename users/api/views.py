from rest_framework import viewsets, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import Usuario
from .serializers import UsuarioSerializer, CrearUsuarioSerializer
from .permissions import EsAdministrador


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    permission_classes = [permissions.IsAuthenticated, EsAdministrador]

    def get_serializer_class(self):
        if self.action == 'create':
            return CrearUsuarioSerializer
        return UsuarioSerializer
    
class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()  # lo agrega a la blacklist
            return Response({'detail': 'Sesión cerrada correctamente'})
        except Exception:
            return Response(
                {'error': 'Token inválido o ya expirado'},
                status=status.HTTP_400_BAD_REQUEST
            )    