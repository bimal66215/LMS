from rest_framework import serializers
from .models import Log


# Creating a model serializer
class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ['id', 'severity', 'app_name', 'type', 'message', 'logged_on', 'warning_cnt_two_hrs',
                  'agg_error_cnt_two_hrs']