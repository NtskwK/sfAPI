from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework import serializers, permissions, status, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        field = '__all__'


class UserViewSet(viewsets.ModelViewSet):
    serializers_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = User.objects.all()
        return queryset

    # logical delete
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telephone_number = models.CharField(max_length=11, blank=True)
    is_delete = models.DateTimeField(blank=True, null=True)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        exclude = ('id', )
        read_only_fields = ('user',)


class UserProfileViewSet(viewsets.ModelViewSet):
    class Meta:
        model = UserProfile
        serializer_class = UserProfileSerializer
        permission_classes = [IsAdminUser]
        lookup_field = 'user'

    def get_queryset(self):
        return UserProfile.objects.all()

    # logical delete
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
