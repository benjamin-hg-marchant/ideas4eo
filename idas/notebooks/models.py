from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime 

import random # HoneyPot
import string # HoneyPot

def uploaded_file_path(instance,filename):
	return '/'.join(['users',instance.notebook.url,'uploaded_files',filename])

def notebook_uploaded_file_path(instance,filename):
	return '/'.join(['users',instance.url,'uploaded_files',filename])
	
def group_uploaded_file_path(instance,filename):
	return '/'.join(['groups',instance.url,'uploaded_files',filename])	

class Notebook(models.Model):
	user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
	url = models.TextField(unique=True)
	notebook_type = models.IntegerField(null=True)	#--- removed
	date_created = models.DateTimeField(default=datetime.now)	
	account_active = models.BooleanField(default=True) 
	account_blocked = models.BooleanField(default=False) 
	last_activity_date = models.DateTimeField(default=datetime.now) 
	docfile = models.FileField(upload_to=notebook_uploaded_file_path, blank=True) 
	profile_picture = models.BooleanField(default=False) 
	header_img_file = models.FileField(upload_to=notebook_uploaded_file_path, blank=True) 
	header_img = models.BooleanField(default=False) 	
	display_full_name = models.BooleanField(default=False)
	display_about_button = models.BooleanField(default=False) 
	full_name = models.CharField(max_length=200,default='')
	middle_name = models.CharField(max_length=100,default='')
	pseudo_changed = models.DateTimeField(default=datetime.now)
	country = models.IntegerField(null=True)
	sex = models.IntegerField(null=True)
	date_of_birth = models.DateTimeField(default=datetime.now)
	language = models.CharField(max_length=4)	
	phone = models.IntegerField(null=True)	
	isced_level = models.IntegerField(null=True)	
	content = models.TextField()
	content_formatted = models.TextField()
	abstract = models.TextField() 
	abstract_formatted = models.TextField()
	content_fr = models.TextField()
	content_fr_formatted = models.TextField()
	abstract_fr = models.TextField() 
	abstract_fr_formatted = models.TextField()
	security_questions = models.BooleanField(default=False) 
	security_question_1_idx = models.IntegerField(null=True)
	security_question_1 = models.TextField()  
	security_question_2_idx = models.IntegerField(null=True)
	security_question_2 = models.TextField() 
	security_question_3_idx = models.IntegerField(null=True) 
	security_question_3 = models.TextField()  
	nb_public_photos = models.IntegerField(default=0)  
	key_words = models.TextField() 
	key_words_machine = models.TextField() 
	removed = models.BooleanField(default=False)  

class Notebook_Stats(models.Model):
	notebook = models.ForeignKey(Notebook, null=True, blank=True, default = None,on_delete=models.DO_NOTHING)
	notes_count = models.IntegerField(null=True)
	article_count = models.IntegerField(null=True)
	image_count = models.IntegerField(null=True)
	file_count = models.IntegerField(null=True)
	code_count = models.IntegerField(null=True)
	visitor_weekly_count = models.IntegerField(null=True)
	removed = models.BooleanField(default=False)  

class Article(models.Model):
	notebook = models.ForeignKey(Notebook, null=True, blank=True, default = None,on_delete=models.DO_NOTHING) 
	url = models.CharField(max_length=1000, unique=True)
	title = models.CharField(max_length=1000)	
	content = models.TextField()
	content_formatted = models.TextField() 
	article_url_link_list = models.TextField()
	image_url_link_list = models.TextField()
	file_url_link_list = models.TextField()
	video_url_link_list = models.TextField()
	nb_public_photos = models.IntegerField(default=0)
	removed = models.BooleanField(default=False) 

class Image(models.Model):
	notebook = models.ForeignKey(Notebook, null=True, blank=True, default = None,on_delete=models.DO_NOTHING)
	docfile = models.FileField(upload_to=uploaded_file_path)
	url = models.CharField(max_length=1000, unique=True)
	name = models.CharField(max_length=500) 
	format = models.CharField(max_length=500)
	size = models.IntegerField(null=True)
	width = models.IntegerField(null=True)
	height = models.IntegerField(null=True)
	timestamp = models.CharField(max_length=1000, default='')
	removed = models.BooleanField(default=False)

class Note(models.Model):
	notebook = models.ForeignKey(Notebook, null=True, blank=True, default = None,on_delete=models.DO_NOTHING) 
	article = models.ForeignKey(Article, null=True, blank=True, default = None,on_delete=models.DO_NOTHING) 
	image = models.ForeignKey(Image, null=True, blank=True, default = None,on_delete=models.DO_NOTHING) 
	note_type = models.CharField(max_length=500)
	title = models.CharField(max_length=1000) 
	note_full_path = models.TextField()
	date_created = models.DateTimeField(default=datetime.now) 
	date_modified = models.DateTimeField(default=datetime.now) 
	public = models.BooleanField(default=True)
	language = models.CharField(max_length=4)
	abstract = models.TextField(default = '')
	abstract_formatted = models.TextField(default = '') 
	comments_counts = models.IntegerField(null=True)
	comments = models.BooleanField(default=True)
	comments_blocked = models.BooleanField(default=False)
	nb_views = models.IntegerField(null=True, default = 0)
	keywords = models.TextField()
	keywords_machine = models.TextField()
	removed = models.BooleanField(default=False) 

class Notebook_Note(models.Model): 
	notebook = models.ForeignKey(Notebook, null=True, blank=True, default = None,on_delete=models.DO_NOTHING) 
	note = models.ForeignKey(Note, null=True, blank=True, default = None,on_delete=models.DO_NOTHING) 
	can_admin = models.BooleanField(default=False) 
	can_see = models.BooleanField(default=True)
	can_edit = models.BooleanField(default=True)
	is_author = models.BooleanField(default=False) 
	date_created = models.DateTimeField(default=datetime.now) 
	removed = models.BooleanField(default=False)  

class Note_Link(models.Model): 
	notebook = models.ForeignKey(Notebook, null=True, blank=True, default = None,on_delete=models.DO_NOTHING) 
	note_01 = models.ForeignKey(Note, null=True, blank=True, default = None, related_name='note_01',on_delete=models.DO_NOTHING) 
	note_02 = models.ForeignKey(Note, null=True, blank=True, default = None, related_name='note_02',on_delete=models.DO_NOTHING)
	removed = models.BooleanField(default=False) 

#----------------------------------------------------------------------------------------#
# Forms

choices_list = [('0','0'),('1','1'),('2','2'),('3','3'),
                ('4','4'),('5','5'),('6','6'),('7','7'),
                ('8','8'),('9','9'),('10','10'),('11','11'),
                ('12','12'),('13','13'),('14','14'),('15','15')]

class UserCreateForm(UserCreationForm):
    #----- Add extra fields -----#
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")
    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user	
    #----- Add Honey Pots -----#
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        # Add honeypots
        self.honeypot_fieldnames = "address", "phone"
        self.honeypot_class = ''.join(random.choice(string.ascii_uppercase + string.digits) for __ in range(10))
        self.honeypot_jsfunction = 'f'+''.join(random.choice(string.ascii_uppercase + string.digits) for __ in range(10))
        for fieldname in self.honeypot_fieldnames:
            self.fields[fieldname] = forms.CharField(
                widget=forms.TextInput(attrs={'class': self.honeypot_class}),
                required=False,)
    def clean(self):
        cd = self.cleaned_data
        for fieldname in self.honeypot_fieldnames:
            if cd[fieldname]: raise forms.ValidationError("Thank you, non-human visitor. Please keep trying to fill in the form.")
        return cd

class Article_Create_Form(forms.Form):
	title = forms.CharField(max_length=500)
	license = forms.ChoiceField(choices=choices_list, widget=forms.RadioSelect(),required=False, initial=0)
	public = forms.ChoiceField(choices=choices_list, widget=forms.RadioSelect(),required=False, initial=1)
	content = forms.CharField(required=False)
	tags = forms.CharField(max_length=500,required=False)	

class Article_Edit_Form(forms.Form):
	title = forms.CharField(max_length=500)
	public = forms.ChoiceField(choices=choices_list, widget=forms.RadioSelect(),required=False)
	comments = forms.ChoiceField(choices=choices_list, widget=forms.RadioSelect(),required=False, initial=1)
	language = forms.ChoiceField(choices=choices_list, widget=forms.RadioSelect(),required=False)
	content = forms.CharField(required=False)
	tags = forms.CharField(max_length=500,required=False)	

class Image_Upload_Form(forms.Form):
	docfile = forms.FileField(label='Select a file', help_text='max. 42 megabytes',required=False)
	license = forms.ChoiceField(choices=choices_list, widget=forms.RadioSelect(),required=False, initial=3)
	public = forms.ChoiceField(choices=choices_list, widget=forms.RadioSelect(),required=False, initial=1)
	content = forms.CharField(required=False)
	tags = forms.CharField(max_length=500,required=False,initial='')

class Link_Form(forms.Form):
	url = forms.CharField(required=True)

class Note_Remove_Form(forms.Form):
	remove_text = forms.CharField(max_length=500,required=True)
	
class Note_Search_Form(forms.Form):
	note_keywords = forms.CharField(required=False)
	note_type = forms.ChoiceField(choices=[('note','All Notes'), ('article','Article'),('image','Image'),('code','Code'),('file','File'),('course','Course'), ('quiz','quiz'), ('coding project','Coding Projects'), ('project','Research Projects')], widget=forms.RadioSelect(), required=False, initial=('note','All Notes'))
	note_can_see = forms.ChoiceField(choices=choices_list, widget=forms.RadioSelect(), required=False, initial=0)	