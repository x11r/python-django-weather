from django.db import models
from django.utils import timezone

class Dailies(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField('測定日')
    prefecture_id = models.SmallIntegerField('都道府県ID')
    station_name = models.CharField('測定地点名', max_length=128)
    temperature_highest = models.DecimalField(
        '最高気温（摂氏）', 
        max_digits=4,
        decimal_places=1,
        null=True,
    )
    temperature_lowest = models.DecimalField(
        '最低気温（摂氏）', 
        max_digits=4, 
        decimal_places=1, 
        null=True,
    )

    # created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'prefecture_id', 'station_name'],
                name='unique_date_prefecture_id_station_name',
            )
        ]
        unique_together = ('date', 'prefecture_id', 'station_name')
        indexes = [
            models.Index(fields=['date', 'prefecture_id', 'station_name']),
            models.Index(fields=['date', 'station_name']),
        ]
