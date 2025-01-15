from django.db import models


class Script(models.Model):
    prompt = models.TextField()
    generated_script = models.TextField()
    language = models.CharField(
        max_length=10, default='en')  # Store language code
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Format the created_at timestamp in 24-hour format
        return f"Script {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
