# -*- coding: utf-8 -*-

from django.conf import settings

from .models import Notebook
from .models import Notebook_Note
from .models import Notebook_Stats
from .models import Article
from .models import Image
from .models import Note
from .models import Note_Link

from .models import Image_Upload_Form

from PIL import Image as img_pil

from . import apps_functions as fc

import os
import markdown
import re
import unicodedata
import datetime

md = markdown.Markdown(extensions=['markdown.extensions.extra','markdown.extensions.toc','markdown.extensions.nl2br'], safe_mode=True)

#----------------------------------------------------------------------------------------#

def create_unique_image_url(title):
	title = title.strip()
	url = title.replace (" ", "-")
	url = title.replace ("_", "-")
	url = unicodedata.normalize('NFD', url).encode('ascii', 'ignore') 
	url = url.decode("utf-8")
	url = [let for let in url if let.isdigit() or let.isalpha() or let == '-'  ]
	url = "".join(url)
	if Image.objects.filter(url=url).exists():
		add_pref = 1
		tmp_url = url
		while( Image.objects.filter(url=tmp_url).exists() ):
			tmp_url = url + '-' + str(add_pref)
			add_pref = add_pref + 1
		url = tmp_url
	return url

#----------------------------------------------------------------------------------------#

def create_unique_article_url(title):
	title = title.strip()
	url = title.replace (" ", "-")
	url = unicodedata.normalize('NFD', url).encode('ascii', 'ignore') 
	url = url.decode("utf-8")
	url = [let for let in url if let.isdigit() or let.isalpha() or let == '-'  ]
	url = "".join(url)
	url_exists = Article.objects.filter(url=url).count() 
	if url_exists == 1:
		add_pref = 1
		while( url_exists == 1 ):
			url_modified = url + '-' + str(add_pref)
			url_exists = Article.objects.filter(url=url_modified).count() 
			add_pref = add_pref + 1
		url = url_modified
	return url

#----------------------------------------------------------------------------------------#

def check_note_permissions(request,note_obj):
	#----- can edit -----#
	can_see = False
	if note_obj.public:
		can_see = True
	#----- can edit -----#
	can_admin = False
	can_edit = False	
	if request.user.is_authenticated:
		notebook_obj = Notebook.objects.get(user=request.user)
		if Notebook_Note.objects.filter(notebook=notebook_obj,note=note_obj).exists():
			notebook_note_obj = Notebook_Note.objects.get(notebook=notebook_obj,note=note_obj)
			can_admin = notebook_note_obj.can_admin
			can_see = notebook_note_obj.can_see
			can_edit = notebook_note_obj.can_edit
	#----- redirect -----#
	return can_see,can_edit,can_admin

#----------------------------------------------------------------------------------------#

def create_new_article(user_id, note_type, url, title, content):
	content_formatted = convert_content_markdown(content, note_type)	
	notebook_obj = Notebook.objects.get(user=user_id)
	if Article.objects.filter(removed=True).exists():
		article_obj = Article.objects.filter(removed=True)[0]
		article_obj.notebook = notebook_obj
		article_obj.url = url
		article_obj.title = title
		article_obj.content = content
		article_obj.content_formatted = content_formatted
		article_obj.article_url_link_list = ''
		article_obj.image_url_link_list = ''
		article_obj.file_url_link_list = ''
		article_obj.video_url_link_list = ''
		article_obj.removed = False
		article_obj.save()
	else:
		new_article = Article(
		notebook = notebook_obj,
		url = url,
		title = title,
		content = content,
		content_formatted = content_formatted,
		article_url_link_list = '',
		image_url_link_list = '',
		file_url_link_list = '',
		video_url_link_list = '',
		removed = False)
		new_article.save()

#----------------------------------------------------------------------------------------#

def convert_content_markdown(content, note_type):
	content_formatted = md.convert(content) 
	image_index = 0
	image_carousel_idx = 0
	image_id_list = []
	#----- Images -----#
	line_list = content_formatted.splitlines()
	line_list_len = len(line_list)
	#for i in iter(content_formatted.splitlines()):
	for idx,i in enumerate(line_list): 
		if not i.startswith('<pre><code>'):
			image_found = False
			#----- image -----#
			m = re.search('\[image:(.*) size:(.*) caption:(.*)\]', i)
			if m and not image_found:
				image_found = True
				if Image.objects.filter( url = m.group(1).strip() ).exists() :
					image_obj = Image.objects.get( url = m.group(1).strip() )
					image_id = image_obj.id
					in_re = '[image:'+m.group(1)+' size:'+m.group(2)+' caption:'+m.group(3)+']'								
					#----- image width -----#
					img_size = str(m.group(2)).strip()
					if img_size.isdigit():
						if int(img_size) > 100: img_size = 100
						if int(img_size) < 10: img_size = 10
					else:
						img_size = 50
					#----- replace -----#
					out_re = '<figure class="image" style="width:'+str(img_size)+'%"> <span data-target="#myModal" data-toggle="modal"> <img class="card-img-top" src="/media/images/thumbnails_1000_1000/'+str(m.group(1)).strip()+str(image_obj.format)+'" alt=""></span><figcaption style="text-align:center; font-size: 13px; font-family: Yellowtail; color: #06a;">'+m.group(3)+'</figcaption></figure>'									
					#out_re = '<figure class="image" style="width:'+str(img_size)+'%"><a title="Image 1" style="cursor: pointer;"> <img class="image_element" id="'+str(image_index)+'"  style="width:100%" src="/media/images/thumbnails_1000_1000/'+str(m.group(1)).strip()+str(image_obj.format)+'" alt="" data-toggle="lightbox" data-gallery="multiimages"></a><figcaption style="background-color: white;">'+m.group(3)+'</figcaption></figure>' 
					line_list[idx] = line_list[idx].replace(in_re, out_re)
					image_index = image_index + 1
					image_id_list.append(str(image_id))	
			#----- multiple images with caption and size
			m = re.search('\[images:(.*) dim:(.*) size:(.*) caption:(.*)\]', i)
			if m and not image_found:
				image_found = True
				images = m.group(1).strip()
				dim = m.group(2).strip()
				caption = m.group(4).strip()
				images = images.split(';')
				dim = dim.split('*')
				dim1 = dim[0]
				dim2 = dim[1]
				#if int( dim1 ) * int( dim2 ) == len(images):
				#	print( 'ok nombre image' )
				#else:
				#	print( 'Houston we have a problem')
				in_re = '[images:'+str(m.group(1))+' dim:'+m.group(2)+' size:'+m.group(3)+' caption:'+m.group(4)+']'
				multiple_images_list = []
				multiple_images_list.append('<figure class="image" style="width:'+str(m.group(3)).strip()+'%">')
				col = 1
				row = 1
				for image in images:
					if col == int(dim2) and row < int(dim1):
						if Image.objects.filter( url = image ).exists():
							image_obj = Image.objects.get(url=image)
							image_id = image_obj.id
							multiple_images_list.append('<span data-target="#myModal" data-toggle="modal"> <img class="image_element" id="'+str(image_index)+'" src="/media/images/thumbnails_1000_1000/'+image.strip()+str(image_obj.format)+'" style="width:'+str(95.0/int(dim2))+'%;margin:0.25%;" alt="" data-toggle="lightbox" data-gallery="multiimages"></span>')
							image_index = image_index + 1
							image_id_list.append(str(image_id))
						multiple_images_list.append('<br>')
						col = 1
						row = row + 1
					else:
						if Image.objects.filter( url = image ).exists():
							image_obj = Image.objects.get(url=image)
							image_id = image_obj.id	
							multiple_images_list.append('<span data-target="#myModal" data-toggle="modal"> <img class="image_element" id="'+str(image_index)+'" src="/media/images/thumbnails_1000_1000/'+image.strip()+str(image_obj.format)+'" style="width:'+str(95.0/int(dim2))+'%;margin:0.25%;" alt="" data-toggle="lightbox" data-gallery="multiimages"></span>')
							image_index = image_index + 1
							image_id_list.append(str(image_id))
						col = col + 1
					#print col, row, col == int(dim2), row < int(dim1), dim1, dim2
				multiple_images_list.append('<figcaption style="text-align:center; font-size: 13px; font-family: Yellowtail; color: #06a;">'+caption+"</figcaption>")
				multiple_images_list.append("</figure>")
				out_re = ''.join(multiple_images_list)	
				line_list[idx] = line_list[idx].replace(in_re, out_re)
			#----- multiple images (carousel) -----#
			m = re.search('\[images:(.*) size:(.*) style:carousel caption:(.*)\]', i)
			if m and not image_found:
				image_found = True
				images = m.group(1).strip()
				caption = m.group(3).strip()
				images = images.split(';')

				#----- image width -----#
				img_size = str(m.group(2)).strip()
				if img_size.isdigit():
					if int(img_size) > 100: img_size = 100
					if int(img_size) < 10: img_size = 10
				else:
					img_size = 50
			
				in_re = '[images:'+str(m.group(1))+' size:'+m.group(2)+' style:carousel'+' caption:'+m.group(3)+']'
				
				multiple_images_list = []
				multiple_images_list.append('<figure class="image" style="width:'+str(img_size)+'%">')
				multiple_images_list.append('<div id="carouselExampleControls_'+str(image_carousel_idx)+'" class="carousel slide" data-ride="carousel" data-interval="false">')
				
				multiple_images_list.append('<div class="carousel-inner" role="listbox">')
				image_active = True
				for image in images:
					if Image.objects.filter( url = image ).exists():
						image_obj = Image.objects.get(url=image)
						image_id = image_obj.id
						
						if image_active:
							multiple_images_list.append('<div class="carousel-item active">')
							image_active = False
						else:
							multiple_images_list.append('<div class="carousel-item">')
						multiple_images_list.append('<img class="d-block img-fluid" src="/media/images/thumbnails_1000_1000/'+image.strip()+str(image_obj.format)+'" alt="First slide">')
						multiple_images_list.append('</div>')
						
						#multiple_images_list.append('<span data-target="#myModal" data-toggle="modal"> <a data-slide-to="'+str(image_index)+'" href="#myGallery"> <img class="image_element" id="'+str(image_index)+'" src="/media/images/thumbnails_1000_1000/'+image.strip()+str(image_obj.format)+'" style="width:'+str(95.0/int(dim2))+'%;margin:0.25%;" alt="" data-toggle="lightbox" data-gallery="multiimages"></span></a>')
						
						image_index = image_index + 1
						image_id_list.append(str(image_id))
				multiple_images_list.append('</div>')
				
				multiple_images_list.append('<a class="carousel-control-prev" href="#carouselExampleControls_'+str(image_carousel_idx)+'" role="button" data-slide="prev">')
				multiple_images_list.append('<span class="carousel-control-prev-icon" aria-hidden="true"></span>')
				multiple_images_list.append('<span class="sr-only">Previous</span>')
				multiple_images_list.append('</a>')
				multiple_images_list.append('<a class="carousel-control-next" href="#carouselExampleControls_'+str(image_carousel_idx)+'" role="button" data-slide="next">')
				multiple_images_list.append('<span class="carousel-control-next-icon" aria-hidden="true"></span>')
				multiple_images_list.append('<span class="sr-only">Next</span>')
				multiple_images_list.append('</a>')
				
				multiple_images_list.append('<figcaption style="text-align:center; font-size: 13px; font-family: Yellowtail; color: #06a;">'+caption+'</figcaption>')
				
				multiple_images_list.append('</div>')
				multiple_images_list.append('</figure>')
				
				image_carousel_idx = image_carousel_idx + 1
				
				out_re = ''.join(multiple_images_list)	
				line_list[idx] = line_list[idx].replace(in_re, out_re)
	content_formatted = '\n'.join(line_list) 			    
	#----- Tables -----#
	content_formatted = content_formatted.replace ('<table>', '<table class="table table-striped">') 
	#----- video -----#
	nb_video = 0
	line_list = content_formatted.splitlines()
	for idx,i in enumerate(line_list): 
		if nb_video < 1:
			if not i.startswith('<pre><code>'):
				m = re.search('\[youtube_video_id:(.*) caption:(.*)\]', i)
				if m:
					in_re = '[youtube_video_id:'+str(m.group(1))+' caption:'+str(m.group(2))+']'
					nb_video = nb_video + 1
					if not note_type == 'faq':
						if idx == 0:
							out_re = '</p><div class="embed-responsive embed-responsive-16by9"><iframe class="embed-responsive-item" src="https://www.youtube.com/embed/'+str(m.group(1))+'"></iframe></div><br><p>'
						else:
							out_re = '</p><br><div class="embed-responsive embed-responsive-16by9"><iframe class="embed-responsive-item" src="https://www.youtube.com/embed/'+str(m.group(1))+'"></iframe></div><br><p>'
					else:						
						if idx == 0:
							out_re = '<div class="embed-responsive embed-responsive-16by9"><iframe class="embed-responsive-item" src="https://www.youtube.com/embed/'+str(m.group(1))+'"></iframe></div><br>'
						else:
							out_re = '<br><div class="embed-responsive embed-responsive-16by9"><iframe class="embed-responsive-item" src="https://www.youtube.com/embed/'+str(m.group(1))+'"></iframe></div><br>'
					line_list[idx] = line_list[idx].replace(in_re, out_re)
	content_formatted = '\n'.join(line_list) 
	#----- code -----#
	line_list = content_formatted.splitlines()
	line_of_code = False
	for idx,i in enumerate(line_list): 		
		if i.startswith('</code></pre>'):
			line_of_code = False
		if line_of_code:
			line_list[idx] = '<code>'+line_list[idx]+'</code>'
		if i.startswith('<pre><code>'):
			line_of_code = True
			line_list[idx] = line_list[idx]+'</code>'
			line_list[idx] = line_list[idx].replace('<pre>', '<pre class="code">')
	content_formatted = '\n'.join(line_list) 
	#----- return -----#
	return content_formatted

#----------------------------------------------------------------------------------------#

def create_article_url_links(article_obj):
	article_link_list = []
	image_link_list = []
	file_link_list = []
	article_content_formatted = article_obj.content_formatted
	#----- article & file links -----#
	link_list = re.findall('<a href="(.*?)">(.*?)</a>', article_content_formatted,re.DOTALL)
	for i,link in enumerate(link_list):
		s = link[0]
		url_element_list = s.split('/')
		if len(url_element_list) > 3:
			if url_element_list[1] == 'Articles':
				if Article.objects.filter(url=url_element_list[2]).exists():
					article_link_list.append(url_element_list[2])
			if url_element_list[1] == 'Files':
				if File.objects.filter(url=url_element_list[2]).exists():
					file_link_list.append(url_element_list[2])
	#----- image links -----#								
	link_list = re.findall('src="/media/images/thumbnails_1000_1000/(.*?)"', article_content_formatted,re.DOTALL)
	for i,link in enumerate(link_list):
		s = link
		image_url_list = s.split('.')
		image_url = image_url_list[0]
		if Image.objects.filter(url=image_url).exists():
			image_link_list.append(image_url)			
	#----- update article -----#
	article_obj.article_url_link_list = ' '.join(article_link_list)	
	article_obj.image_url_link_list = ' '.join(image_link_list)	
	article_obj.file_url_link_list = ' '.join(file_link_list)	
	article_obj.save()

#----------------------------------------------------------------------------------------#

def create_new_note(notebook_obj, note_type, current_obj, public, keywords, language):	
	#----- initialize -----#
	article_obj = None
	gallery_obj = None
	image_obj = None
	title = ''
	note_full_path = ''
	#----- article -----#
	if note_type == 'article': 
		article_obj = current_obj
		title = article_obj.title
		note_full_path = '/Articles/'+article_obj.url+'/'
	#----- image -----#
	if note_type == 'image': 
		image_obj = current_obj	
		title = image_obj.url
		note_full_path = '/Images/'+image_obj.url+'/'
	#----- create note -----#
	if Note.objects.filter(removed=True).count() > 500:			
		note_obj_list = Note.objects.filter(removed=True)
		note_obj = random.choice(note_obj_list)
		note_obj.notebook = notebook_obj
		note_obj.article = article_obj
		note_obj.image = image_obj
		note_obj.note_type = note_type
		note_obj.title = title
		note_obj.note_full_path = note_full_path
		note_obj.date_created = datetime.datetime.now()
		note_obj.date_modified = datetime.datetime.now()
		note_obj.public = public
		note_obj.language = language
		note_obj.keywords = keywords
		note_obj.keywords_machine = ''
		note_obj.removed = False					
		note_obj.save()
		current_note = note_obj
	else:
		new_note = Note(
		notebook = notebook_obj,
		article = article_obj,
		image = image_obj,
		note_type = note_type,
		title = title,
		note_full_path = note_full_path,
		date_created = datetime.datetime.now(),
		date_modified = datetime.datetime.now(),
		public = public,
		language = language,
		keywords = keywords,
		keywords_machine = '',
		removed = False)
		new_note.save()
		current_note = new_note

#----------------------------------------------------------------------------------------#

def create_notebook_note(notebook_obj, note_obj):
	new_notebook_note = Notebook_Note(
	notebook = notebook_obj,
	note = note_obj,
	can_admin = True,
	can_see = True,
	can_edit = True,
	is_author = True,
	removed = False)
	new_notebook_note.save()

#----------------------------------------------------------------------------------------#
		
def image_upload(request,notebook_obj):
	is_image = False
	docfile = request.FILES['docfile']
	fullfileName, fileExtension = os.path.splitext(docfile.name)
	fileName = os.path.basename(docfile.name)	
	#----- create unique url -----#
	url = create_unique_image_url(fullfileName)
	#----- create new image object -----#
	new_image = Image(
	notebook = notebook_obj,
	docfile=request.FILES['docfile'],
	url = url,
	name = fileName,
	format = fileExtension,
	size = request.FILES['docfile'].size, 
	width = 100,
	height = 100,
	removed = False)
	new_image.save()
	#----- check file is an image -----#
	image_obj = Image.objects.get(url=url)
	path = image_obj.docfile.path
	path_to_media = settings.MEDIA_ROOT
	dir = path_to_media + 'users/' + notebook_obj.url + '/uploaded_files/'
	fileName = path.replace(dir,'')
	try:
		i=img_pil.open(dir + fileName)
		fileExtension = '.' + i.format
		width, height = i.size
		image_obj.format = fileExtension
		image_obj.width = width
		image_obj.height = height	
		is_image = True
	except:
		is_image = False		
	#----- create images -----#
	if is_image:
		image_obj.save()
		current_obj = image_obj
		#----- change file name for unique url
		fileName = fileName.replace(' ','\ ')
		command = 'mv '+ dir + fileName + ' ' + dir + url + fileExtension
		os.system(command)
		#----- move image in the main directory
		command = 'mv '+ dir + url + fileExtension + ' ' + path_to_media + 'images/src/'
		os.system(command)
		#----- thumbnails 500 by 500 -----#	
		im = img_pil.open(path_to_media + 'images/src/' + url + fileExtension)
		im_size = im.size		
		thumb = path_to_media + 'images/thumbnails_500_500/'
		size = (500,500)
		im.thumbnail(size, img_pil.ANTIALIAS)
		im_size = im.size
		new_im = img_pil.new('RGB', (500,500), (0,0,0))
		x = int( (500 - im_size[0]) / 2.0 )
		y = int( (500 - im_size[1]) / 2.0 )
		try:
			new_im.paste(im, (x,y), mask=im.split()[3])
		except:
			new_im.paste(im, (x,y))		
		new_im.save(thumb + url + fileExtension)
		#----- thumbnails 1000 by 1000 -----#
		new_im = img_pil.open(path_to_media + 'images/src/' + url + fileExtension)
		thumb = path_to_media + 'images/thumbnails_1000_1000/'
		size = (1000,1000)
		new_im.thumbnail(size, img_pil.ANTIALIAS)
		new_im.save(thumb + url + fileExtension)
		#----- create note -----#			
		note_type = 'image'
		public = int(request.POST['public'])	
		content = request.POST['content']
		keywords = request.POST['tags']
		language = 0
		fc.create_new_note(notebook_obj, note_type, current_obj, public, keywords, language)
		note_obj = Note.objects.get(image=image_obj, note_type='image')
		note_obj.abstract = content
		note_obj.save()
		#----- create note keywords -----#
		fc.create_note_keywords(note_obj)
		#----- create notebook note -----#	
		fc.create_notebook_note(notebook_obj,note_obj)	
	else:
		fileName = fileName.replace(' ','\ ')
		os.system('rm ' + dir + fileName )
		image_obj.notebook = None
		image_obj.removed = True
		image_obj.save()
	#----- return -----#	
	return image_obj, is_image

#----------------------------------------------------------------------------------------#
		
def image_replace(request,notebook_obj,note_obj,image_obj):
	previous_image_format = image_obj.format
	previous_image_docfile = image_obj.docfile
	is_image = False
	docfile = request.FILES['docfile']
	fullfileName, fileExtension = os.path.splitext(docfile.name)
	fileName = os.path.basename(docfile.name)	
	url = image_obj.url
	#----- upload image -----#
	image_obj.docfile=request.FILES['docfile']
	image_obj.save()
	#----- check if file is an image -----#
	path = image_obj.docfile.path
	path_to_media = settings.MEDIA_ROOT
	dir = path_to_media + 'users/' + notebook_obj.url + '/uploaded_files/'
	fileName = path.replace(dir,'')
	try:
		i=img_pil.open(dir + fileName)
		fileExtension = '.' + i.format
		width, height = i.size
		image_obj.format = fileExtension
		image_obj.width = width
		image_obj.height = height	
		is_image = True
	except:
		is_image = False		
	#----- create images -----#
	if is_image:
		image_obj.save()
		#----- remove previous images -----#
		command = 'rm ' + (path_to_media + 'images/src/' + image_obj.url + previous_image_format)
		os.system(command)
		command = 'rm ' + (path_to_media + 'images/thumbnails_500_500/' + image_obj.url + previous_image_format)
		os.system(command)
		command = 'rm ' + (path_to_media + 'images/thumbnails_1000_1000/' + image_obj.url + previous_image_format)
		os.system(command)	
		#----- change file name for unique url
		fileName = fileName.replace(' ','\ ')
		command = 'mv '+ dir + fileName + ' ' + dir + url + fileExtension
		os.system(command)
		#----- move image in the main directory
		command = 'mv '+ dir + url + fileExtension + ' ' + path_to_media + 'images/src/'
		os.system(command)
		#----- thumbnails 500 by 500 -----#	
		im = img_pil.open(path_to_media + 'images/src/' + url + fileExtension)
		im_size = im.size		
		thumb = path_to_media + 'images/thumbnails_500_500/'
		size = (500,500)
		im.thumbnail(size, img_pil.ANTIALIAS)
		im_size = im.size
		new_im = img_pil.new('RGB', (500,500), (0,0,0))
		x = int( (500 - im_size[0]) / 2.0 )
		y = int( (500 - im_size[1]) / 2.0 )
		try:
			new_im.paste(im, (x,y), mask=im.split()[3])
		except:
			new_im.paste(im, (x,y))		
		new_im.save(thumb + url + fileExtension)
		#----- thumbnails 1000 by 1000 -----#
		new_im = img_pil.open(path_to_media + 'images/src/' + url + fileExtension)
		thumb = path_to_media + 'images/thumbnails_1000_1000/'
		size = (1000,1000)
		new_im.thumbnail(size, img_pil.ANTIALIAS)
		new_im.save(thumb + url + fileExtension)
		#----- update note -----#			
		note_obj.date_created = datetime.datetime.now()
		note_obj.date_modified = datetime.datetime.now()
		note_obj.save()
	else:
		fileName = fileName.replace(' ','\ ')
		os.system('rm ' + dir + fileName )
	#----- return -----#	
	return is_image

#----------------------------------------------------------------------------------------#

def create_note_keywords(note_obj):
	process_key_words = False
	#----- note type: article -----#
	if note_obj.note_type == 'article': 
		article_obj = note_obj.article
		keywords = note_obj.notebook.user.first_name + ' ' + \
				   note_obj.notebook.user.last_name + ' ' + \
				   article_obj.title + ' ' + note_obj.keywords  				
		process_key_words = True
	#----- note type: image -----#
	if note_obj.note_type == 'image': 
		keywords = note_obj.notebook.user.first_name + ' ' + \
		           note_obj.notebook.user.last_name + ' ' + \
		           note_obj.keywords 				
		note_link_obj_list = Note_Link.objects.filter(note_02=note_obj,removed=False)
		process_key_words = True
	#----- create keywords machine -----#	
	if process_key_words:
		keywords_process = create_keywords_machine(keywords)
		if note_obj.note_type == 'image': 
			for note_link_obj in note_link_obj_list:
				keywords_process = keywords_process + ' ' + note_link_obj.note_01.keywords_machine
		#----- update note -----#
		note_obj.keywords_machine = keywords_process
		note_obj.save()

#----------------------------------------------------------------------------------------#
	
def create_keywords_machine(keywords):
	keywords_list = keywords.split()				
	keywords_process_list = []
	for word in keywords_list:
		keywords_process_list.append(word)
		#----- lowercase -----#
		lowercase_word = word.lower()
		if not lowercase_word in keywords_process_list:
			keywords_process_list.append(lowercase_word)
		#----- remove accentuated word -----#
		word_no_accents = ''.join((c for c in unicodedata.normalize('NFD', word) if unicodedata.category(c) != 'Mn'))
		if not word_no_accents in keywords_process_list:
			keywords_process_list.append(word_no_accents)
		#----- remove accentuated word & lowercase -----#					
		lowercase_word = word_no_accents.lower()
		if not lowercase_word in keywords_process_list:
			keywords_process_list.append(lowercase_word)
	keywords_process = ' '.join(keywords_process_list)	
	return keywords_process	

#----------------------------------------------------------------------------------------#	

def remove_note(note_obj):	
	#----- remove article -----#
	if note_obj.article != None: 
		article_obj = note_obj.article
		article_obj.removed = True
		article_obj.save()
	#----- remove image -----#
	if note_obj.image != None: 
		image_obj = note_obj.image
		image_obj.removed = True
		image_obj.save()
	#----- remove article - photo links -----#		
	note_link_obj_list = Note_Link.objects.filter(note_01=note_obj) | Note_Link.objects.filter(note_02=note_obj)
	for note_link_obj in note_link_obj_list:
		note_link_obj.removed = True
		note_link_obj.save()	
	#----- remove note -----# 
	note_obj.removed = True
	note_obj.save()		