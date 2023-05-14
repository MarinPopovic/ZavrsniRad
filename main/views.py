from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from .forms import *
import pyrebase

# Create your views here.

config={
  "apiKey": "AIzaSyAb3kFcqaffBQLvmPrAYJ3bEJ6aGj2mv1I",
  "authDomain": "zavrsnirad-d6160.firebaseapp.com",
  "databaseURL": "https://zavrsnirad-d6160-default-rtdb.firebaseio.com",
  "projectId": "zavrsnirad-d6160",
  "storageBucket": "zavrsnirad-d6160.appspot.com",
  "messagingSenderId": "805104473425",
  "appId": "1:805104473425:web:54db2c6cb5499e12fd2f70"
}

firebase=pyrebase.initialize_app(config)
authe=firebase.auth()
database=firebase.database()

def index(request):
    # Get a list of keys in the Knjige node
    keys=database.child('Knjige').shallow().get().val()
    
    # Create an empty list to store the data
    books=[]
    
    # Loop through the keys and retrieve the data from each attribute in 'Knjige'
    for key in keys:
        book=database.child('Knjige').child(key).get().val()
        
        # Join the values in the 'Genre' array with a comma and space separator
        book['Genre']=', '.join(book['Genre'])
        
        books.append(book)
        
    # Sort the books by ID
    books.sort(key=lambda x: int(x['ID']))
       
    # Get the user ID from the session variable
    uid = request.session.get('uid')

    if uid:
       # Check if the logged-in user is a superuser (admin)
       is_superuser = database.child('Superusers').child(uid).get().val()
       
       if is_superuser:
         # Retrieve the superuser data from the Firebase's database
         superuser_data = database.child('Superusers').child(uid).get().val() 
        
         # Pass the superuser's username to the index.html page
         username = superuser_data.get('username')
         context = {"books": books, "username": username, "uid": uid, "is_superuser": is_superuser}
         return render(request, 'index.html', context)
     
       else: 
         # Retrieve the regular user data from the Firebase's database
         user_data = database.child('Users').child(uid).get().val()
    
         # Pass the user's username to the index.html page
         username = user_data.get('username')
         context = {"books": books, "username": username, "uid": uid}
         return render(request, 'index.html', context)
    else:
       context = {"books": books}
       return render(request, 'index.html', context)

def register(request):
    if request.method == 'POST':
        
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        # Check if the password and password confirmation match
        if password != password2:
            error = "Polja za lozinku i potvrdu zaporke se ne podudaraju."
            return render(request, 'user/register.html', {'error': error})

        try:
            # Create the user using Firebase authentication
            user = authe.create_user_with_email_and_password(email, password)
            uid=user['localId']
        except pyrebase.exceptions.EmailAlreadyExistsError:
            error = "Email adresa već postoji."
            return render(request, 'user/register.html', {'error': error})
        except pyrebase.exceptions.RequestsConnectionError:
            error = "Došlo je do pogreške prilikom registracije vašeg računa. Molimo pokušajte ponovno."
            return render(request, 'user/register.html', {'error': error})
        
        # Add the user data to the Firebase's database with an empty wishlist and borrowed list
        data = {"username": username, "email": email, "wishlist": ["Empty"], "borrowed": ["Empty"]}
        database.child("Users").child(uid).set(data)

        # Redirect to the login page after successful registration
        return redirect('main:login')
    else:
        return render(request, 'user/register.html')

def register_superuser(request):
    if request.method == 'POST':
        
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        # Check if the password and password confirmation match
        if password != password2:
            error = "Polja za lozinku i potvrdu zaporke se ne podudaraju."
            return render(request, 'user/register.html', {'error': error})

        try:
            # Create the user using Firebase authentication
            user = authe.create_user_with_email_and_password(email, password)
            uid=user['localId']
        except pyrebase.exceptions.EmailAlreadyExistsError:
            error = "Email adresa već postoji."
            return render(request, 'user/register_superuser.html', {'error': error})
        except pyrebase.exceptions.RequestsConnectionError:
            error = "Došlo je do pogreške prilikom registracije vašeg računa. Molimo pokušajte ponovno."
            return render(request, 'user/register_superuser.html', {'error': error})
        
        # Add the superuser data to the Firebase's database
        superuser_data = {"username": username, "email": email}
        database.child("Superusers").child(uid).set(superuser_data)

        # Redirect to the login page after successful registration
        return redirect('main:login')
    else:
        return render(request, 'user/register_superuser.html')

def login(request):
 if request.method == 'POST':
    
    email = request.POST.get('email')
    password = request.POST.get('password')
    
    try:
        # Authenticate the user using Firebase authentication
        user = authe.sign_in_with_email_and_password(email, password)
    except:
        error = "Netočna email adresa ili loznika. Molimo pokušajte ponovno."
        return render(request, 'login.html', {'error': error})
    
    # Save the user ID as a session variable
    request.session['uid'] = user['localId']

    # Redirect to the index page after successful login
    return redirect('main:index')
 else:
    return render(request, 'user/login.html')

def logout(request):
    # Remove the user ID from the session
    del request.session['uid']

    # Redirect to the login page after successful logout
    return redirect('main:index')

def admin_page(request):
    uid = request.session.get('uid')
    
    is_superuser = database.child('Superusers').child(uid).get().val()
    
    if not is_superuser:
        return HttpResponse(status=403)
    
    # Get all users from the Firebase database
    users = database.child("Users").get()
    
    # Empty list to store user data
    user_data = []
    
    # Loop through the user data and get email, username, and UID for each user
    for user in users.each():
        uid = user.key()
        email = user.val()['email']
        username = user.val()['username']
        user_data.append({"uid": uid, "email": email, "username": username})
        
    context = {'user_data': user_data, 'is_superuser': is_superuser, 'uid': uid}
    return render(request, 'admin_page.html', context)

def delete_account(request):
    if request.method == 'POST':
        # Get the UID of the user to be deleted from the POST request
        uid = request.POST['uid']
        
        try:
            # Delete the user data from the Firebase database
            database.child("Users").child(uid).remove()
            
            # Redirect to the admin page with a success message
            messages.success(request, 'Korisnički račun je uspješno izbrisan.')
            return redirect('main:admin-page')
        
        except:
            # Redirect to the admin page with an error message if there is an error deleting the user
            messages.error(request, 'Greška pri brisanju korisničkog računa.')
            return redirect('main:admin-page')

def user_page(request):
    # Get the user's uid from the session
    uid = request.session.get('uid')
    
    # Retrieve the user data from the Firebase's database
    user_data = database.child('Users').child(uid).get().val()
    
    username = user_data.get('username')

    # Retrieve the wishlist of the user
    wishlist = user_data.get('wishlist', [])
    
    # Retrieve the borrowed book list of the user
    borrowed_list = user_data.get('borrowed', [])
    
    # If the wishlist contains the 'Empty' element, display a message
    if wishlist == ['Empty']:
        wishlist_empty = "Your wishlist is empty"
    else:
        wishlist_empty = ""
        
    # If the borrow list contains the 'Empty' element, display a message
    if borrowed_list == ['Empty']:
        borrowed_list_empty = "Your borrow list is empty"
    else:
        borrowed_list_empty = ""

    # Retrieve the data for the books in the wishlist
    books = []
    for book_id in wishlist:
        book_data = database.child('Knjige').child(book_id).get().val()
        books.append(book_data)
       
    # Retrieve the data for the books in the borrowed list    
    books_2 = []        
    for book_id in borrowed_list:
        book_data = database.child('Knjige').child(book_id).get().val()
        books_2.append(book_data)

    context = {'uid': uid, 'username': username, 'books': books, 'books_2': books_2, 'wishlist_empty': wishlist_empty, 
               'borrowed_list_empty':borrowed_list_empty}
    return render(request, 'user/user_page.html', context)
  
def book_show(request, knjiga_id):   
    # Retrieve the data for the specified book
    book=database.child('Knjige').child(knjiga_id).get().val()
    
    book['Genre'] = ', '.join(book['Genre'])
    
    uid = request.session.get('uid')

    if uid:
       # Check if the logged-in user is a superuser
       is_superuser = database.child('Superusers').child(uid).get().val()
       
       if is_superuser:
         # Retrieve the superuser data from the Firebase's database
         superuser_data = database.child('Superusers').child(uid).get().val() 
        
         username = superuser_data.get('username')
         context = {"book": book, "knjiga_id": knjiga_id, "is_superuser":is_superuser, "username": username, "uid": uid}
         return render(request, 'book_show.html', context)
     
       else: 
         # Retrieve the user data from the Firebase's database
         user_data = database.child('Users').child(uid).get().val()
         
         # Check if the book is in the user's wishlist
         wishlist = user_data.get('wishlist', [])
         is_on_wishlist = knjiga_id in wishlist
         
         # Check if the book is in the user's borrowed list
         borrowed_list = user_data.get('borrowed', [])
         is_borrowed = knjiga_id in borrowed_list
    
         username = user_data.get('username')
         context = {"book": book, "knjiga_id": knjiga_id, "username": username, "uid": uid, "is_on_wishlist": is_on_wishlist, "is_borrowed": is_borrowed}
         return render(request, 'book_show.html', context)
    else:
       context = {"book": book, "knjiga_id": knjiga_id} 
       return render(request, 'book_show.html', context)

def upload(request):
    
    uid = request.session.get('uid')
    
    is_superuser = database.child('Superusers').child(uid).get().val()
    
    if not is_superuser:
        return HttpResponse(status=403)
    
    username = is_superuser.get('username')
    
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            data = {
                'ID': form.cleaned_data['ID'],
                'Title': form.cleaned_data['Title'],
                'Author': form.cleaned_data['Author'],
                'Publisher': form.cleaned_data['Publisher'] if not form.cleaned_data['No_publisher'] else "No publisher",
                'Genre': form.cleaned_data['Genre'].split(', '),
                'Country': form.cleaned_data['Country'],
                'Print length': form.cleaned_data['Print_length'],
                'Year': form.cleaned_data['Year'],
                'Kolicina': form.cleaned_data['Kolicina'],
                'Description': form.cleaned_data['Description'],
            }
            database.child('Knjige').child(str(data['ID'])).set(data)
            return redirect('main:index')
    else:
        form = BookForm()
    
    context = {'form': form, 'username': username, 'uid': uid, 'is_superuser': is_superuser}
    return render(request, 'unos.html', context)

def update_book(request, knjiga_id):
    
    uid = request.session.get('uid')
    
    is_superuser = database.child('Superusers').child(uid).get().val()
    
    if not is_superuser:
        return HttpResponse(status=403)
    
    username = is_superuser.get('username')
    
    # Retrieve the data for the specified book
    book=database.child('Knjige').child(knjiga_id).get().val()

    if request.method == 'POST':
        form = BookFormUpdate(request.POST)
        if form.is_valid():
            # Retrieve the genre data as a string from the form
            genre_string = form.cleaned_data['Genre']
            
            # Convert the genre string into a list
            genre_list = genre_string.split(', ')
            
            # Update the book data in the database
            data = form.cleaned_data
            data['Genre'] = genre_list
            database.child('Knjige').child(knjiga_id).update(form.cleaned_data)
            return redirect('main:index')
    else:
        # Populate the form with the current book data
        form = BookFormUpdate(initial=book)

    context = {'form': form, 'username': username, 'uid': uid, 'is_superuser': is_superuser}
    return render(request, 'update_book.html', context)

def delete_book(request, knjiga_id):
    uid = request.session.get('uid')
    
    is_superuser = database.child('Superusers').child(uid).get().val()

    if not is_superuser:
        return HttpResponse(status=403)
    
    # Remove the book data from the database
    database.child('Knjige').child(knjiga_id).remove()
    return redirect('main:index')

def add_to_wishlist(request, knjiga_id):
    uid = request.session.get('uid')

    # Get the current wishlist for the user
    wishlist = database.child('Users').child(uid).child('wishlist').get().val()

    # If the wishlist is empty, remove the "Empty" item
    if wishlist == ['Empty']:
        database.child('Users').child(uid).child('wishlist').remove()
        wishlist = []
        
    # Check if the book is already in the wishlist
    if knjiga_id in wishlist:
        # Book already in wishlist, so don't add it again
        return redirect('main:user')

    # Retrieve the data for the specified book
    book = database.child('Knjige').child(knjiga_id).get().val()

    # Add the book to the wishlist
    wishlist.append(knjiga_id)
    database.child('Users').child(uid).child('wishlist').set(wishlist)

    # Redirect to the user page
    return redirect('main:user')

def remove_from_wishlist(request):
    if request.method == 'POST':
        uid = request.session.get('uid')
        
        # Retrieve the user data from the Firebase's database
        user_data = database.child('Users').child(uid).get().val()
        
        # Retrieve the wishlist of the user
        wishlist = user_data.get('wishlist', [])

        # Remove the book ID from the wishlist
        book_id = request.POST.get('book_id')
        if book_id in wishlist:
            wishlist.remove(book_id)
                    
        # Check if the wishlist is now empty
        if not wishlist:
            # Add the "Empty" item back to the borrowed list
            wishlist.append('Empty')
            
        # Update the wishlist in the Firebase's database    
        database.child('Users').child(uid).child('wishlist').set(wishlist)    
        
        # Redirect to the user page
        return redirect('main:user')

def borrow_book(request, knjiga_id):
    uid = request.session.get('uid')

    # Get the current borrowed books and wishlist for the user
    borrowed_books = database.child('Users').child(uid).child('borrowed').get().val()
    wishlist = database.child('Users').child(uid).child('wishlist').get().val()

    # If the borrowed books list is empty, remove the "Empty" item
    if borrowed_books == ['Empty']:
        database.child('Users').child(uid).child('borrowed').remove()
        borrowed_books = []

    # Check if the book is already borrowed by the user
    if knjiga_id in borrowed_books:
        # Book already borrowed by the user, so don't add it again
        return redirect('main:user')

    # Retrieve the data for the specified book
    book = database.child('Knjige').child(knjiga_id).get().val()

    # Decrease the quantity of the book by 1
    quantity = book.get('Kolicina')
    if quantity > 0:
        quantity -= 1
        database.child('Knjige').child(knjiga_id).child('Kolicina').set(quantity)
    else:
        # Book not available for borrowing
        return redirect('main:user')

    # Add the book to the borrowed books list
    borrowed_books.append(knjiga_id)
    database.child('Users').child(uid).child('borrowed').set(borrowed_books)

    # Set the wishlist of the user without the book that was borrowed
    if knjiga_id in wishlist:
        wishlist.remove(knjiga_id)
        if not wishlist:
            # Add the "Empty" item back to the wishlist if it is now empty
            wishlist.append('Empty')
        database.child('Users').child(uid).child('wishlist').set(wishlist)

    # Redirect to the user page
    return redirect('main:user')

def return_book(request):
    if request.method == 'POST':
        uid = request.session.get('uid')
        
        # Retrieve the user data from the Firebase's database
        user_data = database.child('Users').child(uid).get().val()
        
        # Retrieve the wishlist of the user
        borrowed_books = user_data.get('borrowed', [])

        # Remove the book ID from the wishlist
        book_id = request.POST.get('book_id')
        if book_id in borrowed_books:
            borrowed_books.remove(book_id)
            
            book = database.child('Knjige').child(book_id).get().val()
            quantity = book.get('Kolicina')
            quantity += 1
            database.child('Knjige').child(book_id).child('Kolicina').set(quantity)
        
        # Check if the borrowed list is now empty
        if not borrowed_books:
            # Add the "Empty" item back to the borrowed list
            borrowed_books.append('Empty')
        
        # Update the borrowed list in the Firebase's database   
        database.child('Users').child(uid).child('borrowed').set(borrowed_books)
        
        # Redirect to the user page
        return redirect('main:user')
    
def book_search(request):   
    if request.method == 'GET':
        uid = request.session.get('uid')
        is_superuser = database.child('Superusers').child(uid).get().val()
        
        search_term = request.GET['search_term']
        search_type = request.GET['search_type']
        books = []
        keys = database.child('Knjige').shallow().get().val()
        for key in keys:
            book = database.child('Knjige').child(key).get().val()
            if search_type == 'title' and search_term.lower() in book['Title'].lower():
                book['Genre'] = ', '.join(book['Genre'])
                books.append(book)
            elif search_type == 'author' and search_term.lower() in book['Author'].lower():
                book['Genre'] = ', '.join(book['Genre'])
                books.append(book)
        books.sort(key=lambda x: int(x['ID']))
        if search_type == 'title':
            url = reverse('main:book-search') + '?title=' + search_term
            context = {'books': books, 'search_term': search_term, 'uid': uid, 'url': url, 'is_superuser': is_superuser}
            return render(request, 'search/book_search.html', context)
        elif search_type == 'author':
            url = reverse('main:book-author-search') + '?author=' + search_term
            context = {'books': books, 'search_term': search_term, 'uid': uid, 'url': url, 'is_superuser': is_superuser}
            return render(request, 'search/book_author_search.html', context)
    else:
        return render(request, 'search/book_search.html')
    
def book_author_search(request):
    if request.method == 'POST':
        search_term = request.POST['search_book']
        books = []
        keys = database.child('Knjige').shallow().get().val()
        for key in keys:
            book = database.child('Knjige').child(key).get().val()
            if search_term.lower() in book['Author'].lower():
                book['Genre'] = ', '.join(book['Genre'])
                books.append(book)
        books.sort(key=lambda x: int(x['ID']))
        return render(request, 'search/book_search.html', {'books': books, 'search_term': search_term})
    else:
        return render(request, 'book_search.html')

def books_by_author(request, author):
   
    keys = database.child('Knjige').shallow().get().val()

    books = []

    for key in keys:
        book = database.child('Knjige').child(key).get().val()
        
        book['Genre']=', '.join(book['Genre'])
        
        # Check if the book is written by the author
        if book['Author'] == author:
            books.append(book)

    # Sort the books list by ID
    books.sort(key=lambda x: int(x['ID']))
    
    uid = request.session.get('uid')

    if uid:
       # Check if the logged-in user is a superuser
       is_superuser = database.child('Superusers').child(uid).get().val()
       
       if is_superuser:
         # Retrieve the superuser data from the Firebase's database
         superuser_data = database.child('Superusers').child(uid).get().val() 
         username = superuser_data.get('username')
         context = {'author': author, 'books': books, 'uid': uid, 'username': username, 'is_superuser': is_superuser}
         return render(request, 'books_by/books_by_author.html', context)
     
       else: 
         # Retrieve the user data from the Firebase's database
         user_data = database.child('Users').child(uid).get().val()
         username = user_data.get('username')
         context = {'author': author, 'books': books, 'uid': uid, 'username': username}
         return render(request, 'books_by/books_by_author.html', context)
    else:
        context = {'author': author, 'books': books}
        return render(request, 'books_by/books_by_author.html', context)
    
def books_by_publisher(request, publisher):    
    keys=database.child('Knjige').shallow().get().val()
    
    # Create empty list to store the data
    books=[]
    
    # Loop through the keys and retrieve the data from each node
    for key in keys:
        book=database.child('Knjige').child(key).get().val()
        
        # Join the values in the 'Genre' array with a comma and space separator
        book['Genre']=', '.join(book['Genre'])
        
        # Check if the book's publisher matches the selected publisher
        if book['Publisher'] == publisher:
            books.append(book)
        
    # Sort the books list by ID
    books.sort(key=lambda x: int(x['ID']))
    
    uid = request.session.get('uid')

    if uid:
       # Check if the logged-in user is a superuser
       is_superuser = database.child('Superusers').child(uid).get().val()
       
       if is_superuser:
         # Retrieve the superuser data from the Firebase's database
         superuser_data = database.child('Superusers').child(uid).get().val() 
         username = superuser_data.get('username')
         context = {'publisher': publisher, 'books': books, 'uid': uid, 'username' :username, 'is_superuser': is_superuser}   
         return render(request, 'books_by/books_by_publisher.html', context)
     
       else: 
         # Retrieve the user data from the Firebase's database
         user_data = database.child('Users').child(uid).get().val()
         username = user_data.get('username')
         context = {'publisher': publisher, 'books': books, 'uid': uid, 'username' :username}
         return render(request, 'books_by/books_by_author.html', context)
    else:
        context = {'publisher': publisher, 'books': books}
        return render(request, 'books_by/books_by_author.html', context)
    
def books_by_genre(request, genre):
    # Query the database for all books that contain the given genre
    books = []
    keys = database.child('Knjige').shallow().get().val()
    for key in keys:
        book = database.child('Knjige').child(key).get().val()
        if genre in book['Genre']:
            book['Genre'] = ', '.join(book['Genre'])
            books.append(book)
    
    # Sort the books list by ID
    books.sort(key=lambda x: int(x['ID']))
    
    return render(request, 'books_by/books_by_genre.html', {'genre': genre, 'books': books})