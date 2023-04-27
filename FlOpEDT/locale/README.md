# Internationalization
This folder contains translation files for FlOpEDT.

## How to contribute
If you want to be part of this project by improving translation, please
read the following page on the django documentation : 
[https://docs.djangoproject.com/en/2.1/topics/i18n/translation/]().

TLDR:
After adding new internationalised strings, you have to do the following:
* go in the FlOpEDT folder
* run `django-admin makemessages -l fr`  
It will create the file `FlOpEDT/locale/fr/LC_MESSAGES/django.po`
* Edit this file and translate sentences
* run `django-admin compilemessages`  
It compiles `django.po` to be used by Django.
The resulting file is `django.mo`

Now you can invite your English-speaking friends to enjoy FlOpEDT!

NB The language of the rendered pages is determined by the language of
the browser that launches the request. If you want a uniform language for all
users, go to [the base setting file](../FlOpEDT/settings/base.py),
remove `django.middleware.locale.LocaleMiddleware` from the `MIDLEWARE`
and set the `LANGUAGE_CODE` variable to the right language.
