
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.conf import settings

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password, make_password

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Notebook
from .models import Notebook_Note
from .models import Notebook_Stats
from .models import Article
from .models import Image
from .models import Note
from .models import Note_Link

from .models import UserCreateForm
from .models import Article_Create_Form
from .models import Article_Edit_Form
from .models import Image_Upload_Form
from .models import Note_Remove_Form
from .models import Link_Form
from .models import Note_Search_Form

from . import apps_functions as fc

import os
import urllib, hashlib
import datetime

#----------------------------------------------------------------------------------------#

def home_view(request):
	note_obj_list = Note.objects.filter(note_type='article').order_by('-date_created')
	#----- language selection -----#
	language = 'en'
	template_title = 'Intelligent Data Exploration and Analysis Systems'
	template_name = "notebooks/welcome_fr.html"
	header_h1_text = '' 
	header_h2_text = ""
	header_img_url = '/static/notebooks/photos/earth-1990298.jpg'
	header_navbar_01_button = []
	header_navbar_02_button = []
	#header_navbar_01_button.append((True,False,'/?language=fr','<span class="flag-icon flag-icon-fr"> </span> French '))
	#header_navbar_01_button.append((True,False,'/?language=en','<span class="flag-icon flag-icon-us"></span> English'))
	if 'language' in request.GET and request.GET['language']:
		language = request.GET['language']
		if language == 'fr': 
			request.session['language'] = 'fr'
			template_name = "notebooks/welcome_fr.html"
			note_obj_list = Note.objects.filter(note_type='article',language='fr').order_by('-date_created')
		if language == 'en': 
			request.session['language'] = 'en'
			note_obj_list = Note.objects.filter(note_type='article',language='en').order_by('-date_created')
	else:
		if 'language' in request.session: 
			language = request.session['language']
			if language == 'fr':
				template_name = "notebooks/welcome_fr.html"
				note_obj_list = Note.objects.filter(note_type='article',language='fr').order_by('-date_created')
			if language == 'en':
				template_name = "notebooks/welcome_fr.html"		
				note_obj_list = Note.objects.filter(note_type='article',language='en').order_by('-date_created')		
	#----- language translation -----#	
	if language == 'fr': 
		text_dic = {}
		text_dic['posted_on'] = 'Ajouté le'	
		text_dic['by'] = 'par'	
		text_dic['read_more'] = 'Lire la suite'	
		text_dic['keywords'] = 'mots clés ...'	
		text_dic['search'] = 'Chercher'
		text_dic['reset'] = 'Réinitialiser'
		text_dic['add_button'] = 'Ajouter un article'	
	if language == 'en': 
		text_dic = {}
		text_dic['posted_on'] = 'Posted on'	
		text_dic['by'] = 'by'	
		text_dic['read_more'] = 'Read More'
		text_dic['keywords'] = 'keywords ...'	
		text_dic['search'] = 'Search'
		text_dic['reset'] = 'Reset'	
		text_dic['add_button'] = 'Add an article'	
	#----- form -----#
	form = Note_Search_Form() 
	if request.method == 'POST':		
		if 'Auth_Form' in request.POST:
			if request.user.is_authenticated:
				msg = 'Oops! your are already authenticated'	
				messages.add_message(request, messages.INFO, msg)		
			else:		
				username = request.POST['username']  
				password = request.POST['password'] 
				user = authenticate(username=username, password=password)
				if user is not None:
					if user.is_active:
						login(request, user)
						corresp_id = User.objects.get( username = username ).pk
						user_notebook_obj = Notebook.objects.get( pk = corresp_id )
						return HttpResponseRedirect("/Notebooks/"+user_notebook_obj.url+"/")
					else:
						messages.add_message(request, messages.INFO, "This account is currently not active !")
				else:
					messages.add_message(request, messages.INFO, 'Sorry, the username and/or password are incorrect  !')
		if 'start_search' in request.POST: 
			form = Note_Search_Form(request.POST) 
			if form.is_valid():
				note_keywords = request.POST['note_keywords']
				request.session['note_search_page'] = request.path
				request.session['note_search_keywords'] = note_keywords
				return HttpResponseRedirect(request.path)						
		if 'reset_search' in request.POST:
			request.session['note_search_page'] = ''
			request.session['note_search_keywords'] = ''
	if 'note_search_page' in request.session:
		if request.path == request.session['note_search_page']:								
			note_keywords = request.session['note_search_keywords']
			#----- form -----#
			form_dict = {}
			form_dict['note_keywords'] = note_keywords
			form = Note_Search_Form(initial=form_dict)
			#----- note keywords -----#
			note_keywords_list = note_keywords.split()
			for note_keywords in note_keywords_list:
				note_obj_list = note_obj_list.filter( keywords_machine__icontains = note_keywords )
	#----- paginator -----#
	paginator = Paginator(note_obj_list, 50)
	page = request.GET.get('page')
	try:
		PagList = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		PagList = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		PagList = paginator.page(paginator.num_pages)
	adjacent_pages=2
	startPage = max(PagList.number - adjacent_pages, 1)
	if startPage <= 3: startPage = 1
	endPage = PagList.number + adjacent_pages + 1
	page_numbers = [n for n in range(startPage, endPage) if n > 0 and n <= paginator.num_pages]	
	#----- render template -----#
	context = {
	'language':language,
	'text_dic':text_dic,
	'template_title':template_title,
	'header_h1_text':header_h1_text,
	'header_h2_text':header_h2_text,
	'header_img_url':header_img_url,
	'header_navbar_01_button':header_navbar_01_button,
	'header_navbar_02_button':header_navbar_02_button,	
	'form':form,
	'PagList': PagList, 
	'paginator': paginator, 
	'page_numbers':page_numbers,
	'startPage':startPage,
	'endPage':endPage,
	'show_first': 1 not in page_numbers,
	'show_last': paginator.num_pages not in page_numbers}	
	return render(request, "notebooks/welcome_fr.html", context)	

#----------------------------------------------------------------------------------------#

def signup_view(request):
	#----- session language -----#
	language = 'en'
	template_name = "notebooks/signup_en.html"
	header_h1_text = "So you want to become a bee <br> and join the community !" 
	header_h2_text = "<br> It is simple just fill the following form"

	#----- template variables -----#
	title = 'Sign-Up'
	header_img_url = '/static/notebooks/photos/eiffel-tower-951509_1920.jpg'
	header_button_01 = True
	header_button_01_url = '/Notes/'
	header_button_01_txt = 'Contact us'	
	#----- redirect authenticated user -----#
	if request.user.is_authenticated:
		notebooj_obj = Notebook.objects.get(user=request.user)
		msg = 'Oops! your are already authenticated'	
		messages.add_message(request, messages.INFO, msg)
		return HttpResponseRedirect("/")		
	#----- sign-up form
	SignUp_form = UserCreateForm()
	form_part = 'part1'
	form_part1_valid = False
	if request.method == 'POST':
		if 'SignUp_Form' in request.POST: 
			SignUp_form = UserCreateForm(request.POST)
			if SignUp_form.is_valid():
				username = request.POST['username']
				password = request.POST['password1']
				form_part = request.POST['form_part']
				if not User.objects.filter(username=username).exists():
					form_part1_valid = True
					if form_part1_valid and form_part == 'part2':
						security_question_1 = request.POST['security_question_1']	
						security_question_2 = request.POST['security_question_2']	
						security_question_3 = request.POST['security_question_3']	
						security_answer_1 = request.POST['security_answer_1']
						security_answer_2 = request.POST['security_answer_2']
						security_answer_3 = request.POST['security_answer_3']
						security_answer_1 = security_answer_1.lower()
						security_answer_2 = security_answer_2.lower()
						security_answer_3 = security_answer_3.lower()				
						security_questions = True
						if not security_answer_1: security_questions = False
						if not security_answer_2: security_questions = False
						if not security_answer_3: security_questions = False
						if security_questions:
							SignUp_form.save()	
							notebook_id = User.objects.get(username=username).pk
							user_obj = User.objects.get(pk=notebook_id)
							url = hashlib.md5(str(notebook_id).encode('utf-8')).hexdigest()
							#----- create user folder -----#
							path_to_media = settings.MEDIA_ROOT
							os.system('mkdir -m 777 '+path_to_media+'users/'+ url )
							os.system('mkdir -m 777 '+path_to_media+'users/'+ url + '/uploaded_files' )
							#----- create notebook -----#							
							new_notebook = Notebook(				
							user = user_obj,
							url = url,
							date_created = datetime.datetime.now(), 	
							account_active = True,
							account_blocked = False,
							last_activity_date = datetime.datetime.now(), 
							profile_picture = False,
							header_img = False,
							display_full_name = False,
							display_about_button = False,
							full_name = '',
							middle_name = '',
							content = '',
							content_formatted = '',
							abstract = '',
							abstract_formatted = '',
							content_fr = '',
							content_fr_formatted = '',
							abstract_fr = '',
							abstract_fr_formatted = '',
							security_questions = security_questions,
							security_question_1_idx = security_question_1,
							security_question_1 = make_password(security_answer_1), 
							security_question_2_idx = security_question_2,
							security_question_2 = make_password(security_answer_2),
							security_question_3_idx = security_question_3,
							security_question_3 = make_password(security_answer_3),    
							key_words = '',
							key_words_machine = '',
							removed = False) 
							new_notebook.save()
							notebook_obj = Notebook.objects.get(url = url)
							#----- create notebook stats -----#
							new_notebook_stats =  Notebook_Stats(
							notebook = notebook_obj,
							notes_count = 0,
							article_count = 0,
							image_count = 0,
							file_count = 0,
							code_count = 0,
							visitor_weekly_count = 0,
							removed = False) 
							new_notebook_stats.save()
							#----- user login -----#
							user = authenticate(username=username, password=password)
							login(request, user)
							messages.add_message(request, messages.INFO, "Welcome " + username + u" / Bienvenue " + username)
							return HttpResponseRedirect("/Notebooks/"+url+"/")
					#----- part2 -----#
					if form_part == 'part1':
						form_part = 'part2'
				else:
					msg = 'Sorry, username "'+username+'" is already taken !'	
					messages.add_message(request, messages.INFO, msg)	
			else:
				form_errors = SignUp_form.errors
				messages.add_message(request, messages.INFO, u"Sorry form is not valid ! ..." + '<br>' + str(form_errors) )
	#----- template render -----#
	context = {
	'title':title,
	'SignUp_form':SignUp_form,
	'header_h1_text':header_h1_text,
	'header_h2_text':header_h2_text,
	'header_img_url':header_img_url,
	'header_button_01':header_button_01,
	'header_button_01_url':header_button_01_url,
	'header_button_01_txt':header_button_01_txt,
	'form_part1_valid':form_part1_valid,
	'form_part':form_part}
	return render(request, template_name, context )

#----------------------------------------------------------------------------------------#

def signin_view(request):
	title = 'Sign-In'
	header_h1_text = "Welcome back to the hive ! <br> blblblbl" 
	header_h2_text = "<br> It is time to make honey from the nectar... "
	header_img_url = '/static/notebooks/photos/lavender-1537694_1920_greyscale.png'
	#----- redirect authenticated user -----#
	if request.user.is_authenticated:
		notebooj_obj = Notebook.objects.get(user=request.user)
		return HttpResponseRedirect("/")	
	#----- sign in form -----#
	if request.method == 'POST':
		username = request.POST['username']  
		password = request.POST['password'] 
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				corresp_id = User.objects.get( username = username ).pk
				user_notebook_obj = Notebook.objects.get( pk = corresp_id )
				return HttpResponseRedirect("/")
			else:
				messages.add_message(request, messages.INFO, "This account is currently not active !")
		else:
			messages.add_message(request, messages.INFO, 'Sorry, the username and/or password are incorrect  !')
	context = {
	'title':title,
	'header_h1_text':header_h1_text,
	'header_h2_text':header_h2_text,
	'header_img_url':header_img_url}
	return render(request, "notebooks/sign_in.html", context )

#----------------------------------------------------------------------------------------#

def logout_view(request):
	if request.user.is_authenticated:
		notebook_obj = Notebook.objects.get(user=request.user)    
		logout(request)
		messages.add_message(request, messages.INFO, u'See you soon ' + str(notebook_obj.user.first_name) + u' !')
		return HttpResponseRedirect('/')	
	else:
		raise Http404   

#----------------------------------------------------------------------------------------#

def notebooks_view(request):
	template_nb_element_displayed = 1000
	template_title = 'Open Science Notebooks'
	header_h1_text = '<br> Open Science Notebooks' 
	header_h2_text = ""
	header_img_url = '/static/notebooks/photos/eiffel-tower-951509_1920.jpg'
	header_navbar_01_button = []
	header_navbar_02_button = []
	#header_navbar_01_button.append((True,True,'/Notebooks/','Notebooks'))
	#header_navbar_01_button.append((True,False,'/Groups/','Groups'))
	#----- notebooks filter -----#	
	notebook_stats_obj_list = Notebook_Stats.objects.filter(removed=False).order_by('-notes_count')	
	template_heading = 'Ant population: '
	template_subheading = notebook_stats_obj_list.count
	#----- paginator -----#
	paginator = Paginator(notebook_stats_obj_list, template_nb_element_displayed)
	page = request.GET.get('page')
	try:
		PagList = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		PagList = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		PagList = paginator.page(paginator.num_pages)
	adjacent_pages=2
	startPage = max(PagList.number - adjacent_pages, 1)
	if startPage <= 3: startPage = 1
	endPage = PagList.number + adjacent_pages + 1
	page_numbers = [n for n in range(startPage, endPage) if n > 0 and n <= paginator.num_pages]	
	#----- render template -----#
	context = {
	'template_title':template_title,
	'header_h1_text':header_h1_text,
	'header_h2_text':header_h2_text,
	'header_img_url':header_img_url,
	'header_navbar_01_button':header_navbar_01_button,
	'header_navbar_02_button':header_navbar_02_button,	
	'template_heading':template_heading,
	'template_subheading':template_subheading,
	'PagList': PagList, 
	'paginator': paginator, 
	'page_numbers':page_numbers,
	'startPage':startPage,
	'endPage':endPage,
	'show_first': 1 not in page_numbers,
	'show_last': paginator.num_pages not in page_numbers}	
	return render(request, "notebooks/notebooks.html", context )	

#----------------------------------------------------------------------------------------#

def notebook_home_view(request,notebook_url):
	language = 'fr'
	if Notebook.objects.filter(url=notebook_url).exists():  
		notebook_obj = Notebook.objects.get(url=notebook_url)
		#----- check user status -----#
		is_owner = False
		is_follower = False
		if request.user.is_authenticated:
			if request.user.id == notebook_obj.user.id: 
				is_owner = True				
		else:
			if 'q1' in request.GET and request.GET['q1']:	
				msg = 'Oops! you need to be <a href="/Sign-in/">logged in</a> to start following a notebook'	
				messages.add_message(request, messages.INFO, msg)
		#----- get notebook notes -----#
		if is_owner:
			notebook_note_obj_list = Notebook_Note.objects.filter(notebook=notebook_obj, note__note_type__in = ['article', 'image'],note__removed=False).order_by('-note__date_created')				
		else:
			notebook_note_obj_list = Notebook_Note.objects.filter(notebook=notebook_obj, note__note_type__in = ['article', 'image'],note__public=True,note__removed=False).order_by('-note__date_created')
		#----- search -----#
		form = Note_Search_Form()
		if request.method == 'POST':
			if 'start_search' in request.POST: 
				form = Note_Search_Form(request.POST) 
				if form.is_valid():
					note_keywords = request.POST['note_keywords']
					note_type = request.POST['note_type']
					if is_owner: note_can_see = request.POST['note_can_see']					
					request.session['note_search_page'] = request.path
					request.session['note_search_keywords'] = note_keywords
					request.session['note_search_type'] = note_type
					if is_owner: 
						if 'note_search_can_see' in request.session: 
							request.session['note_search_can_see'] = note_can_see
					return HttpResponseRedirect(request.path)						
			if 'reset_search' in request.POST:
				request.session['note_search_page'] = ''
				request.session['note_search_keywords'] = ''
				request.session['note_search_type'] = ''
				if is_owner: request.session['note_search_can_see'] = ''
		else:
			if 'note_search_page' in request.session:
				if request.path == request.session['note_search_page']:								
					note_keywords = request.session['note_search_keywords']
					note_type = request.session['note_search_type']
					if is_owner: 
						if 'note_search_can_see' in request.session:
							note_can_see = request.session['note_search_can_see']
					#----- form -----#
					form_dict = {}
					form_dict['note_keywords'] = note_keywords
					form_dict['note_type'] = note_type
					if is_owner: 
						if 'note_search_can_see' in request.session: 
							form_dict['note_can_see'] = int(note_can_see)
					form = Note_Search_Form(initial=form_dict)
					#----- note keywords -----#
					note_keywords_list = note_keywords.split()
					for note_keywords in note_keywords_list:
						notebook_note_obj_list = notebook_note_obj_list.filter(note__keywords_machine__icontains=note_keywords)
					#----- note type -----#
					if not note_type == 'note':
						notebook_note_obj_list = notebook_note_obj_list.filter(note__note_type=note_type)					
					#----- note permissions -----#
					if is_owner: 
						if 'note_search_can_see' in request.session: 
							if int(note_can_see) == 1:
								notebook_note_obj_list = notebook_note_obj_list.filter(note__public=False).order_by('-note__date_created')	
							if int(note_can_see) == 2:
								notebook_note_obj_list = notebook_note_obj_list.filter(note__public=True).order_by('-note__date_created')
		#----- template variables -----#		
		template_nb_element_displayed = 25
		template_note_count = notebook_note_obj_list.count()
		header_h2_text = ""
		if notebook_obj.display_full_name:
			template_title = notebook_obj.full_name + "'s Notebook"
			header_h1_text = notebook_obj.full_name + "'s Notebook"
		else:
			template_title = notebook_obj.user.username + "'s Notebook"
			header_h1_text = notebook_obj.user.username + "'s Notebook"
		if notebook_obj.header_img:
			header_img_url = '/media/users/' + notebook_obj.url + '/header_image_1000_1000.png'
		else:
			header_img_url = '/static/notebooks/photos/eiffel-tower-951509_1920.jpg'		
		header_navbar_01_button = []
		header_navbar_02_button = []		
		if is_owner:
			header_navbar_01_button.append((True,True,'/Notebooks/'+notebook_obj.url+'/','<i class="fa fa-home"></i> Home'))
			header_navbar_01_button.append((True,False,'/Notebooks/'+notebook_obj.url+'/Images/','<i class="fa fa-picture-o"></i> Photos'))		
		else:
			if notebook_obj.nb_public_photos == 0:
				header_h1_text = '<br><br>' + header_h1_text
				#header_navbar_01_button.append((True,True,'/Notebooks/'+notebook_obj.url+'/','<i class="fa fa-home"></i> Home'))
			else:
				header_navbar_01_button.append((True,True,'/Notebooks/'+notebook_obj.url+'/','<i class="fa fa-home"></i> Home'))
				header_navbar_01_button.append((True,False,'/Notebooks/'+notebook_obj.url+'/Images/','<i class="fa fa-picture-o"></i> Photos'))
		display_paginator_navbar = True
		if template_note_count < template_nb_element_displayed:
			display_paginator_navbar = False
		#----- tags -----#
		note_keywords = notebook_obj.key_words
		tag_list = []
		if note_keywords:
			note_keywords = note_keywords.split(';')	
			tag_list = [i for i in note_keywords if i]
		#----- paginator -----#
		paginator = Paginator(notebook_note_obj_list, template_nb_element_displayed)
		page = request.GET.get('page')
		try:
			PagList = paginator.page(page)
		except PageNotAnInteger:
			# If page is not an integer, deliver first page.
			PagList = paginator.page(1)
		except EmptyPage:
			# If page is out of range (e.g. 9999), deliver last page of results.
			PagList = paginator.page(paginator.num_pages)
		adjacent_pages=2
		startPage = max(PagList.number - adjacent_pages, 1)
		if startPage <= 3: startPage = 1
		endPage = PagList.number + adjacent_pages + 1
		page_numbers = [n for n in range(startPage, endPage) if n > 0 and n <= paginator.num_pages]	
		#----- template render -----#
		context = {
		'notebook_obj':notebook_obj,
		'template_title':template_title,
		'template_note_count':template_note_count,
		'header_h1_text':header_h1_text,
		'header_h2_text':header_h2_text,
		'header_img_url':header_img_url,
		'header_navbar_01_button':header_navbar_01_button,
		'header_navbar_02_button':header_navbar_02_button,	
		'language':language,
		'display_paginator_navbar':display_paginator_navbar,
		'is_owner':is_owner,
		'is_follower':is_follower,
		'form':form,
		'tag_list':tag_list,
		'PagList': PagList, 
		'paginator': paginator, 
		'page_numbers':page_numbers,
		'startPage':startPage,
		'endPage':endPage,
		'show_first': 1 not in page_numbers,
		'show_last': paginator.num_pages not in page_numbers}	
		return render(request, "notebooks/notebook_home.html", context )
	return HttpResponseRedirect('/Notebooks/')

#----------------------------------------------------------------------------------------#

def notebook_images_view(request,notebook_url):
	if Notebook.objects.filter(url=notebook_url).exists():  
		notebook_obj = Notebook.objects.get(url=notebook_url)
		is_owner = False
		is_follower = False
		#----- check permissions -----#
		if request.user.is_authenticated:
			if request.user.id == notebook_obj.user.id: 
				is_owner = True
				notebook_note_obj_list = Notebook_Note.objects.filter(notebook=notebook_obj, note__note_type = 'image', note__removed=False).order_by('-note__date_created')
			else:
				notebook_note_obj_list = Notebook_Note.objects.filter(notebook=notebook_obj, note__note_type = 'image', note__public=True, note__removed=False).order_by('-note__date_created')
		else:
			notebook_note_obj_list = Notebook_Note.objects.filter(notebook=notebook_obj, note__note_type = 'image', note__removed=False, note__public=True).order_by('-note__date_created')
		#----- check user -----#		
		template_nb_element_displayed = 60
		template_note_count = notebook_note_obj_list.count()
		header_h2_text = ""
		if notebook_obj.display_full_name:
			template_title = notebook_obj.full_name + "'s Photos"
			header_h1_text = notebook_obj.full_name + "'s Photos"
		else:
			template_title = notebook_obj.user.username + "'s Photos"
			header_h1_text = notebook_obj.user.username + "'s Photos"
		if notebook_obj.header_img:
			header_img_url = '/media/users/' + notebook_obj.url + '/header_image_1000_1000.png'
		else:
			header_img_url = '/static/notebooks/photos/eiffel-tower-951509_1920.jpg'
		template_heading = 'Groups: '
		template_subheading = '5 000' 
		header_navbar_01_button = []
		header_navbar_02_button = []
		header_navbar_01_button.append((True,False,'/Notebooks/'+notebook_obj.url+'/','<i class="fa fa-home"></i> Home'))
		header_navbar_01_button.append((True,True,'/Notebooks/'+notebook_obj.url+'/Images/','<i class="fa fa-picture-o"></i> Photos'))
		display_paginator_navbar = True
		if template_note_count < template_nb_element_displayed:
			display_paginator_navbar = False
		#----- search -----#
		search_form = Note_Search_Form()
		if request.method == 'POST':
			if 'start_search' in request.POST: 
				search_form = Note_Search_Form(request.POST) 
				if search_form.is_valid():
					note_keywords = request.POST['note_keywords']
					if is_owner: note_can_see = request.POST['note_can_see']					
					request.session['note_search_page'] = request.path
					request.session['note_search_keywords'] = note_keywords
					if is_owner: 
						if 'note_search_can_see' in request.session: 
							request.session['note_search_can_see'] = note_can_see
					return HttpResponseRedirect(request.path)						
			if 'reset_search' in request.POST:
				request.session['note_search_page'] = ''
				request.session['note_search_keywords'] = ''
				if is_owner: request.session['note_search_can_see'] = ''
		else:
			if 'note_search_page' in request.session:
				if request.path == request.session['note_search_page']:								
					note_keywords = request.session['note_search_keywords']
					if is_owner: 
						if 'note_search_can_see' in request.session:
							note_can_see = request.session['note_search_can_see']
					#----- form -----#
					form_dict = {}
					form_dict['note_keywords'] = note_keywords
					if is_owner: 
						if 'note_search_can_see' in request.session: 
							form_dict['note_can_see'] = int(note_can_see)
					search_form = Note_Search_Form(initial=form_dict)
					#----- note keywords -----#
					note_keywords_list = note_keywords.split()
					for note_keywords in note_keywords_list:
						notebook_note_obj_list = notebook_note_obj_list.filter(note__keywords_machine__icontains=note_keywords)				
					#----- note permissions -----#
					if is_owner: 
						if 'note_search_can_see' in request.session: 
							if int(note_can_see) == 1:
								notebook_note_obj_list = notebook_note_obj_list.filter(note__public=False).order_by('-note__date_created')	
							if int(note_can_see) == 2:
								notebook_note_obj_list = notebook_note_obj_list.filter(note__public=True).order_by('-note__date_created')
		#----- form -----#
		form = Image_Upload_Form()
		path_url = request.get_full_path	
		#----- authenticated user -----#			
		if is_owner:
			if request.method == 'POST':
				#----- edit -----#
				if 'add_image' in request.POST:
					form = Image_Upload_Form(request.POST, request.FILES)
					if form.is_valid():
						if request.FILES:
							is_image = False
							image_obj, is_image = fc.image_upload(request,notebook_obj)
							if is_image:
								notebook_obj.nb_public_photos = notebook_obj.nb_public_photos + 1
								notebook_obj.save()
								return HttpResponseRedirect('/Notebooks/'+notebook_obj.url+'/Images/')
							else:
								msg = "Oops! Image type not valid"
								messages.add_message(request, messages.INFO, msg)	
					msg = "Oops! Form not valid"
					messages.add_message(request, messages.INFO, msg)	
		#----- paginator -----#
		paginator = Paginator(notebook_note_obj_list, template_nb_element_displayed)
		page = request.GET.get('page')
		try:
			PagList = paginator.page(page)
		except PageNotAnInteger:
			# If page is not an integer, deliver first page.
			PagList = paginator.page(1)
		except EmptyPage:
			# If page is out of range (e.g. 9999), deliver last page of results.
			PagList = paginator.page(paginator.num_pages)
		adjacent_pages=2
		startPage = max(PagList.number - adjacent_pages, 1)
		if startPage <= 3: startPage = 1
		endPage = PagList.number + adjacent_pages + 1
		page_numbers = [n for n in range(startPage, endPage) if n > 0 and n <= paginator.num_pages]	
		#----- template render -----#
		context = {
		'notebook_obj':notebook_obj,
		'template_title':template_title,
		'template_note_count':template_note_count,
		'header_h1_text':header_h1_text,
		'header_h2_text':header_h2_text,
		'header_img_url':header_img_url,
		'header_navbar_01_button':header_navbar_01_button,
		'header_navbar_02_button':header_navbar_02_button,	
		'template_heading':template_heading,
		'template_subheading':template_subheading,
		'display_paginator_navbar':display_paginator_navbar,
		'is_owner':is_owner,
		'path_url':path_url,
		'search_form':search_form,
		'form':form,
		'PagList': PagList, 
		'paginator': paginator, 
		'page_numbers':page_numbers,
		'startPage':startPage,
		'endPage':endPage,
		'show_first': 1 not in page_numbers,
		'show_last': paginator.num_pages not in page_numbers}	
		return render(request, "notebooks/notebook_images.html", context )
	else:
		return HttpResponseRedirect('/Notebooks/')

#----------------------------------------------------------------------------------------#

def article_create_view(request):
	#----- session language -----#
	language = 'fr'
	if 'language' in request.session: 
		language = request.session['language']
	#----- template variables -----#
	template_name = "notebooks/article_create.html"
	template_title = 'Post a new story'
	header_h1_text = '<br><br><span style="color:white;font-size:28px"> Post a new story</span>'
	header_h2_text = ""
	header_img_url = '/static/notebooks/photos/eiffel-tower-951509_1920.jpg'
	header_navbar_01_button = []
	header_navbar_02_button = []
	#----- form -----#
	path_url = request.path
	note_type_url = path_url.split('/')[1]	
	form = Article_Create_Form()				
	#----- authenticated user -----#
	username = ''
	can_create = False
	if request.user.is_authenticated:
		notebook_obj = Notebook.objects.get(user=request.user.id)
		username = notebook_obj.user.username
		can_create = True
		if request.method == 'POST':
			form = Article_Create_Form(request.POST)
			if form.is_valid():	
				title = request.POST['title']
				public = request.POST['public']	
				content = request.POST['content']
				tags = request.POST['tags']								
				#----- create article -----#
				note_type = 'article'
				url = fc.create_unique_article_url(title)
				fc.create_new_article(
				request.user.id,
				note_type,
				url,
				title,
				content) 				
				article_obj = Article.objects.get(url=url)	
				#----- create note -----#
				current_obj = article_obj				
				fc.create_new_note(
				notebook_obj, 
				note_type, 
				article_obj, 
				public, 
				tags, 
				language)
				#----- create notebook note -----#
				note_obj = Note.objects.get(article=article_obj,note_type=note_type)
				fc.create_notebook_note(notebook_obj,note_obj)
				#----- update article url link -----#
				fc.create_article_url_links(article_obj)			
				#----- create note keywords -----#
				fc.create_note_keywords(note_obj)
				#----- redirect -----#						
				return HttpResponseRedirect('/Articles/'+url+'/')
			else:
				msg = 'Oops! Form not valid'	
				messages.add_message(request, messages.INFO, msg)	
	#----- render template -----#
	context = {
	'template_title':template_title,
	'header_h1_text':header_h1_text,
	'header_h2_text':header_h2_text,
	'header_img_url':header_img_url,
	'header_navbar_01_button':header_navbar_01_button,
	'header_navbar_02_button':header_navbar_02_button,	
	'path_url':path_url,
	'form':form,
	'can_create':can_create,
	'username':username,
	'language':language}
	return render(request, template_name, context)

#----------------------------------------------------------------------------------------#

def article_view(request,note_url):
	#----- session language -----#
	language = 'en'
	if 'language' in request.session: 
		language = request.session['language']
	#----- article -----#
	if Article.objects.filter(url=note_url).exists(): 
		article_obj = Article.objects.get(url=note_url)
		if not article_obj.removed:
			note_obj = Note.objects.get(article=article_obj)		
			#----- user permissions -----#
			can_see,can_edit,can_admin = fc.check_note_permissions(request,note_obj)			
			can_comment = False
			if request.user.is_authenticated:
				can_comment = True
			#----- can see only -----#
			if can_see:
				notebook_note_obj_list = Notebook_Note.objects.filter(note=note_obj,is_author=True)	
				#----- template variables -----#
				template_title = article_obj.title	
				if note_obj.image != None:
					header_img_url = '/media/images/thumbnails_1000_1000/' + note_obj.image.url + note_obj.image.format
				else:
					header_img_url = '/static/notebooks/photos/eiffel-tower-951509_1920.jpg'				
				#----- header navbar -----#
				if can_edit:
					header_h1_text = note_obj.article.title
					header_h2_text = ""
					header_navbar_01_button = []
					header_navbar_02_button = []
					header_navbar_01_button.append((True,True,'/Articles/'+article_obj.url+'/','<i class="fa fa-book"></i> Read'))
					header_navbar_01_button.append((True,False,'/Articles/'+article_obj.url+'/Images/','<i class="fa fa-picture-o"></i> Photos'))
					header_navbar_01_button.append((True,False,'/Articles/'+article_obj.url+'/Edit/','<i class="fa fa-pencil"></i> Edit'))				
				else:
					if article_obj.nb_public_photos == 0:
						header_h1_text = '<br><br>' + note_obj.article.title
						header_h2_text = ""
						header_navbar_01_button = []
						header_navbar_02_button = []
					else:
						header_h1_text = note_obj.article.title
						header_h2_text = ""
						header_navbar_01_button = []
						header_navbar_02_button = []
						header_navbar_01_button.append((True,True,'/Articles/'+article_obj.url+'/','<i class="fa fa-book"></i> Read'))
						header_navbar_01_button.append((True,False,'/Articles/'+article_obj.url+'/Images/','<i class="fa fa-picture-o"></i> Photos'))
				#----- forms -----#
				path_url = request.path	
				#----- tags -----#
				note_keywords = note_obj.keywords
				tag_list = []
				if note_keywords:
					tag_list = note_keywords.split(';')	
				#----- images -----#
				image_url_list = article_obj.image_url_link_list			
				image_obj_list = []
				if len(image_url_list.strip()) > 0:
					image_url_list = image_url_list.split(' ')			
					for image_url in image_url_list:
						if Image.objects.filter(url=image_url).exists():
							image_obj_list.append( Image.objects.get(url=image_url) ) 				
				#----- show start count date-----#
				show_start_count_date = False
				try:
					year = note_obj.date_created.year
					month = note_obj.date_created.month
					day = note_obj.date_created.day				
					date_note_created = datetime.datetime(year,month,day)
					date_counting_started = datetime.datetime(2019,5,15)
					if date_note_created < date_counting_started:
						show_start_count_date = True
				except:
					pass								
				#----- main author online -----#
				present_date = datetime.datetime.now()
				ref_date = present_date - datetime.timedelta(minutes=5)	
				author_is_online = False

				#----- template render -----#
				context = {
				'template_title':template_title,
				'header_h1_text':header_h1_text,
				'header_h2_text':header_h2_text,
				'header_img_url':header_img_url,
				'header_navbar_01_button':header_navbar_01_button,
				'header_navbar_02_button':header_navbar_02_button,			
				'note_obj':note_obj,
				'tag_list':tag_list,
				'image_obj_list':image_obj_list,
				'language':language,
				'author_is_online':author_is_online,
				'show_start_count_date':show_start_count_date}
				return render(request, "notebooks/article.html", context )				
	msg = 'Oops! Article does not exist, has been removed or is not public'		
	messages.add_message(request, messages.INFO, msg)
	return HttpResponseRedirect("/Articles/") 

#----------------------------------------------------------------------------------------#

def article_images_view(request,note_url):
	#----- session language -----#
	language = 'en'
	if 'language' in request.session: 
		language = request.session['language']
	#----- article -----#	
	if Article.objects.filter(url=note_url).exists(): 
		article_obj = Article.objects.get(url=note_url)
		if not article_obj.removed:
			note_obj = Note.objects.get(article=article_obj)
			can_see,can_edit,can_admin = fc.check_note_permissions(request,note_obj)
			if can_see:
				#----- template variables -----#
				template_title = article_obj.title	
				if note_obj.image != None:
					header_img_url = '/media/images/thumbnails_1000_1000/' + note_obj.image.url + note_obj.image.format
				else:
					header_img_url = '/static/notebooks/photos/eiffel-tower-951509_1920.jpg'
				#----- header navbar -----#				
				if can_edit:
					header_h1_text = note_obj.article.title
					header_h2_text = ""
					header_navbar_01_button = []
					header_navbar_02_button = []
					header_navbar_01_button.append((True,False,'/Articles/'+article_obj.url+'/','<i class="fa fa-book"></i> Read'))
					header_navbar_01_button.append((True,True,'/Articles/'+article_obj.url+'/Images/','<i class="fa fa-picture-o"></i> Photos'))
					header_navbar_01_button.append((True,False,'/Articles/'+article_obj.url+'/Edit/','<i class="fa fa-pencil"></i> Edit'))				
				else:
					if article_obj.nb_public_photos == 0:
						header_h1_text = '<br><br>' + note_obj.article.title
						header_h2_text = ""
						header_navbar_01_button = []
						header_navbar_02_button = []
					else:
						header_h1_text = note_obj.article.title
						header_h2_text = ""
						header_navbar_01_button = []
						header_navbar_02_button = []
						header_navbar_01_button.append((True,True,'/Articles/'+article_obj.url+'/','<i class="fa fa-book"></i> Read'))
						header_navbar_01_button.append((True,False,'/Articles/'+article_obj.url+'/Images/','<i class="fa fa-picture-o"></i> Photos'))
				#----- form -----#
				form = Image_Upload_Form()
				path_url = request.get_full_path	
				#----- authenticated user -----#			
				username = ''
				can_create = False
				if can_edit:
					if request.user.is_authenticated:
						notebook_obj = Notebook.objects.get(user=request.user)
						username = notebook_obj.user.username
						can_create = True
						if request.method == 'POST':
							#----- edit -----#
							if 'add_image' in request.POST:
								form = Image_Upload_Form(request.POST, request.FILES)
								print(form)
								if form.is_valid():
									if request.FILES:
										is_image = False
										image_obj, is_image = fc.image_upload(request,notebook_obj)
										if is_image:
											note_image_obj = Note.objects.get(image=image_obj)
											new_note_link = Note_Link(
											notebook = notebook_obj,
											note_01 = note_obj,
											note_02 = note_image_obj,
											removed = False)
											new_note_link.save()
											note_link_obj_list = Note_Link.objects.filter(note_01=note_obj,note_02__public=True,removed=False)
											article_obj.nb_public_photos = note_link_obj_list.count()
											article_obj.save()
											notebook_obj.nb_public_photos = notebook_obj.nb_public_photos + 1
											notebook_obj.save()
											return HttpResponseRedirect('/Articles/'+article_obj.url+'/Images/')
								msg = "Oops! Form not valid"
								messages.add_message(request, messages.INFO, msg)										
							#----- link image -----#
							if 'link_image' in request.POST:
								form = Link_Form(request.POST)
								if form.is_valid():
									url = request.POST['url']	
									if Image.objects.filter(url=url).exists():  
										image_obj = Image.objects.get(url=url)
										if not image_obj.removed:
											image_note_obj = Note.objects.get(image=image_obj)
											if not Note_Link.objects.filter(note_01=note_obj,note_02=image_note_obj,removed=False).exists():
												note_image_obj = Note.objects.get(image=image_obj)
												new_note_link = Note_Link(
												notebook = notebook_obj,
												note_01 = note_obj,
												note_02 = note_image_obj,
												removed = False)
												new_note_link.save()
												msg = "The image has been added"
												note_link_obj_list = Note_Link.objects.filter(note_01=note_obj,note_02__public=True,removed=False)
												article_obj.nb_public_photos = note_link_obj_list.count()
												article_obj.save()
											else:
												msg = "Oops! Image is already linked to the article"
											messages.add_message(request, messages.INFO, msg)
							#----- link image -----#
							if 'unlink_image' in request.POST:
								form = Link_Form(request.POST)
								if form.is_valid():
									url = request.POST['url']	
									if Image.objects.filter(url=url).exists():  
										image_obj = Image.objects.get(url=url)
										if not image_obj.removed:
											image_note_obj = Note.objects.get(image=image_obj)
											if Note_Link.objects.filter(note_01=note_obj,note_02=image_note_obj,removed=False).exists():
												note_link_obj = Note_Link.objects.get(note_01=note_obj,note_02=image_note_obj,removed=False)
												note_link_obj.removed = True
												note_link_obj.save()
												note_link_obj_list = Note_Link.objects.filter(note_01=note_obj,note_02__public=True,removed=False)
												article_obj.nb_public_photos = note_link_obj_list.count()
												article_obj.save()
												msg = "Image has been unliked"
											else:
												msg = "Oops! Image is already linked to the article"
											messages.add_message(request, messages.INFO, msg)				
				if can_edit:
					note_link_obj_list = Note_Link.objects.filter(note_01=note_obj,removed=False)
				else:
					note_link_obj_list = Note_Link.objects.filter(note_01=note_obj,note_02__public=True,removed=False)
				#----- paginator -----#
				paginator = Paginator(note_link_obj_list, 50)
				page = request.GET.get('page')
				try:
					PagList = paginator.page(page)
				except PageNotAnInteger:
					# If page is not an integer, deliver first page.
					PagList = paginator.page(1)
				except EmptyPage:
					# If page is out of range (e.g. 9999), deliver last page of results.
					PagList = paginator.page(paginator.num_pages)
				adjacent_pages=2
				startPage = max(PagList.number - adjacent_pages, 1)
				if startPage <= 3: startPage = 1
				endPage = PagList.number + adjacent_pages + 1
				page_numbers = [n for n in range(startPage, endPage) if n > 0 and n <= paginator.num_pages]	
				#----- render template -----#
				context = {
				'template_title':template_title,
				'header_h1_text':header_h1_text,
				'header_h2_text':header_h2_text,
				'header_img_url':header_img_url,
				'header_navbar_01_button':header_navbar_01_button,
				'header_navbar_02_button':header_navbar_02_button,
				'note_link_obj_list':note_link_obj_list,
				'path_url':path_url,
				'form':form,
				'can_create':can_create,
				'can_edit':can_edit,
				'username':username,
				'language':language,
				'PagList': PagList, 
				'paginator': paginator, 
				'page_numbers':page_numbers,
				'startPage':startPage,
				'endPage':endPage,
				'show_first': 1 not in page_numbers,
				'show_last': paginator.num_pages not in page_numbers}	
				return render(request, "notebooks/article_images.html", context)
	msg = 'Oops! Article does not exist, has been removed or is not public'		
	messages.add_message(request, messages.INFO, msg)
	return HttpResponseRedirect("/Articles/") 

#----------------------------------------------------------------------------------------#

def article_edit_view(request,note_url):
	#----- session language -----#
	language = 'en'
	if 'language' in request.session: 
		language = request.session['language']
	#----- article -----#	
	if Article.objects.filter(url=note_url).exists(): 
		article_obj = Article.objects.get(url=note_url)
		if not article_obj.removed:
			note_obj = Note.objects.get(article=article_obj)
			can_see,can_edit,can_admin = fc.check_note_permissions(request,note_obj)
			if can_see:
				#----- template variables -----#
				template_title = article_obj.title	
				header_h1_text = note_obj.article.title
				header_h2_text = ""
				if note_obj.image != None:
					header_img_url = '/media/images/thumbnails_1000_1000/' + note_obj.image.url + note_obj.image.format
				else:
					header_img_url = '/static/notebooks/photos/eiffel-tower-951509_1920.jpg'
				header_navbar_01_button = []
				header_navbar_02_button = []
				header_navbar_01_button.append((True,False,'/Articles/'+article_obj.url+'/','<i class="fa fa-book"></i> Read'))
				header_navbar_01_button.append((True,False,'/Articles/'+article_obj.url+'/Images/','<i class="fa fa-picture-o"></i> Photos'))
				header_navbar_01_button.append((True,True,'/Articles/'+article_obj.url+'/Edit/','<i class="fa fa-pencil"></i> Edit'))
				#----- form -----#
				path_url = request.path
				note_type_url = path_url.split('/')[1]
				dest = path_url.replace('Edit/','')			
				#----- form -----#
				form_dict = {}
				form_dict['title'] = note_obj.article.title
				form_dict['public'] = note_obj.public
				form_dict['comments'] = note_obj.comments
				form_dict['language'] = note_obj.language
				form_dict['content'] = note_obj.article.content
				form_dict['tags'] = note_obj.keywords
				form_edit = Article_Edit_Form(initial=form_dict)						
				#----- authenticated user -----#
				username = ''
				if request.user.is_authenticated:
					notebook_obj = Notebook.objects.get(user=request.user.id)
					if can_edit:
						username = notebook_obj.user.username
						if request.method == 'POST':
							#----- link image -----#
							if 'header_image' in request.POST:
								form = Link_Form(request.POST)
								if form.is_valid():
									url = request.POST['url']	
									if Image.objects.filter(url=url).exists():  
										image_obj = Image.objects.get(url=url)
										if not image_obj.removed:
											note_obj.image = image_obj
											note_obj.save()
											#----- Redirect -----#
											return HttpResponseRedirect(dest)
									if url == 'no header image':
										note_obj.image = None
										note_obj.save()
							#----- remove -----#		
							if 'remove_note' in request.POST:
								form_remove = Note_Remove_Form(request.POST)
								if form_remove.is_valid():	
									remove_text = request.POST['remove_text']														
									can_remove = True
									if can_remove:					
										if 'remove' in remove_text or 'supprimer' in remove_text:
											fc.remove_note(note_obj)
											msg = 'The article has been removed'
											messages.add_message(request, messages.INFO, msg)
											return HttpResponseRedirect("/Articles/") 
								else:
									msg = 'Oops! you need to enter the word remove to valid the form'
									messages.add_message(request, messages.INFO, msg)
							#----- edit -----#
							if 'edit_note' in request.POST:		
								form_edit = Article_Edit_Form(request.POST)	
								if form_edit.is_valid():			
									title = request.POST['title']
									public = request.POST['public']	
									comments = request.POST['comments']	
									article_language = request.POST['language']	
									content = request.POST['content']
									tags = request.POST['tags']
									#----- update article -----#	
									content_formatted = fc.convert_content_markdown(content, note_type='article')	
									article_obj.title = title 
									article_obj.content = content 
									article_obj.content_formatted = content_formatted 
									article_obj.save()						
									note_obj.keywords = tags
									note_obj.save()							
									#----- update note -----#
									note_obj.public = public
									note_obj.comments = comments
									note_obj.language = language
									note_obj.keywords = tags
									note_obj.save()
									#----- update article url link -----#
									fc.create_article_url_links(article_obj)
									#----- create note keywords -----#
									fc.create_note_keywords(note_obj)
									#----- Redirect -----#
									return HttpResponseRedirect(dest)
								else:						
									msg = 'Oops! Form not valid'	
									messages.add_message(request, messages.INFO, msg)
					else:
						msg = 'Oops! you do not have the permission to edit the article'
						messages.add_message(request, messages.INFO, msg)
				else:
					msg = '' #'Oops! you need to be <a href="/Sign-in/">logged in</a> to use this form'
					messages.add_message(request, messages.INFO, msg)
				context = {
				'template_title':template_title,
				'header_h1_text':header_h1_text,
				'header_h2_text':header_h2_text,
				'header_img_url':header_img_url,
				'header_navbar_01_button':header_navbar_01_button,
				'header_navbar_02_button':header_navbar_02_button,			
				'note_obj':note_obj,
				'path_url':path_url,
				'form':form_edit,
				'can_admin':can_admin,
				'can_edit':can_edit,
				'username':username,
				'language':language}
				return render(request, "notebooks/article_edit.html", context )	
	msg = 'Oops! Article does not exist, has been removed or is not public'		
	messages.add_message(request, messages.INFO, msg)
	return HttpResponseRedirect("/Articles/") 

#----------------------------------------------------------------------------------------#

def image_view(request,note_url):
	#----- session language -----#
	language = 'en'
	if 'language' in request.session: 
		language = request.session['language']
	#----- article -----#
	if Image.objects.filter(url=note_url).exists(): 
		image_obj = Image.objects.get(url=note_url)
		if not image_obj.removed:
			note_obj = Note.objects.get(image=image_obj, note_type='image')		
			#----- user permissions -----#
			can_see,can_edit,can_admin = fc.check_note_permissions(request,note_obj)			
			can_comment = False
			if request.user.is_authenticated:
				can_comment = True
			#----- can see only -----#
			if can_see:
				notebook_note_obj_list = Notebook_Note.objects.filter(note=note_obj,is_author=True)	
				#----- template variables -----#
				template_title = image_obj.url	
				header_h1_text = note_obj.image.url
				header_h2_text = ""
				header_img_url = '/static/notebooks/photos/eiffel-tower-951509_1920.jpg'
				header_navbar_01_button = []
				header_navbar_02_button = []
				header_navbar_01_button.append((True,True,'/Images/'+image_obj.url+'/','<i class="fa fa-book"></i> Read'))
				header_navbar_01_button.append((True,False,'/Images/'+image_obj.url+'/Images/','<i class="fa fa-picture-o"></i> Photos'))
				header_navbar_01_button.append((True,False,'/Images/'+image_obj.url+'/Edit/','<i class="fa fa-pencil"></i> Edit'))
				#----- form ----- #
				form = Image_Upload_Form()
				path_url = request.get_full_path
				username = ''
				if request.user.is_authenticated:
					notebook_obj = Notebook.objects.get(user=request.user)	
					username = notebook_obj.user.username
					if can_edit:
						if request.method == 'POST':
							#----- remove -----#		
							if 'remove_image' in request.POST:
								form_remove = Note_Remove_Form(request.POST)
								if form_remove.is_valid():	
									remove_text = request.POST['remove_text']
									if can_admin:					
										if 'remove' in remove_text or 'supprimer' in remove_text:
											try:
												path_to_media = settings.MEDIA_ROOT
												#----- remove files -----#
												command = 'rm ' + (path_to_media + 'images/src/' + image_obj.url + image_obj.format)
												os.system(command)
												command = 'rm ' + (path_to_media + 'images/thumbnails_500_500/' + image_obj.url + image_obj.format)
												os.system(command)
												command = 'rm ' + (path_to_media + 'images/thumbnails_1000_1000/' + image_obj.url + image_obj.format)
												os.system(command)	
												#----- remove in database -----#
												fc.remove_note(note_obj)	
												messages.add_message(request, messages.INFO, u"Image has been removed")				
											except:
												messages.add_message(request, messages.INFO, u"An error has occured while trying to remove the image. Please contact an administraor")	
											return HttpResponseRedirect("/Notebooks/"+notebook_obj.url+'/') 
							#----- edit -----#
							if 'edit_image' in request.POST:
								form = Image_Upload_Form(request.POST, request.FILES)
								if form.is_valid():
									if request.FILES:
										is_image = fc.image_replace(request,notebook_obj,note_obj,image_obj)	
									public = request.POST['public']						
									content = request.POST['content']
									tags = request.POST['tags']
									note_obj.public = public
									note_obj.abstract = content
									note_obj.keywords = tags
									note_obj.save()								
									#----- create note keywords -----#
									fc.create_note_keywords(note_obj)
									#----- timestamp -----#
									now = datetime.datetime.now()
									image_obj.timestamp = datetime.datetime.timestamp(now)
									image_obj.save()
									return HttpResponseRedirect(request.path)
								else:
									msg = "Oops! Form not valid"
									messages.add_message(request, messages.INFO, msg)	
				#----- links -----#
				note_link_obj_list = Note_Link.objects.filter(note_02=note_obj,removed=False)
				#----- tags -----#
				note_keywords = note_obj.keywords
				tag_list = []
				if note_keywords:
					tag_list = note_keywords.split(';')					
				#----- template render -----#
				context = {
				'template_title':template_title,
				'header_h1_text':header_h1_text,
				'header_h2_text':header_h2_text,
				'header_img_url':header_img_url,
				'header_navbar_01_button':header_navbar_01_button,
				'header_navbar_02_button':header_navbar_02_button,			
				'note_obj':note_obj,
				'can_edit':can_edit,
				'path_url':path_url,
				'note_link_obj_list':note_link_obj_list,
				'tag_list':tag_list,
				'language':language}
				return render(request, "notebooks/image.html", context )				
	msg = 'Oops! Image does not exist, has been removed or is not public'		
	messages.add_message(request, messages.INFO, msg)
	return HttpResponseRedirect("/") 

#----------------------------------------------------------------------------------------#

def note_search_view(request):

	#----- variables initialization -----#

	header_note_create_button = False
	header_note_create_button_url = ''
	header_note_create_button_txt = ''	

	header_note_create_button = False
	header_note_create_button_active= False	
	header_note_create_button_url = ''
	header_note_create_button_txt = ''	

	header_photo_upload_button = False
	header_photo_upload_button_active = False	
	header_photo_upload_button_url = ''
	header_photo_upload_button_txt = ''	

	#----- set-up page -----#
	
	note_obj_list = Note.objects.all()  
	
	if request.path == '/Travels/':
		template_title = 'Travels'
		template_name = 'note_search.html'
		header_h1_text = "Ready to travel" 
		header_h2_text = "<br> Read our latest stories or add yours !"
		header_img_url = '/static/notebooks/photos/VEG-arrivee_avion.jpg'
		header_note_create_button = True
		header_note_create_button_url = '/Travels/Create/'
		header_note_create_button_txt = 'Add a new story'

	if request.path == '/Photos/':
		template_title = 'Photos'
		template_name = 'photos_search.html'
		header_h1_text = "Photos" 
		header_h2_text = ""
		header_img_url = '/static/notebooks/photos/photo-256888_1920.jpg'
		header_photo_upload_button = True
		header_photo_upload_button_url = '/Photos/Upload/'
		header_photo_upload_button_txt = 'Upload a new photo'	
		note_obj_list = Note.objects.filter(note_type=1, removed=False, public=True).order_by('-date_modified')	

	if request.path == '/Addresses/':
		template_title = 'Addresses'
		template_name = 'note_search.html'
		header_h1_text = "Ready to Recipes" 
		header_h2_text = "<br> Read our latest stories or add yours !"
		header_img_url = '/static/notebooks/photos/hotel-room-1447201_1920.jpg'
		header_note_create_button = True
		header_note_create_button_url = '/Travels/Create/'
		header_note_create_button_txt = 'Add a new story'

	if request.path == '/Recipes/':
		template_title = 'Recipes'
		template_name = 'note_search.html'
		header_h1_text = "Ready to Recipes" 
		header_h2_text = "<br> Read our latest stories or add yours !"
		header_img_url = '/static/notebooks/photos/dough-943245_1920.jpg'
		header_note_create_button = True
		header_note_create_button_url = '/Travels/Create/'
		header_note_create_button_txt = 'Add a new story'	

	#----- paginator -----#
	paginator = Paginator(note_obj_list, 50)
	page = request.GET.get('page')
	try:
		PagList = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		PagList = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		PagList = paginator.page(paginator.num_pages)
	adjacent_pages=2
	startPage = max(PagList.number - adjacent_pages, 1)
	if startPage <= 3: startPage = 1
	endPage = PagList.number + adjacent_pages + 1
	page_numbers = [n for n in range(startPage, endPage) if n > 0 and n <= paginator.num_pages]	
	#----- template render -----#
	context = {
	'template_title':template_title,
	'header_h1_text':header_h1_text,
	'header_h2_text':header_h2_text,
	'header_img_url':header_img_url,
	'header_note_create_button':header_note_create_button,
	'header_note_create_button_url':header_note_create_button_url,
	'header_note_create_button_txt':header_note_create_button_txt,
	'header_photo_upload_button':header_photo_upload_button,
	'header_photo_upload_button_url':header_photo_upload_button_url,
	'header_photo_upload_button_txt':header_photo_upload_button_txt,	
	'PagList': PagList, 
	'paginator': paginator, 
	'page_numbers':page_numbers,
	'startPage':startPage,
	'endPage':endPage,
	'show_first': 1 not in page_numbers,
	'show_last': paginator.num_pages not in page_numbers}	
	return render(request, "notebooks/"+template_name, context )	





















