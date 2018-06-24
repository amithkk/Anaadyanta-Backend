import uuid
import pytz
from io import BytesIO
import datetime
import sys
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from shortuuidfield import ShortUUIDField

class Event(models.Model):
    id = ShortUUIDField(editable=False, primary_key=True)
    avail_types = (("CUL","Cultural"), ("TECH","Technical"))
    name = models.CharField(max_length=50, verbose_name="Event Name")
    when = models.DateTimeField(verbose_name="Event Date/Time", default=datetime.datetime(2018,3,8,tzinfo=pytz.timezone('Asia/Kolkata')))
    when_end = models.DateTimeField(verbose_name="Event End Date/Time", default=datetime.datetime(2018,3,8,tzinfo=pytz.timezone('Asia/Kolkata')))
    venue = models.CharField(max_length=20,verbose_name="Event Venue", default="TBD")
    tags = models.CharField(max_length=50, verbose_name="Event Tags (Separate By Comma)",null=True, blank=True)
    desc = models.TextField()
    rules = models.TextField(default="To Be Decided")
    is_team = models.BooleanField()
    image = models.ImageField(upload_to='events/',verbose_name="Event Image")
    type = models.CharField(choices=avail_types, max_length=10, default="TECH", verbose_name="Event Category")
    prize_amt = models.IntegerField(verbose_name="Prize Amount")
    sec_prize_amt = models.IntegerField(verbose_name="Second Prize Amount", null=True, blank=True)
    reg_cost = models.IntegerField(verbose_name="Registration Cost")
    primary_coord_name = models.CharField(verbose_name="Primary Coordinator Name", max_length=30, null=True)
    primary_coord_contact = PhoneNumberField(verbose_name="Primary Coordinator Number", null=True, default="+91")
    secondary_coord_name = models.CharField(verbose_name="Secondary Coordinator Name", max_length=30, null=True, blank=True)
    secondary_coord_contact = PhoneNumberField(verbose_name="Secondary Coordinator Number", null=True, blank=True, default="+91")
    is_flagship = models.BooleanField(default=False)
    coord_id = models.TextField(verbose_name="Firebase UID For Coordinator", default="", null=True, blank=True)
    has_alt_time = models.BooleanField(default=False)
    alter_time = models.DateTimeField(verbose_name="Event Date/Time",
                                default=datetime.datetime(2018, 3, 8))
    alter_end_time = models.DateTimeField(verbose_name="Event End Date/Time",
                                    default=datetime.datetime(2018, 3, 8))


    def __str__(self):
        return self.name

    def save(self, **kwargs):
        # Opening the uploaded image
        im = Image.open(self.image)

        output = BytesIO()

        size = 640, 640

        # Resize/modify the image

        im.thumbnail(size, Image.ANTIALIAS)

        # after modifications, save it to the output
        im.save(output, format='JPEG', quality=100)
        output.seek(0)

        # change the imagefield value to be the newley modifed image value
        self.image = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.image.name.split('.')[0], 'image/jpeg',
                                        sys.getsizeof(output), None)

        super(Event, self).save(**kwargs)

class Registration(models.Model):
    name = models.CharField(verbose_name="Participant Name", max_length=50)
    email = models.EmailField(verbose_name="Participant Email")
    college = models.CharField(verbose_name="College Name", max_length=50)
    mob_number = PhoneNumberField(verbose_name="Participant Number")
    event = models.ForeignKey(Event, on_delete=models.CASCADE,verbose_name="Event")
    source = models.CharField(verbose_name="Registration Source",max_length=10,choices=(("web","web"),("android","android")))
    time_registered = models.DateField(auto_now_add=True, verbose_name="Registration Time")

    def has_add_permission(self, request):
        return False

    def __str__(self):
        return self.name+"-"+self.event.name




