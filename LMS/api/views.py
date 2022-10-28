from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import LogSerializer
from .models import Log
from datetime import timedelta, datetime
from rest_framework.authentication import TokenAuthentication


# create a Viewset
class LogViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = LogSerializer
    queryset = Log.objects.none()

    # Token.objects.get(user=)
    def create(self, request, *args, **kwargs):
        log_data = request.data
        print(log_data)

        warning_cnt_two_hrs = Log.objects.filter(logged_on__gte=datetime.now() - timedelta(hours=2)).filter(
            type__exact='WARNING').count()
        agg_error_cnt_two_hrs = Log.objects.filter(logged_on__gte=datetime.now() - timedelta(hours=2)).filter(
            type__exact='ERROR').count()

        new_log = Log.objects.create(severity=log_data['severity'], app_name=log_data['app_name'],
                                     message=log_data['message'], type=log_data['type'],
                                     warning_cnt_two_hrs=warning_cnt_two_hrs,
                                     agg_error_cnt_two_hrs=agg_error_cnt_two_hrs)
        new_log.save()
        serializer = LogSerializer(new_log)

        headers = super().get_success_headers(serializer.data)
        print(headers)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        id = self.request.query_params.get('id')
        type = self.request.query_params.get('type')
        app_name = self.request.query_params.get('app_name')
        total_records_last_n_hrs = self.request.query_params.get('total_records_last_n_hrs')
        latest_n_records = self.request.query_params.get('latest_n_records')

        filtered_log = Log.objects.all()

        if id is not None:
            filtered_log = filtered_log.filter(id__exact=int(id)).order_by('logged_on')

        if total_records_last_n_hrs is not None:
            filtered_log = filtered_log.filter(logged_on__gte=datetime.now() - timedelta(hours=int(total_records_last_n_hrs)))
            # print()

        if latest_n_records is not None:
            filtered_log = filtered_log.order_by('-logged_on')[:int(latest_n_records)]
            filtered_log = reversed(filtered_log)

        if type is not None and app_name is None:
            filtered_log = filtered_log.filter(type__exact=type).order_by('logged_on')

        if app_name is not None and type is None:
            filtered_log = filtered_log.filter(app_name_exact=app_name).order_by('logged_on')

        if type is not None and app_name is not None:
            filtered_log = filtered_log.filter(type__exact=type).filter(app_name_exact=app_name).order_by('logged_on')

        serializer = LogSerializer(filtered_log, many=True)

        return Response(serializer.data)

