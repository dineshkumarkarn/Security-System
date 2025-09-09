from django.db import models



class Attendance(models.Model):
    name = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.timestamp}"
    


class AnomalyClip(models.Model):
    clip_file = models.FileField(upload_to='anomaly_clips/')
    timestamp = models.DateTimeField(auto_now_add=True)
    severity = models.CharField(max_length=10, default="Unusual")  # "High" or "Unusual"

    def __str__(self):
        return f"AnomalyClip {self.id} ({self.severity}) at {self.timestamp}"




