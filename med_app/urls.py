from django.urls import path

from med_app.views import *

urlpatterns = [
    path('reports/get_call_questions/', get_call_questions_ajax, name='get_call_questions_ajax'),
    path('api/questions/', get_questions, name='get_questions'),
    # index main page
    path('', index_view, name='index_url'),
    # create med card
    path('create/med/cart/for/user/get/', create_med_cart_get_view, name='create_med_cart_get_url'),
    path('create/med/cart/for/user/post/', create_med_cart_post_view, name='create_med_cart_post_url'),
    # search med card
    path('search/med/card/get/', search_med_card_get_view, name='search_med_card_get_url'),
    path('search/med/card/post/', search_med_card_post_view, name='search_med_card_post_url'),
    # show med card
    path('show/med/card/profile/<int:id>/', med_card_profile_view, name='med_card_profile_url'),
    # create call
    path('create/user/call/get/or/post/<int:med_card_id>/',
         create_call_get_or_post_view,
         name='create_user_call_get_or_post_url'),
    # call detail
    path('call/detail/<int:call_id>/', call_detail_view, name='call_detail_url'),
    # create visit
    path('create/user/visit/get/<int:med_card_id>/', create_visit_get_view,
         name='create_visit_get_url'),
    path('create/user/visit/post/<int:med_card_id>/', create_visit_post_view,
         name='create_visit_post_url'),

    # all med cards
    path('all/med/cards/view/', all_med_cards_view, name='all_med_cards_url'),
    path('call/<int:call_id>/recording/',
         serve_recording_view,  # Используем обновленный view
         name='serve_call_recording_url'),
    # reports
    path('reports/', reports_view, name='reports_url'),
    path('reports/operator/', operator_report_view, name='operator_report_url'),
    path('reports/questions/', questions_report_view, name='questions_report_url'),
    path('reports/visits/', visits_report_view, name='visits_report_url'),

    # analaytics
    path('analytics/', analytics_view, name='analytics_url'),
]
