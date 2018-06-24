import logging
import os
import csv
import pyrebase
from aybackend.pyreconfig import config

from django.core.exceptions import ValidationError

from aybackend.models import Registration, Event

logger = logging.getLogger(__name__)



def sync_with_firebase():

    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    users = db.child("users").get()
    d = users.val()
    Registration.objects.filter(source='android').delete()
    for userid, info in d.items():
        try:
            for event in info['reg_events']:
                if info['reg_events'][event]:
                    try:
                        related_event = Event.objects.get(id=event)
                    except (ValidationError, Event.DoesNotExist) as e:
                        logger.error("[AmithFirebaseSync] Invalid Event UUID " + event + " was recieved.")
                        continue
                    new = Registration.objects.create(name=info['username'], email=info['email'],
                                                      mob_number="+91" + info['contact'], event=related_event,
                                                      college=info['college'], source='android')
                    new.save()
        except KeyError:
            logger.error("[AmithFirebaseSync] Unfinished user " + userid + " was recieved.")
            continue


def event_sync_firebase():
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    sdata = {}
    evcrdlist = {}
    for event in Event.objects.all():
        coordlist  = [x.strip() for x in str(event.coord_id).split(',')]
        for coord in coordlist:
            if coord:
                evcrdlist[coord] = str(event.id)
        evname = str(event.name).replace("(","\n(")
        data = {'name': evname,'timestamp': event.when.timestamp(),'tags': str(event.tags), 'when_date': event.when.strftime("%B %d"), 'when_time': event.when.strftime("%I:%M %p"),
                'when_time_end': event.when_end.strftime("%I:%M %p"), 'venue': str(event.venue), 'desc': str(event.desc),
                'rules': str(event.rules), 'is_team': event.is_team, 'image': str(event.image), 'type': str(event.type), 'prize_amt': event.prize_amt,
                'prize_amt_sec': event.sec_prize_amt,
                'reg_cost': event.reg_cost, 'primary_coord_name': str(event.primary_coord_name), 'primary_coord_contact' : str(event.primary_coord_contact),
                'secondary_coord_name': str(event.secondary_coord_name), 'secondary_coord_contact': str(event.secondary_coord_contact),
                'is_flagship': event.is_flagship
                }
        sdata[str(event.id)]=data
        if event.has_alt_time:
            datam = data.copy()
            datam['when_date'] = event.alter_time.strftime("%B %d")
            datam['when_time'] = event.alter_time.strftime("%I:%M %p")
            datam['when_time_end'] = event.alter_end_time.strftime("%I:%M %p")
            datam['timestamp'] = event.alter_time.timestamp()
            sdata["dupe-"+str(event.id)] = datam

    db.child('events').set(sdata)
    db.child('event_coordinators').set(evcrdlist)



def getUserID(email):
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    m =db.child("users").order_by_child("email").equal_to(email).get().val()
    return next(iter(m.keys()))



def getUserIDfromCSV(file):



    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    mdct = []

    with open(file, 'r') as csvinput:
        with open('output.csv', 'w') as csvoutput:
            writer = csv.writer(csvoutput, lineterminator='\n')
            reader = csv.reader(csvinput)

            all = []
            row = next(reader)
            row.append('UID')
            all.append(row)

            for row in reader:
                try:
                    row.append(next(iter(db.child("users").order_by_child("email").equal_to(row[1]).get().val())))
                    all.append(row)
                except IndexError:
                    print("Unregistered User", row[1])
            writer.writerows(all)


    # with open(file) as csvfile:
    #     reader = csv.DictReader(csvfile)
    #
    #     for row in reader:
    #         try:
    #             dct = {row['Email address'],next(iter(db.child("users").order_by_child("email").equal_to(row['Email address']).get().val())) }
    #             mdct.append(dct)
    #         except IndexError:
    #             print("Unregistered User",row['Email address'])
    # return mdct


