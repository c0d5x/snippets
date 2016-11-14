

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




