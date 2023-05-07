from django.apps import AppConfig
import os

class MyflopConfig(AppConfig):
    name = 'MyFlOp'

    def ready(self):
        from django.conf import settings as ds

        # STARTUP code
        # Create directory for serving static content in production
        if not os.path.exists(ds.STATIC_ROOT):
        
            # Directory doesn't exist let's create it
            print("Let's create %s" % ds.STATIC_ROOT)
            os.makedirs(ds.STATIC_ROOT,exist_ok=True)
        
        # Create directory for django cache
        if not os.path.exists(ds.CACHE_DIRECTORY):
        
            # Directory doesn't exist let's create it
            print("Let's create %s" % ds.CACHE_DIRECTORY)
            os.makedirs(ds.CACHE_DIRECTORY,exist_ok=True)
        
        # Create tmp directory used for solver resolution
        if not os.path.exists(ds.TMP_DIRECTORY):
        
            # Directory doesn't exist let's create it
            print("Let's create %s" % ds.TMP_DIRECTORY)
            os.makedirs(ds.TMP_DIRECTORY,exist_ok=True)
        
        # Let's create the missing directories
        os.makedirs(os.path.join(ds.TMP_DIRECTORY,"misc/logs/iis"),exist_ok=True)
