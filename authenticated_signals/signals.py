from django.db.models.signals import ModelSignal

authenticated_pre_save = ModelSignal(providing_args=["instance", "raw", "using", "update_fields", "request"], use_caching=True)
authenticated_post_save = ModelSignal(providing_args=["instance", "raw", "created", "using", "update_fields", "request"], use_caching=True)
authenticated_save = authenticated_post_save
authenticated_pre_delete = ModelSignal(providing_args=["instance", "using", "request"], use_caching=True)
authenticated_post_delete = ModelSignal(providing_args=["instance", "using", "request"], use_caching=True)
authenticated_delete = authenticated_pre_delete
