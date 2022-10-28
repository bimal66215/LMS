from rest_framework import serializers
from .models import Log
from django.contrib.auth.models import User


# Creating a model serializer
class LogSerializer(serializers.ModelSerializer):
    # specify model and fields
    # warning_cnt = serializers.SerializerMethodField()
    # agg_error_cnt = serializers.SerializerMethodField()
    class Meta:
        model = Log
        fields = ['id', 'severity', 'app_name', 'type', 'message', 'logged_on', 'warning_cnt_two_hrs',
                  'agg_error_cnt_two_hrs']
#
#
# class userSerializers(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = '__all__'
