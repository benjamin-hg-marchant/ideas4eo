from django.conf import settings

from .models import Notebook

#----------------------------------------------------------------------------------------#

def navbar(request):
	debug_flag = settings.DEBUG
	#----- context -----#
	context_noteook_url = ''
	if request.user.is_authenticated:
		notebooks_obj = Notebook.objects.get(user=request.user.id) 
		context_noteook_url = notebooks_obj.url
	#----- session language -----#
	language = 'en'
	if 'language' in request.session: 
		language = request.session['language']
	#----- english -----#
	if language == 'en':
		navbar_courses = 'Courses'
		navbar_research = 'Research'
		navbar_tutorials = 'Tutorials'
		navbar_sign_up = 'Sign-Up'
		navbar_search_input_txt = 'key words...'
		navbar_search_button = 'Search'
	#----- fr -----#
	if language == 'fr':
		navbar_courses = 'Cours'
		navbar_research = 'Recherche'
		navbar_tutorials = 'Tutoriels'
		navbar_sign_up = 'Inscription'
		navbar_search_input_txt = 'mots-clés...'
		navbar_search_button = 'Chercher'
	#----- return -----#	
	return{
	"debug_flag":debug_flag,
	"context_noteook_url":context_noteook_url,
	"navbar_courses":navbar_courses,
	"navbar_research":navbar_research,
	"navbar_tutorials":navbar_tutorials,
	'navbar_sign_up':navbar_sign_up,
	"navbar_search_input_txt":navbar_search_input_txt,
	"navbar_search_button":navbar_search_button}		
	



