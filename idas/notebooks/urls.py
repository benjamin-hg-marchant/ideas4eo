
from django.conf.urls import url

from . import views

urlpatterns = [

url(r'^$', views.home_view, name='home_view'),

url(r'^SignUp/$', views.signup_view, name='signup_view'), 
url(r'^Log-out/$', views.logout_view, name='logout_view'),

url(r'^Notebooks/$', views.notebooks_view, name='notebooks_view'), 
url(r'^Notebooks/(?P<notebook_url>[\w.@+-]+)/$', views.notebook_home_view, name='notebook_home_view'),
url(r'^Notebooks/(?P<notebook_url>[\w.@+-]+)/Images/$', views.notebook_images_view, name='notebook_images_view'), 

url(r'^Articles/$', views.note_search_view, name='note_search_view'), 
url(r'^Articles/Create/$', views.article_create_view, name='article_create_view'), 	 
url(r'^Articles/(?P<note_url>[\w.@+-]+)/$', views.article_view, name='article_view'),
url(r'^Articles/(?P<note_url>[\w.@+-]+)/Edit/$', views.article_edit_view, name='article_edit_view'),
url(r'^Articles/(?P<note_url>[\w.@+-]+)/Images/$', views.article_images_view, name='article_images_view'),

url(r'^Images/$', views.note_search_view, name='note_search_view'),
url(r'^Images/(?P<note_url>[\w.@+-]+)/$', views.image_view, name='image_view'),
 
url(r'^Recipes/$', views.note_search_view, name='note_search_view'), 
url(r'^Addresses/$', views.note_search_view, name='note_search_view'),

]