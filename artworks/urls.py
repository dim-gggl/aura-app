from django.urls import path
from . import views

app_name = 'artworks'

urlpatterns = [
    path('', views.artwork_list, name='list'),
    path('create/', views.artwork_create, name='create'),
    path('<uuid:pk>/', views.artwork_detail, name='detail'),
    path('<uuid:pk>/edit/', views.artwork_update, name='update'),
    path('<uuid:pk>/delete/', views.artwork_delete, name='delete'),
    path('<uuid:pk>/export/html/', views.artwork_export_html, name='export_html'),
    path('<uuid:pk>/export/pdf/', views.artwork_export_pdf, name='export_pdf'),
    path('suggestion/', views.random_suggestion, name='random_suggestion'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/<int:pk>/delete/', views.wishlist_delete, name='wishlist_delete'),
    
    # Artists
    path('artists/', views.artist_list, name='artist_list'),
    path('artists/create/', views.artist_create, name='artist_create'),
    path('artists/<int:pk>/', views.artist_detail, name='artist_detail'),
    path('artists/<int:pk>/edit/', views.artist_update, name='artist_update'),
    
    # Collections
    path('collections/', views.collection_list, name='collection_list'),
    path('collections/create/', views.collection_create, name='collection_create'),
    path('collections/<int:pk>/', views.collection_detail, name='collection_detail'),
    path('collections/<int:pk>/edit/', views.collection_update, name='collection_update'),
    
    # Exhibitions
    path('exhibitions/', views.exhibition_list, name='exhibition_list'),
    path('exhibitions/create/', views.exhibition_create, name='exhibition_create'),
    path('exhibitions/<int:pk>/', views.exhibition_detail, name='exhibition_detail'),
    path('exhibitions/<int:pk>/edit/', views.exhibition_update, name='exhibition_update'),
    
    # AJAX endpoints
    path('ajax/artist/create/', views.artist_create_ajax, name='artist_create_ajax'),
    path('ajax/collection/create/', views.collection_create_ajax, name='collection_create_ajax'),
    path('ajax/exhibition/create/', views.exhibition_create_ajax, name='exhibition_create_ajax'),
    path('ajax/arttype/create/', views.arttype_create_ajax, name='arttype_create_ajax'),
    path('ajax/support/create/', views.support_create_ajax, name='support_create_ajax'),
    path('ajax/technique/create/', views.technique_create_ajax, name='technique_create_ajax'),
    path('ajax/keyword/create/',       views.keyword_create_ajax,       name='keyword_create_ajax'),
    path('ajax/keyword/autocomplete/', views.keyword_autocomplete,   name='keyword_autocomplete'),
]
