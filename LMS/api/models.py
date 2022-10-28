from django.db import models



class Log(models.Model):

    log_type = (
        ('WARNING', 'WARNING'),
        ('DEBUG', 'DEBUG'),
        ('INFO', 'INFO'),
        ('ERROR', 'ERROR'),
        ('CRITICAL', 'CRITICAL')
    )

    severity = models.CharField(max_length=200)
    app_name = models.CharField(max_length=50)
    type = models.CharField(max_length=50, choices=log_type,
                            default='INFO')
    message = models.TextField()
    logged_on = models.DateTimeField(auto_now_add=True)
    warning_cnt_two_hrs = models.IntegerField()
    agg_error_cnt_two_hrs = models.IntegerField()

    def __str__(self):
        return self.message

