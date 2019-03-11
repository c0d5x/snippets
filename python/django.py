

# create project
django-admin startproject <proj-name>
cd <proj-name>

# create app
python manage.py startapp <app-name>

# edit settings.py, adding the app
vim <proj-name>/settings.py
    /INSTALLED_APPS
    add <app-name>

# edit the model, views, etc...
vim <app-name>/models.py
# https://docs.djangoproject.com/en/1.10/topics/db/models/

# Make migrations for the first time
python manage.py makemigrations

# sync the DB
python manage.py migrate

# create super user
python manage.py createsuperuser
    username
    email
    passwd

# edit admin.py
vim <app-name>/admin.py
    from .models import Model1, model2, etc..
    admin.site.register(Model1)
    admin.site.register(model2)


# add URL routes to views or controllers
vim <proj-name>/urls.py
    add if not present:
        from django.conf.urls import include
    /urlpatterns
        add routes with regex:
            url(r'^polls/', include('polls.urls')),
                                    ^ urls.py in polls directory
#For <app-name>/urls.py add:
from django.conf.urls import url
from . import views  # or controllers,
                ^ views.py in current dir (app-name)

# https://docs.djangoproject.com/en/1.10/topics/http/urls/
urlpatterns = [
      url(r'^$', views.index, name="index"),
      #      ^ this adds to '^polls/' defined previously
      url(r'^list', views.list, name="list"),
             ^ -> '/polls/list', file views.py method list
      url(r'^question/(?P<question_id>[0-9]{4})/$', views.show_question, name="show_question"),
             ^ -> '/polls/question/1234', file views.py method show_question
      url(r'^question/(?P<question_id>[0-9]+)/$', views.show_question, name="show_question"),
             ^ -> '/polls/question/1234567', file views.py method show_question
      url(r'^question/(?P<question_id>\d+)/$', views.show_question, name="show_question"),
             ^ -> '/polls/question/1234567', file views.py method show_question
      ]

# for a view or controller
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello World!")

def show_question(question_id):
    return HttpResponse("Hello World! for q {}".format(question_id))


# django model data types
https://docs.djangoproject.com/en/2.1/ref/models/fields/
AutoField
BinaryField
BooleanField
CharField
DateField
DateTimeField
DecimalField
DurationField
EmailField
FileField
FilePathField
FloatField
ImageField
IntegerField
GenericIPAddressField
PositiveIntegerField
SmallIntegerField
TextField
URLField
UUIDField

# field options
null
blank
choices
db_column
db_index
db_tablespace
default
editable
error_messages
help_text
primary_key
unique
unique_for_date
unique_for_month
unique_for_year
verbose_name
validators

# relationship fields
ForeignKey
ManyToManyField
OneToOneField


# django model examples
from datetime import date
from django.utils import timezone


class Person(models.Model):
    # Default (blank=False,null=False)
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, unique=True)
    state = models.CharField(max_length=2, default='CA')
    datetime = models.DateTimeField(default=timezone.now)
    date_lastupdated = models.DateField(auto_now=True)
    date_added = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ("name", "email")
        ordering = ['-last_name']
        indexes = [
            models.Index(fields=['city', 'state']),
            models.Index(fields=['city'], name='city_idx')
        ]



class Menu(models.Model):
    name = models.CharField(max_length=30)


ITEM_SIZES = (('S', 'Small'), ('M', 'Medium'), ('L', 'Large'), ('P', 'Portion'),)
class Item(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100,
                                   help_text="""Ensure you provide some description of the ingredients""")
    size = models.CharField(choices=ITEM_SIZES, max_length=1)


# Import built-in validator
from  django.core.validators import MinLengthValidator

# Create custom validator
from django.core.exceptions import ValidationError


def calorie_watcher(value):
    if value > 5000:
        raise ValidationError(
            ('Whoa! calories are %(value)s ? We try to serve healthy food, try something less than 5000!'),
            params={'value': value},
        )
    if value < 0:
        raise ValidationError(
            ('Strange calories are %(value)s ? This can\'t be, value must be greater than 0'),
            params={'value': value},
        )


class X(models.Model):
    calories = models.IntegerField(validators=[calorie_watcher])

