from django.db import models

class User(models.Model):
    name=models.CharField(max_length=30)
    email=models.EmailField()
    password1=models.CharField(max_length=30)
    password2=models.CharField(max_length=30)

    def __str__(self):
        return self.name
class UserPrompt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_message = models.TextField()
    chatbot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prompt by {self.user.name} on {self.timestamp}"