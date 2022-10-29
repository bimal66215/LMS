from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from .serializers import LogSerializer
from .models import Log
from datetime import timedelta, datetime
from rest_framework.authentication import TokenAuthentication
import re


# create a Custom ViewSet
class LogViewSet(viewsets.ModelViewSet):
    # Setting the Authentications. Hence, any request made to this ViewSet needs to have a valid Token in the Header.
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Creating the Serializer Object
    serializer_class = LogSerializer

    # Default Query set
    queryset = Log.objects.none()

    # Custom Create method used for Post Requests.
    def create(self, request, *args, **kwargs):

        uploaded_file = request.FILES.get('uploaded_file', None)

        # API can be used directly to push data into the DataBase or a Log File(Tab formatted file) can be uploaded,
        # the uploaded file be mapped accordingly and pushed to the Database.
        # checking if a File is Uploaded or not
        if uploaded_file is None:

            # If File is not uploaded then, API is expecting values of 'severity', 'app_name',
            # 'message', 'type' along with the POST request.

            log_data = request.data

            # Creating the Count of Warning and Error Logs in the Past 2 Hours.
            warning_cnt_two_hrs = Log.objects.filter(logged_on__gte=datetime.now() - timedelta(hours=2)).filter(
                type__exact='WARNING').count()
            agg_error_cnt_two_hrs = Log.objects.filter(logged_on__gte=datetime.now() - timedelta(hours=2)).filter(
                type__exact='ERROR').count()

            # If received log is already a 'WARNING' type then add 1 to the WARNING count
            if log_data['type'] == "WARNING":
                warning_cnt_two_hrs = warning_cnt_two_hrs + 1
            # If received log is already a 'ERROR' type then add 1 to the ERROR count
            if log_data['type'] == "ERROR":
                agg_error_cnt_two_hrs = agg_error_cnt_two_hrs + 1

            # Creating and Saving the Log Entry
            new_log = Log.objects.create(severity=log_data['severity'], app_name=log_data['app_name'],
                                         message=log_data['message'], type=log_data['type'],
                                         warning_cnt_two_hrs=warning_cnt_two_hrs,
                                         agg_error_cnt_two_hrs=agg_error_cnt_two_hrs)
            new_log.save()

            # Serializing the data, so that it can be send in the Response
            serializer = LogSerializer(new_log)

            # Calling the function from Parent Class to generate Headers
            headers = super().get_success_headers(serializer.data)

            # Returning the Data in Json format, along with Status Code and Headers
            return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

        else:
            # Reading the Uploaded File and assinging them to the respective Variables
            for line_num, line in enumerate(uploaded_file.read().decode().splitlines()):

                # Splitting by '/t' TAB
                items = re.split(r'\t+', line.rstrip('\t'))

                # Converting the String to Datetime object only if the Datetime value is present in the Log File.
                # If not or in the incorrect Order then the error message will be added to the response
                # and the Line will be skipped.
                try:
                    pattern = "%Y-%m-%dT%H:%M:%S.%f"
                    logged_on = datetime.strptime(items[0], pattern)
                except ValueError :
                    mes = f"The DateField is either not in '{pattern}' format or it is missing, at Line Number {line_num+1} of the Log File "
                    continue

                severity = items[1]
                app_name = items[2]
                type = items[3]
                message = items[4]

                warning_cnt_two_hrs = Log.objects.filter(logged_on__gte=logged_on - timedelta(hours=2)).filter(
                    type__exact='WARNING').count()
                agg_error_cnt_two_hrs = Log.objects.filter(logged_on__gte=logged_on - timedelta(hours=2)).filter(
                    type__exact='ERROR').count()

                if type == "WARNING":
                    warning_cnt_two_hrs = warning_cnt_two_hrs + 1
                if type == "ERROR":
                    agg_error_cnt_two_hrs = agg_error_cnt_two_hrs + 1

                new_log = Log(severity=severity, app_name=app_name,
                              message=message, type=type,
                              warning_cnt_two_hrs=warning_cnt_two_hrs,
                              agg_error_cnt_two_hrs=agg_error_cnt_two_hrs, logged_on=logged_on)

                # Here we should not enter current DateTime and just need to use the DateTime provided in the LogFile.
                # Hence, we have used the custom save function created in the Log Model.
                new_log.save()

            return HttpResponse(f"<p>Log Data successfully added to the Database.<br><b>Error</b>: {mes}</p>")

    def list(self, request, *args, **kwargs):

        # Created certain List views based on certain Filters. You can provide
        # the values in the Parameters of the URL to access the respective filtered View.
        id = self.request.query_params.get('id')
        type = self.request.query_params.get('type')
        app_name = self.request.query_params.get('app_name')
        total_records_last_n_hrs = self.request.query_params.get('total_records_last_n_hrs')
        latest_n_records = self.request.query_params.get('latest_n_records')

        filtered_log = Log.objects.all()

        if id is not None:
            filtered_log = filtered_log.filter(id__exact=int(id)).order_by('logged_on')

        if total_records_last_n_hrs is not None:
            filtered_log = filtered_log.filter(
                logged_on__gte=datetime.now() - timedelta(hours=int(total_records_last_n_hrs)))

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

        return Response(serializer.data, status=status.HTTP_200_OK)
