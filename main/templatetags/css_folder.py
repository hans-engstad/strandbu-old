from django import template
from strandbu.settings.dev import BASE_DIR, STATIC_URL
#from strandbu.settings.prod import BASE_DIR, STATIC_URL
import os, os.path
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def load_scss():
	scss_common_folder = os.path.join(BASE_DIR, "staticfiles/scss/common")
	scss_home_folder = os.path.join(BASE_DIR, "staticfiles/scss/home")
	
	links = []
	links.append(get_links_from_folder(scss_common_folder, 'scss/common'))
	links.append(get_links_from_folder(scss_home_folder, 'scss/home'))

	print('---------------------------')
	print(links)
	print('---------------------------')

	return links



def get_links_from_folder(folder, static_path):
	files = os.listdir(folder)

	out = []
	for file in files:
		if file != '.DS_Store':
			path = STATIC_URL + static_path + '/' + file
			link = r'<link rel="stylesheet" type="text/x-scss" href="{}" />'.format(path)
			out.append(link)

	return mark_safe("\n".join(out))