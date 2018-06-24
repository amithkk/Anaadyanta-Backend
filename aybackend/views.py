import json
import _thread
from json.decoder import JSONDecodeError

import sys

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render

# Create your views here.
from aybackend.admin import RegistrationExporterResource
from aybackend.models import Event, Registration
from aybackend.tasks import sync_with_firebase, event_sync_firebase


def eventlist_view(request):
    return render(request, 'eventview.html')


@csrf_exempt
def get_events(request):
    # data = json.loads(str(request.body))
    event_queryset = Event.objects.annotate(registration_number=Count('registration')).all()
    return HttpResponse(json.dumps(list(event_queryset.values()), cls=DjangoJSONEncoder),
                        content_type="application/json")


@csrf_exempt
def do_registration(request):

    try:
        registration_data = json.loads(request.body.decode('utf-8'))

        if Registration.objects.filter(email=registration_data['email'],
                                       event=Event.objects.get(id=registration_data['eventid'])).exists():
            return JsonResponse({"result": "fail", "error": "Email already registered with event"})
        new = Registration.objects.create(name=registration_data['name'],
                                          email=registration_data['email'],
                                          mob_number=registration_data['mob_number'],
                                          event=Event.objects.get(id=registration_data['eventid']))
        new.full_clean()

    except KeyError:
        new.delete()
        return JsonResponse({"result": "fail", "error": "Invalid Keys"})
    except JSONDecodeError:
        new.delete()
        return JsonResponse({"result": "fail", "error": "Invalid JSON Body"})
    except ValidationError:
        new.delete()
        return JsonResponse({"result": "fail", "error": "ValidationError - Invalid mob_number or email"})
    else:
        new.save()
        return JsonResponse({"result": "success"})

@staff_member_required
def export_xslx(request):
    exported = RegistrationExporterResource().export().xlsx
    response = HttpResponse(exported, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename = "export_ayframework.xlsx"'
    return response


@staff_member_required
def do_firebase_sync(request):
    _thread.start_new_thread(sync_with_firebase, ())
    return render(request, 'firebasesync.html')


@user_passes_test(lambda u: u.is_superuser)
def do_event_fb_sync(request):
    _thread.start_new_thread(event_sync_firebase, ())
    return render(request, 'firebasesync.html')

