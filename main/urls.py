from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    
    path('user/', views.user_page, name='user'),
    path('remove_from_wishlist/', views.remove_from_wishlist, name='remove-from-wishlist'),
    path('return_book/', views.return_book, name='return-book'),
    
    path('register/', views.register, name="register"),
    path('register_superuser/', views.register_superuser, name="register_superuser"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name='logout'),
    path('settings/', views.settings_main_page, name="settings-main"),
    path('change_username/', views.change_username, name="change-username"),
    path('change_email/', views.change_email, name="change-email"),
    path('change_password/', views.change_password, name="change-password"),
    path('delete_account/', views.delete_account, name="delete-account"),
    
    path('book_search/', views.book_search, name='book-search'),
    path('book_author_search/', views.book_author_search, name='book-author-search'),
    path('book_publisher_search/', views.book_publisher_search, name='book-publisher-search'),
    
    path('book_show/<knjiga_id>/', views.book_show, name='book-show'),
    path('update_book/<knjiga_id>/', views.update_book, name='update-book'),
    path('delete_book/<knjiga_id>/', views.delete_book, name='delete-book'),
    path('add_to_wishlist/<knjiga_id>/', views.add_to_wishlist, name='add-to-wishlist'),
    path('borrow_book/<knjiga_id>/', views.borrow_book, name='borrow-book'),
    
    path('books_by_author/<author>/', views.books_by_author, name='books-by-author'),
    path('books_by_publisher/<publisher>/', views.books_by_publisher, name='books-by-publisher'),
    path('books_by_genre/<str:genre>/', views.books_by_genre, name='books-by-genre'),
    
    path('admin_page/', views.admin_page, name='admin-page'),
    path('approve_book_return/<str:random_string>/', views.approve_book_return, name='approve-book-return'),
    path('delete_user_account/<str:uid>/', views.delete_user_account, name='delete-user-account'), #Admin deletes user's account
    
    path('upload_book/', views.upload, name="upload-book"),
    path('upload_publisher/', views.upload_publisher, name="upload-publisher"),
    path('update_publisher/', views.update_publisher, name="update-publisher"),
    path('delete_publisher/', views.delete_publisher, name='delete-publisher'),
    path('upload_author/', views.upload_author, name="upload-author"),
    path('update_author/', views.update_author, name="update-author"),
    path('delete_author/', views.delete_author, name='delete-author')
]