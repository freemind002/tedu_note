from django.db import models

# Create your models here.

class User(models.Model):
    username = models.CharField("用戶名", max_length=30, unique=True)
    password = models.CharField("密碼", max_length=32)
    created_time = models.DateTimeField('創建時間', auto_now_add=True)
    updated_time = models.DateTimeField('更新時間', auto_now=True)

    def __str__(self):
        return 'username %s' % (self.username)