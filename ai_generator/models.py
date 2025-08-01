from django.db import models
from django.contrib.auth import get_user_model
from account.models import User

class AIChat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_chats')
    message = models.TextField(help_text="User's message to AI")
    ai_response = models.TextField(help_text="AI's response")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Chat for {self.user.email} at {self.created_at}"