import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from django.core.files.storage import FileSystemStorage
from django.conf import settings
from pathlib import Path
from django.utils.timezone import now

from accounts.auth import Authentication
from accounts.serializers import UserModelSerializer
from accounts.models import User

from app.utils.exceptions import ValidationError


class SignInView(APIView, Authentication):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email', '')
        password = request.data.get('password', '')

        signin = self.signin(email, password)

        if not signin:
            raise AuthenticationFailed

        user = UserModelSerializer(signin).data
        access_token = RefreshToken.for_user(signin).access_token

        return Response({
            "user": user,
            "access_token": str(access_token)
        })


class SignUpView(APIView, Authentication):
    permission_classes = (AllowAny,)

    def post(self, request):
        name = request.data.get('name', '')
        email = request.data.get('email', '')
        password = request.data.get('password', '')

        if not name or not email or not password:
            raise AuthenticationFailed

        signup = self.signup(name, email, password)

        if not signup:
            raise AuthenticationFailed

        user = UserModelSerializer(signup).data
        access_token = RefreshToken.for_user(signup).access_token

        return Response({
            "user": user,
            "access_token": str(access_token)
        })


class UserView(APIView):
    def get(self, request):
        # Update last_access
        User.objects.filter(id=request.user.id).update(last_access=now())

        user = UserModelSerializer(request.user).data

        return Response({
            "user": user
        })

    def put(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        password = request.data.get('password')
        avatar = request.FILES.get('avatar')

        # Initialize storage
        storage = FileSystemStorage(
            str(Path(settings.MEDIA_ROOT) / "avatars"),
            settings.MEDIA_URL + "avatars"
        )

        if avatar:
            content_type = avatar.content_type

            # Extensão do arquivo, último elemento do array [-1] após o ponto
            extension = avatar.name.split('.')[-1]

            # Validate avatar tipo de arquivo aceito
            if not content_type == "image/png" and not content_type == "image/jpeg":
                raise ValidationError(
                    "Somente arquivos do tipo PNG ou JPEG são suportados")

            # Save new avatar
            file = storage.save(f"{uuid.uuid4()}.{extension}", avatar)
            avatar = storage.url(file)

        serializer = UserModelSerializer(request.user, data={
            "name": name,
            "email": email,
            "avatar": avatar or request.user.avatar
        })

        # Se não for valido o serializer
        if not serializer.is_valid():
            # Delete uploaded file
            if avatar:
                # Deletar arquivo enviado, último elemento do array [-1] após o ponto
                storage.delete(avatar.split("/")[-1])

            # Obter primeira mensagem de erro (string)
            first_error = list(serializer.errors.values())[0][0]

            raise ValidationError(first_error)

        # Delete o avatar antigo enviado caso seja diferente do padrão
        if avatar and request.user.avatar != "/media/avatars/default-avatar.png":
            # Deletar arquivo enviado, último elemento do array [-1] após o ponto
            storage.delete(request.user.avatar.split("/")[-1])

        # Update password
        if password:
            request.user.set_password(password)

        serializer.save()

        return Response({
            "user": serializer.data
        })
