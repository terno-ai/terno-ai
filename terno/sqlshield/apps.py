from django.apps import AppConfig
# from django.core.signals import setting_changed
# from django.core.signals import post_save

# def my_callback(sender, **kwargs):
#     print("Request finished!")

class SqlshieldConfig(AppConfig):
    # default_auto_field = 'django.db.models.BigAutoField'
    name = 'sqlshield'
    # def ready(self):
    #     # print("Ready! And settings up!")
    #     # post_save.connect(my_callback)
    #     # setting_changed.connect(my_callback)
    #     # setting_changed.send(sender=self.__class__, toppings="toppings", setting=AppConfig, size="size")
    #     # from .signals import data_source_changed
    #     pass