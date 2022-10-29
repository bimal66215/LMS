from django.db import models
from datetime import datetime


class Log(models.Model):

    # Allowed Values for Type of Log
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
    logged_on = models.DateTimeField(null=True, blank=True)
    warning_cnt_two_hrs = models.IntegerField()
    agg_error_cnt_two_hrs = models.IntegerField()

    # Custom Save Function
    def save(self, *args, **kwargs):
        if self.logged_on is None:
            self.logged_on = datetime.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.message
