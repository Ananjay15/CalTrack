import json
import requests
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "tinyllama"

@login_required
def chat_assistant(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        body = json.loads(request.body)
        message = body.get('message', '').strip()
    except:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    prompt = f"System: You are a helpful fitness assistant.\nUser: {message}\nAssistant:"
    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": 256}
        }, timeout=30)
        reply = resp.json()['response']
        return JsonResponse({'reply': reply})
    except Exception as e:
        return JsonResponse({'error': f'Ollama error: {str(e)}'}, status=503)