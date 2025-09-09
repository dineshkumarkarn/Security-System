from datetime import datetime, timezone
from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from video_capture.pc_camera import generate_frames_detect ,generate_frames_normal
from video.mobile_camera_processing import generate_mobile_detect_frames ,generate_mobile_normal_frames
from .models import Attendance , AnomalyClip
from detection.face_recognition import generate_combined_stream , add_new_face
from detection.abnormal_detection import generate_frames_normal_for_anomaly



def index(request):
    attendances = Attendance.objects.all().order_by('-timestamp')[:10]
    return render(request, "index.html", {'attendances': attendances})

def start_normal(request):
    return StreamingHttpResponse(generate_frames_normal(),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

def start_detection(request):
    return StreamingHttpResponse(generate_frames_detect(),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


def start_mobile_detection(request):
    return StreamingHttpResponse(generate_mobile_detect_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

def start_mobile_normal(request):
    return StreamingHttpResponse(generate_mobile_normal_frames(),
                                 content_type='multipart/x-mixed-replace; boundary=frame')
def start_face(request):
    return StreamingHttpResponse(generate_combined_stream(),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

def add_face(request):
    """
    Processes the add-face form submission:
      - Accepts a name and an image file.
      - Calls add_new_face() to store the new face.
    """
    message = None
    if request.method == 'POST':
        name = request.POST.get('name')
        face_image = request.FILES.get('face_image')
        if name and face_image:
            add_new_face(name, face_image)
            message = "Face added successfully!"
        else:
            message = "Please provide both a name and a face image."
    return render(request, 'add_face.html', {'message': message})

def anomaly_stream(request):
    return StreamingHttpResponse(
        generate_frames_normal_for_anomaly(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )
    
def all_anomalies(request):
    
    hard_clips = AnomalyClip.objects.filter(severity="High").order_by('-timestamp')
    unusual_clips = AnomalyClip.objects.filter(severity="Unusual").order_by('-timestamp')
    return render(request, 'anomaly.html', {
        'hard_clips': hard_clips,
        'unusual_clips': unusual_clips,
    })
    
def alert_status(request):
    recent_time = timezone.now() - datetime.timedelta(minutes=1)
    high_alert = AnomalyClip.objects.filter(severity="High", timestamp__gte=recent_time).exists()
    unusual_alert = AnomalyClip.objects.filter(severity="Unusual", timestamp__gte=recent_time).exists()
    return JsonResponse({"high": high_alert, "unusual": unusual_alert})
    