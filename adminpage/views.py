from django.shortcuts import render, redirect
from .models import Request, Plan, SelectedTheme, UploadedTheme
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse
from django.core.files.storage import FileSystemStorage
import json

@csrf_exempt
def request(request):
    if request.method == 'POST':
        #변수 받아오기
        floor_type = request.POST.get('floor_type')
        commercial_type = request.POST.get('commercial_type')
        floor_number = request.POST.get('floor_number')
        floor_size = request.POST.get('floor_size')
        floor_size_unit = request.POST.get('floor_size_unit')
        floor_height = request.POST.get('floor_height')
        floor_height_unit = request.POST.get('floor_height_unit')
        floor_address = request.POST.get('floor_address')
        add_request = request.POST.get('add_req')

        newRequest = Request.objects.create(
            floor_type = floor_type,
            commercial_type = commercial_type,
            floor_number = floor_number,
            floor_size = floor_size,
            floor_size_unit = floor_size_unit,
            floor_height = floor_height,
            floor_height_unit = floor_height_unit, 
            floor_address = floor_address,
            add_request = add_request
        )

        #file 처리 
        for afile in request.FILES.getlist('floor_plan'):
            files = Plan()
            files.photo = afile
            files.save()
            newRequest.floor_plan.add(files)
            newRequest.save()

        for afile in request.FILES.getlist('uploaded_theme'):
            files = UploadedTheme()
            files.photo = afile
            files.save()
            newRequest.uploaded_theme.add(files)
            newRequest.save()

        for afile in request.POST.getlist('selected_theme'):
            themes = SelectedTheme()
            newfile = str(afile.split(".")[0]) + ".jpg"
            themes.option = newfile
            themes.save()
            newRequest.selected_theme.add(themes)
            newRequest.save()
        
        return HttpResponse(status=200)
    else:
        return HttpResponseNotAllowed(['POST'])

def dashboard(request):
    if request.method == 'GET':
        #labels = []
        #data = []
        requests = Request.objects.all()
        queryset = Request.objects.order_by('-progress')[:]
        progress = [0,0,0,0,0]
        for user in queryset:
            for i in range(5):
                if(user.progress == i+1):
                    progress[i] += 1

        labels = ["progress_1", "progress_2", "progress_3", "progress_4", "progress_5"]
        data = progress.copy()

        return render(request, 'adminpage/dashboard.html', {
            'requests': requests,
            'labels': labels,
            'data': data,
        })


def show(request):

    if request.method == 'GET':
        onrunRequests = Request.objects.exclude(progress = 5) #on run: filter (step 5 이하, step 5이면 제외)
        totalRequests = Request.objects.all()
        return render(request, 'adminpage/show.html', {'totalRequests': totalRequests, 'onrunRequests': onrunRequests})



def each(request, id):

    # 보여주기
    if request.method == 'GET':

        arequest= Request.objects.get(id = id)
        return render(request, 'adminpage/request.html', {'arequest': arequest})
    

    # 수정하기
    elif request.method == 'POST':

        arequest= Request.objects.get(id = id)


        due_at = request.POST.get('due_at', arequest.due_at)
        progress = request.POST.get('progress', arequest.progress)
        floor_type = request.POST.get('floor_type', arequest.floor_type)
        commercial_type = request.POST.get('commercial_type', arequest.commercial_type)
        floor_number = request.POST.get('floor_number', arequest.floor_number)
        floor_size = request.POST.get('floor_size', arequest.floor_size)
        floor_size_unit = request.POST.get('floor_size_unit', arequest.floor_size_unit)
        floor_height = request.POST.get('floor_height', arequest.floor_height)
        floor_height_unit = request.POST.get('floor_height_unit', arequest.floor_height_unit)
        floor_address = request.POST.get('floor_address', arequest.floor_address)
        add_request = request.POST.get('add_request', arequest.add_request)

        
        arequest.due_at = due_at
        arequest.progress = progress
        arequest.floor_type = floor_type
        arequest.commercial_type = commercial_type
        arequest.floor_number = floor_number
        arequest.floor_size = floor_size
        arequest.floor_size_unit = floor_size_unit
        arequest.floor_height = floor_height
        arequest.floor_height_unit = floor_height_unit
        arequest.floor_address = floor_address
        arequest.add_request = add_request

        arequest.save()
        arequest.update_date()

        return redirect('/'+str(id))

def edit(request, id):

    arequest = Request.objects.get(id=id)
    return render(request, 'adminpage/edit.html', {'arequest':arequest})

def download(request, req_id, file_id):

    arequest= Request.objects.get(id = req_id)
    afile = arequest.floor_plan.get(id = file_id)
    fs = FileSystemStorage('../On-Demand-Back/media')
    response = FileResponse(fs.open(str(afile.photo), 'rb'), content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename= floorplan.png'
    
    return response