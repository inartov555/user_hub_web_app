The *.po files need to be compiled to *.mo files, so the localization is read.
To do it, run the command from below (add more -l $locale if there are multiple languages)

django-admin compilemessages -l et_EE -l en_US

or

python manage.py compilemessages -l et -l en
