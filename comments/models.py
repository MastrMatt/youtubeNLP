from django.db import models

# Create your models here.
class Comment(models.Model):
    name = models.CharField(max_length=100)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        return "Comment {} by {}".format(self.body, self.name)
