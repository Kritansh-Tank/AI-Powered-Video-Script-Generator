from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
import requests
import pytesseract
from pdfminer.high_level import extract_text
from PIL import Image
import os
import pytesseract
from .models import Script
import json
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import io
from reportlab.pdfgen import canvas
import textract

pytesseract.pytesseract.tesseract_cmd = r"K:\GTA\Tesseract-OCR\tesseract.exe"


HUGGINGFACE_API_KEY = "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"
HUGGINGFACE_MODEL = "bigscience/bloom"


def home(request):
    return render(request, 'script_generator/home.html')


@csrf_exempt
def generate_script(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '').strip()
        files = request.FILES.getlist('files')
        selected_text = request.POST.get('selected_text', '')
        external_links = request.POST.getlist('links', [])
        language = request.POST.get(
            'language', 'English').strip()  # Use full language name

        if not prompt and not files and not external_links:
            return JsonResponse({"error": "Please provide a prompt, file(s), or link(s)."}, status=400)

        enhanced_prompt = f"Generate the following script in {language}:\n{prompt}\n\nAdditional Context:\n{selected_text}"

        extracted_text = ""
        for file in files:
            extracted_text += handle_file(file)

        for link in external_links:
            extracted_text += fetch_link_metadata(link)

        enhanced_prompt = f"Generate the following script in {language}:\n{prompt}\n\nAdditional Context:\n{extracted_text}"

        url = f"https://api-inference.huggingface.co/models/{HUGGINGFACE_MODEL}"
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
        }
        payload = {
            "inputs": enhanced_prompt,
            "parameters": {"max_new_tokens": 500},
            "options": {"use_cache": True, "wait_for_model": True}
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            print(response_data)  # Debugging: Log response

            generated_text = response_data[0].get("generated_text", "") if isinstance(
                response_data, list) else response_data.get("generated_text", "")

            # Filter repetitive text (Optional)
            from difflib import SequenceMatcher

            def remove_redundancy(text):
                chunks = text.split('. ')
                unique_chunks = []
                for i, chunk in enumerate(chunks):
                    if all(SequenceMatcher(None, chunk, prev).ratio() < 0.8 for prev in unique_chunks):
                        unique_chunks.append(chunk)
                return '. '.join(unique_chunks)

            generated_text = remove_redundancy(generated_text)

            # Save the script
            script = Script.objects.create(
                prompt=prompt, generated_script=generated_text, language=language)
            return JsonResponse({"script": generated_text, "script_id": script.id})

        else:
            return JsonResponse({
                "error": f"Failed to generate script. Error code: {response.status_code} - {response.json()}"
            }, status=response.status_code)

    return JsonResponse({"error": "Invalid request method. Use POST."}, status=400)


@csrf_exempt
def save_script(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt', '').strip()
            script = data.get('script', '').strip()

            if not script:
                return JsonResponse({"error": "Script content is required."}, status=400)

            # Log to ensure it's only being called once
            print("Saving script...")  # Debug message

            Script.objects.create(prompt=prompt, generated_script=script)
            return JsonResponse({"message": "Script saved successfully!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=400)


def saved_scripts(request):
    print("Fetching saved scripts...")  # Debug message

    # Get search query from the request
    search_query = request.GET.get('search', '').strip()

    # Fetch all scripts and apply search filter if a query is provided
    scripts = Script.objects.all().order_by('-created_at')
    if search_query:
        scripts = scripts.filter(
            Q(prompt__icontains=search_query) | Q(
                generated_script__icontains=search_query)
        )

    # Apply pagination
    paginator = Paginator(scripts, 5)  # 5 scripts per page
    page_number = request.GET.get('page', 1)  # Get current page number
    page_obj = paginator.get_page(page_number)

    # Render the template with the paginated and filtered scripts
    return render(request, 'script_generator/saved_scripts.html', {
        'scripts': page_obj,
        'search_query': search_query,  # Pass the search query back to the template
    })


def export_script(request, script_id, file_format):
    script = get_object_or_404(Script, id=script_id)

    if file_format == 'txt':
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="script_{script_id}.txt"'
        response.write(script.generated_script)
        return response

    elif file_format == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="script_{script_id}.pdf"'

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 750, f"Prompt: {script.prompt}")
        p.drawString(100, 730, "Generated Script:")
        text_object = p.beginText(100, 710)
        text_object.setFont("Helvetica", 10)
        for line in script.generated_script.splitlines():
            text_object.textLine(line)
        p.drawText(text_object)
        p.save()

        buffer.seek(0)
        response.write(buffer.getvalue())
        buffer.close()
        return response

    else:
        return JsonResponse({"error": "Invalid file format."}, status=400)


def preview_file_content(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']

        try:
            # Extract text content from the file
            extracted_text = textract.process(
                file.temporary_file_path()).decode('utf-8')
            return JsonResponse({"extracted_text": extracted_text})
        except Exception as e:
            return JsonResponse({"error": f"Failed to extract content: {str(e)}"}, status=400)
    return JsonResponse({"error": "Invalid request. Please upload a file."}, status=400)


def handle_file(file):
    file_ext = os.path.splitext(file.name)[1].lower()
    fs = FileSystemStorage()
    file_path = fs.save(file.name, file)
    file_full_path = fs.path(file_path)

    try:
        if file_ext == '.txt':
            with open(file_full_path, 'r') as f:
                content = f.read()
        elif file_ext == '.pdf':
            content = extract_text(file_full_path)
        elif file_ext in ['.jpg', '.jpeg', '.png']:
            image = Image.open(file_full_path)
            content = pytesseract.image_to_string(image)
        else:
            content = ""

    finally:
        fs.delete(file_path)

    return content


def fetch_link_metadata(link):
    try:
        response = requests.get(link, timeout=5)
        if response.status_code == 200:
            return response.text[:1000]
    except Exception as e:
        return f"Error fetching metadata from {link}: {e}"
    return ""
