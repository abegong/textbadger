from django.conf.urls.defaults import patterns, include, url
from django.views.generic import TemplateView, ListView, DetailView

import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    #Pre-login screens
    url(r'^$', TemplateView.as_view(template_name="home.html")),
    url(r'^sign-in/$', TemplateView.as_view(template_name="sign-in.html")),
    url(r'^about/$', TemplateView.as_view(template_name="about.html")),

    #Object list pages
    url(r'^my-account/$', 'textbadger.tb_app.views.my_account' ),
    url(r'^shared-resources/$', 'textbadger.tb_app.views.shared_resources' ),
    url(r'^administration/$', 'textbadger.tb_app.views.administration' ),

    #Object view pages
    url(r'^codebook/(.*)/$', 'textbadger.tb_app.views.codebook' ),
    #url(r'^collection/(.*)/$', 'textbadger.tb_app.views.collection' ),
    #url(r'^batch/(.*)/$', 'textbadger.tb_app.views.batch' ),

    #Game page(s)
    #!?    url(r'^game/$', 'textbadger.tb_app.views.game' ),

    #Ajax
    url(r'^ajax/sign-in/$', 'tb_app.views.signin'),
    url(r'^sign-out/$', 'tb_app.views.signout'),

    url(r'^ajax/create-account/$', 'tb_app.views.create_account'),
    #url(r'^ajax/save-codebook/$', 'tb_app.views.save_codebook'),

    #url(r'^ajax/create-codebook/$', 'tb_app.views.create_codebook'),
    #url(r'^ajax/save-codebook/$', 'tb_app.views.save_codebook'),

    url(r'^ajax/upload-collection/$', 'tb_app.views.upload_collection'),
    #url(r'^ajax/sample-collection/$', 'tb_app.views.sample_collection'),

    #url(r'^ajax/create-batch/$', 'tb_app.views.create_batch'),
    #url(r'^ajax/update-batch-report/$', 'tb_app.views.update_batch_report'),

    #url(r'^ajax/submit-code/$', 'tb_app.views.submit_code'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)


urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )

