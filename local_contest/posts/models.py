from django.db import models
from django.conf import settings

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    description = models.TextField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    likes = models.IntegerField(default=0)
    published = models.BooleanField(default=False)

    def __str__(self):
        return self.description
    
    def like(self):
        self.likes += 1
        self.save()

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} a liké {self.post.description}"