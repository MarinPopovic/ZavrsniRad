from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
import datetime
import os #upload image
from .forms import *
import pyrebase
import firebase_admin
from firebase_admin import credentials, auth
import tempfile

# Create your views here.

# Initialize Firebase Admin SDK
#This is used for updating the email adress in the Firebase's Authentication page
cred = credentials.Certificate("./main/zavrsnirad-d6160-firebase-adminsdk-c68do-afe21305d5.json")
firebase_admin.initialize_app(cred)

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
storage = firebase.storage()

def index(request):
    # Get a list of keys in the Knjige node
    keys=database.child('Knjige').shallow().get().val()
    
    # Create an empty list to store the data
    books=[]
    
    # Loop through the keys and retrieve the data from each attribute in 'Knjige'
    for key in keys:
        book=database.child('Knjige').child(key).get().val()  
        
        # Retrieve the publisher data from the "Publishers" node
        publisher_id = book.get('PublisherID')
        publisher = database.child('Publishers').child(publisher_id).child('Publisher').get().val()
        
        # Replace the "PublisherID" with the retrieved "Publisher" value
        book['Publisher'] = publisher
        
        # Retrieve the author data from the "Authors" node
        author_id = book.get('AuthorID')
        author = database.child('Authors').child(author_id).child('Author').get().val()
        
        # Replace the "AuthorsID" with the retrieved "Authors" value
        book['Author'] = author
              
        books.append(book)
      
    # Sort the books by ID
    books.sort(key=lambda x: int(x['ID']))
    
    # Paginate the books list
    paginator = Paginator(books, 50)  # 50 books per page
    page = request.GET.get('page')

    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, show the first page
        books = paginator.page(1)
    except EmptyPage:
        # If the page is out of range, show the last page
        books = paginator.page(paginator.num_pages)
       
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
            messages.error(request, "Polja za lozinku i potvrdu zaporke se ne podudaraju.")
            return render(request, 'user/register.html')

        try:
            # Create the user using Firebase authentication
            user = authe.create_user_with_email_and_password(email, password)
            uid=user['localId']
        except:
            # Check if the email already exists in the Users node
            users = database.child("Users").get()
            for user in users.each():
                if user.val()["email"] == email:
                    messages.error(request, "Email adresa već postoji.")
                    return render(request, 'user/register.html')
        
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
            messages.error(request, "Polja za lozinku i potvrdu zaporke se ne podudaraju.")
            return render(request, 'user/register_superuser.html')

        try:
            # Create the user using Firebase authentication
            user = authe.create_user_with_email_and_password(email, password)
            uid=user['localId']
        except pyrebase.exceptions.EmailAlreadyExistsError:
            # Check if the email already exists in the Users node
            users = database.child("Superusers").get()
            for user in users.each():
                if user.val()["email"] == email:
                    messages.error(request, "Email adresa već postoji.")
                    return render(request, 'user/register_superuser.html')
        
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
    
    # Check if the user's email exists in the "DeletedUsers" node
    deleted_users = database.child('DeletedUsers').get()
    for user in deleted_users.each():
        if user.val() == email:
            messages.error(request, 'Ovaj korisnik je obrisan.')
            return render(request, 'user/login.html')
    
    try:
        # Authenticate the user using Firebase authentication
        user = authe.sign_in_with_email_and_password(email, password)
    except:
        messages.error(request, 'Netočna email adresa ili loznika. Molimo pokušajte ponovno.')
        return render(request, 'user/login.html')
    
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

def settings_main_page(request):
    uid = request.session.get('uid')
    
    is_superuser = database.child('Superusers').child(uid).get().val()
    
    if is_superuser:
        user_data = database.child("Superusers").child(uid).get().val()
    else:
        user_data = database.child("Users").child(uid).get().val()
    
    username = user_data['username']
    email = user_data['email']
    
    # Censor email
    local_part, domain = email.split('@')
    censored_email = local_part[0] + '***' + local_part[-1] + '@' + domain[0] + '***' + domain[-1]
    
    context = {'username': username, 'email': censored_email, 'uid': uid, 'is_superuser': is_superuser}
    return render(request, 'settings/settings_main_page.html', context)

def change_username(request):
    if request.method == 'POST':
        new_username = request.POST.get('new_username')
        password = request.POST.get('password')
        
        # Get the user's UID from the session variable
        uid = request.session.get('uid')
        
        try:
            # Retrieve the user's email from the database
            # Check if the user is a regular user or an admin (superuser) 
            is_superuser = database.child('Superusers').child(uid).get().val()
            if is_superuser:
                user_data = database.child("Superusers").child(uid).get().val()
            else:
                user_data = database.child("Users").child(uid).get().val()   
                    
            email = user_data['email']
            
            # Re-authenticate the user using Firebase authentication
            user = authe.sign_in_with_email_and_password(email, password)
                     
            if is_superuser:
                user_type = 'Superusers'
            else:
                user_type = 'Users'
            
            # Update the username in the appropriate node in the Firebase's database
            database.child(user_type).child(uid).update({"username": new_username})
            
            # Redirect to the settings page with a success message
            messages.success(request, 'Korisničko ime je uspješno promijenjeno.')
            return render(request, 'settings/change_username.html', {'uid': uid, 'is_superuser': is_superuser})
        
        except:
            messages.error(request, 'Pogrešna lozinka ili greška prilikom promjene korisničkog imena. Molim te pokušaj ponovno.')
            return render(request, 'settings/change_username.html', {'uid': uid, 'is_superuser': is_superuser})

    else:
        uid = request.session.get('uid')
        if uid:
         # Check if the logged-in user is a superuser
         is_superuser = database.child('Superusers').child(uid).get().val()
        return render(request, 'settings/change_username.html', {'uid': uid, 'is_superuser': is_superuser})

def change_email(request):
    if request.method == 'POST':
        new_email = request.POST.get('new_email')
        password = request.POST.get('password')
        
        # Get the user's UID from the session variable
        uid = request.session.get('uid')
        
        try:
            # Retrieve the user's email from the database
            # Check if the user is a regular user or an admin (superuser) 
            is_superuser = database.child('Superusers').child(uid).get().val()
            if is_superuser:
                user_data = database.child("Superusers").child(uid).get().val()
            else:
                user_data = database.child("Users").child(uid).get().val() 
                
            email = user_data['email']
            
            # Re-authenticate the user using Firebase authentication
            user = authe.sign_in_with_email_and_password(email, password)
        
            if is_superuser:
                user_type = 'Superusers'
            else:
                user_type = 'Users'
                
            # Update the email in the Firebase's database
            database.child(user_type).child(uid).update({"email": new_email})
            
            # Update the email in Firebase Authentication
            user = auth.update_user(uid, email=new_email)
            
            # Redirect to the settings page with a success message
            messages.success(request, 'Email je uspješno promijenjen.')
            return render(request, 'settings/change_email.html', {'uid': uid, 'is_superuser': is_superuser})
        except:
            messages.error(request,"Pogrešna lozinka ili greška prilikom promjene emaila. Molimo pokušajte ponovno.")
            return render(request, 'settings/change_email.html', {'uid': uid, 'is_superuser': is_superuser})      

    else:
        uid = request.session.get('uid')
        if uid:
         # Check if the logged-in user is a superuser
         is_superuser = database.child('Superusers').child(uid).get().val()
        return render(request, 'settings/change_email.html', {'uid': uid, 'is_superuser': is_superuser})

def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        
        # Get the user's UID from the session variable
        uid = request.session.get('uid')
        
        try:
            # Retrieve the user's email from the database
            # Check if the user is a regular user or an admin (superuser) 
            is_superuser = database.child('Superusers').child(uid).get().val()
            if is_superuser:
                user_data = database.child("Superusers").child(uid).get().val()
            else:
                user_data = database.child("Users").child(uid).get().val() 
                
            email = user_data['email']
            
            # Re-authenticate the user using Firebase authentication
            user = authe.sign_in_with_email_and_password(email, current_password)
            
            # Update the password in Firebase Authentication
            auth.update_user(uid, password=new_password)
            
            # Redirect to the settings page with a success message
            messages.success(request, "Lozinka je uspješno promijenjena.") 
            return render(request, 'settings/change_password.html', {'uid': uid, 'is_superuser': is_superuser})
        
        except:
            messages.error(request, "Pogrešna trenutna lozinka ili greška tijekom promjene lozinke. Molimo pokušajte ponovno.")
            return render(request, 'settings/change_password.html', {'uid': uid, 'is_superuser': is_superuser})
    
    else:
        uid = request.session.get('uid')
        if uid:
         # Check if the logged-in user is a superuser
         is_superuser = database.child('Superusers').child(uid).get().val()
        return render(request, 'settings/change_password.html', {'uid': uid, 'is_superuser': is_superuser})

def delete_account(request):
    uid = request.session.get('uid')
    
    try:
        # Delete the user's account from Firebase Authentication
        auth.delete_user(uid)
    except:
        # Handle any errors that occur during account deletion
        error = "An error occurred while deleting your account. Please try again."
        return render(request, 'settings/settings_main_page.html', {'error': error})
    
    # Remove the user data from the Firebase Realtime Database
    database.child("Users").child(uid).remove()
    
    # Clear the user ID from the session
    del request.session['uid']
       
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
        
    approve_data = database.child("Approve_book_return").get()

    # Empty list to store data from "Approve_book_return"
    approve_list = []
    
    # Loop through the approve data and get book_id and user_email for each item
    for approve in approve_data.each():
       if approve.val() is None:
        continue 
        
       book_id = approve.val()['book_id']
       user_email = approve.val()['user_email']
       date_requested_return = approve.val()['date_requested_return']
       
       if book_id == -1:
          continue
      
       book_data = database.child('Knjige').child(book_id).get().val()
       book_title = book_data.get('Title')
       
       approve_list.append({"book_id": book_id, "user_email": user_email,
                            "date_requested_return": date_requested_return, "random_string": approve.key(),
                            "book_title": book_title})
        
    context = {'user_data': user_data, 'is_superuser': is_superuser, 'uid': uid, 'approve_list': approve_list}
    return render(request, 'admin_page.html', context)

def approve_book_return(request, random_string):    
    database.child('Approve_book_return').child(random_string).remove()
    return redirect('main:admin-page')
    
def delete_user_account(request, uid):
    if request.method == 'POST':
        # Get the email of the user to be deleted
        user_email = database.child('Users').child(uid).child('email').get().val()
        
        # Store the email in the 'DeletedUsers' node
        database.child('DeletedUsers').push(user_email)

        # Delete the user from the 'Users' node
        database.child('Users').child(uid).remove()
        
    return redirect('main:admin-page')

def user_page(request):
    # Get the user's uid from the session
    uid = request.session.get('uid')
    
    is_superuser = database.child('Superusers').child(uid).get().val()

    if is_superuser:
        return HttpResponse(status=403)
    
    # Retrieve the user data from the Firebase's database
    user_data = database.child('Users').child(uid).get().val()
    
    username = user_data.get('username')
    user_email = user_data.get('email')

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
        
    # Retrieve the data for the books awaiting return approval
    approve_data = database.child("Approve_book_return").get()
    approve_list = []
    for approve in approve_data.each():
        if approve.val() is None:
            continue

        book_id = approve.val().get('book_id')
        current_user = approve.val().get('user_email')

        if book_id == -1:
            continue

        book_data = database.child('Knjige').child(book_id).get().val()
        book_title = book_data.get('Title')
        
        if current_user == user_email:
         approve_list.append({
            "book_id": book_id,
            "book_title": book_title,
            "user_email": current_user,
            "random_string": approve.key(),       
         })

    context = {'uid': uid, 'username': username, 'books': books, 'books_2': books_2, 
               'wishlist_empty': wishlist_empty, 'borrowed_list_empty':borrowed_list_empty, 
               'approve_list': approve_list, 'is_superuser': is_superuser}
    return render(request, 'user/user_page.html', context)
  
def book_show(request, knjiga_id):   
    # Retrieve the data for the specified book
    book=database.child('Knjige').child(knjiga_id).get().val()
    
    # Retrieve the publisher ID from the book data
    publisher_id = book.get('PublisherID')
    
    # Retrieve the publisher data from the "Publishers" node
    publisher_data = database.child('Publishers').child(publisher_id).get().val()

    # Extract the publisher name from the fetched data
    publisher_name = publisher_data.get('Publisher')

    # Update the book dictionary with the publisher name
    book['Publisher'] = publisher_name
    
    author_id = book.get('AuthorID')
    author_data = database.child('Authors').child(author_id).get().val()
    author_name = author_data.get('Author')
    book['Author'] = author_name
    
    book['Genre'] = ', '.join(book['Genre'])
    
    # Retrieve the image path of the author from the "Authors" node
    image_path = author_data.get('Image')
    
    # Get the download URL for the author image from Firebase Storage
    image_url = storage.child(image_path).get_url(None)
    
    uid = request.session.get('uid')

    if uid:
       # Check if the logged-in user is a superuser
       is_superuser = database.child('Superusers').child(uid).get().val()
       
       if is_superuser:
         # Retrieve the superuser data from the Firebase's database
         superuser_data = database.child('Superusers').child(uid).get().val() 
        
         username = superuser_data.get('username')
         context = {"book": book, "knjiga_id": knjiga_id, "is_superuser":is_superuser, "username": username, 
                    "uid": uid, "image_url": image_url}
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

         # Check if the user has reached the maximum borrowing limit
         is_max_limit_reached = len(borrowed_list) >= 5
    
         username = user_data.get('username')
         context = {"book": book, "knjiga_id": knjiga_id, "username": username, "uid": uid, "is_on_wishlist": is_on_wishlist, 
                    "is_borrowed": is_borrowed, "is_max_limit_reached": is_max_limit_reached, "image_url": image_url}
         return render(request, 'book_show.html', context)
    else:
       context = {"book": book, "knjiga_id": knjiga_id, "image_url": image_url} 
       return render(request, 'book_show.html', context)

def upload(request):
    uid = request.session.get('uid')

    is_superuser = database.child('Superusers').child(uid).get().val()

    if not is_superuser:
        return HttpResponse(status=403)

    username = is_superuser.get('username')

    publishers = database.child('Publishers').get().val()  # Retrieve all publishers from the database
    authors = database.child('Authors').get().val()  # Retrieve all authors from the database

    if request.method == 'POST':
        form = BookForm(request.POST, publishers=publishers, authors=authors)
        if form.is_valid():
            data = {
                'Title': form.cleaned_data['Title'],
                'AuthorID': form.cleaned_data['Author'],
                'PublisherID': form.cleaned_data['Publisher'],
                'Genre': form.cleaned_data['Genre'].split(', '),
                'Country': form.cleaned_data['Country'],
                'Print_length': form.cleaned_data['Print_length'],
                'Year': form.cleaned_data['Year'],
                'Quantity': form.cleaned_data['Quantity'],
                'Description': form.cleaned_data['Description'],
            }
            
            # Assign "NULL" to fields that are not required
            if data['Country'] == '':
                data['Country'] = 'NULL'
            if data['Year'] is None:
                data['Year'] = 'NULL'
            if data['Description'] == '':
                data['Description'] = 'NULL'
            
            books_count = database.child('Knjige').get().each()
            next_id = len(books_count) if books_count else 0
            data['ID'] = next_id
            
            database.child('Knjige').child(str(next_id)).set(data)
            messages.success(request, 'Upload successful.')
            return redirect('main:upload-book')
        else:
            messages.error(request, 'Upload unsuccessful.')
    else:
        form = BookForm(publishers=publishers, authors=authors)

    context = {'form': form, 'username': username, 'uid': uid, 'is_superuser': is_superuser}
    return render(request, 'upload/upload_book.html', context)

def upload_publisher(request):
    uid = request.session.get('uid')
    
    is_superuser = database.child('Superusers').child(uid).get().val()
    
    if not is_superuser:
        return HttpResponse(status=403)
    
    username = is_superuser.get('username')
    
    if request.method == 'POST':
        form = PublisherForm(request.POST)
        if form.is_valid():            
            publisher_data = {             
                #'PublisherID': form.cleaned_data['PublisherID'],
                'Publisher': form.cleaned_data['Publisher'],
            }
            
            publisher_count = database.child('Publishers').get().each()
            next_id = len(publisher_count) if publisher_count else 0
            publisher_data['PublisherID'] = next_id
            
            database.child('Publishers').child(str(next_id)).set(publisher_data)
            
            messages.success(request, 'Upload successful.')
            
            return redirect('main:upload-publisher')
        else:
            messages.error(request, 'Error. Upload was not successful.')
    else:
        form = PublisherForm()
    
    context = {'form': form, 'username': username, 'uid': uid, 'is_superuser': is_superuser}
    return render(request, 'upload/upload_publisher.html', context)

def upload_author(request):
    uid = request.session.get('uid')
    
    is_superuser = database.child('Superusers').child(uid).get().val()
    
    if not is_superuser:
        return HttpResponse(status=403)
    
    username = is_superuser.get('username')
    
    if request.method == 'POST':
        form = AuthorForm(request.POST, request.FILES)
        if form.is_valid():
            author_data = {             
                'Author': form.cleaned_data['Author'],
            }
            image = request.FILES['Image']
            
            image_path = f"authors/{image.name}" #Get image path
            
            author_count = database.child('Authors').get().each()
            next_id = len(author_count) if author_count else 0
            author_data['AuthorID'] = next_id
            
            # Upload image to storage
            try:
                storage.child(image_path).put(image)
                messages.success(request, "Upload successful")
            except:
                messages.error(request, "Upload unsuccessful")
                return redirect(reverse('upload-author'))
            
            # Update author data with image path
            author_data['Image'] = image_path
            
            # Store author data in the database
            database.child('Authors').child(str(next_id)).set(author_data)
        else:
            messages.error(request, "Form is invalid")
    else:
        form = AuthorForm()
    
    context = {'form': form, 'username': username, 'uid': uid, 'is_superuser': is_superuser}
    return render(request, 'upload/upload_author.html', context)

def update_publisher(request):
    uid = request.session.get('uid')
    is_superuser = database.child('Superusers').child(uid).get().val()

    if not is_superuser:
        return HttpResponse(status=403)

    username = is_superuser.get('username')

    publishers = database.child('Publishers').get().val()

    if request.method == 'POST':
        form = UpdatePublisherForm(request.POST, publishers=publishers)
        if form.is_valid():
            publisher_id = form.cleaned_data['Publisher']
            new_publisher_name = form.cleaned_data['NewPublisherName']

            # Update the publisher data
            publisher_data = {
                'Publisher': new_publisher_name,
            }
            database.child('Publishers').child(str(publisher_id)).update(publisher_data)

            messages.success(request, 'Ažuriranje je uspijelo.')

            # Redirect to the current page
            return redirect(request.path)
        else:
            # Add an error message
            messages.error(request, 'Greška! Ažuriranje nije uspijelo')
    else:
        form = UpdatePublisherForm(publishers=publishers)

    context = {'form': form, 'publishers': publishers, 'username': username, 'uid': uid, 'is_superuser': is_superuser}
    return render(request, 'update/update_publisher.html', context)

def update_author(request):
    uid = request.session.get('uid')
    is_superuser = database.child('Superusers').child(uid).get().val()

    if not is_superuser:
        return HttpResponse(status=403)

    username = is_superuser.get('username')

    authors = database.child('Authors').get().val()

    if request.method == 'POST':
        form = UpdateAuthorForm(request.POST, request.FILES, authors=authors)
        if form.is_valid():
            author_id = form.cleaned_data['Author']
            new_author_name = form.cleaned_data['NewAuthorName']
            new_image = form.cleaned_data['Image']
            
            # Update the author data
            author_data = {
                'Author': new_author_name,
            }
            
            # Check if a new image is uploaded
            if new_image:
                # Generate a temporary file to store the new image
                with tempfile.NamedTemporaryFile(delete=True) as temp_image:
                    temp_image.write(new_image.read())
                    temp_image.flush()
                    
                    # Upload the new image to storage
                    image_path = f"authors/{new_image.name}"
                    try:
                        storage.child(image_path).put(temp_image.name)
                        messages.success(request, "Ažuriranje slike je uspijelo")
                    except:
                        messages.error(request, "Ažuriranje slike nije uspijelo")
                        return redirect(reverse('update-author'))
                    
                    # Update the author's image path
                    author_data['Image'] = image_path

            database.child('Authors').child(str(author_id)).update(author_data)

            messages.success(request, 'Ažuriranje je uspijelo.')

            # Redirect to the current page
            return redirect(request.path)
        else:
            # Add an error message
            messages.error(request, 'Greška! Ažuriranje nije uspijelo.')
    else:
        form = UpdateAuthorForm(authors=authors)

    context = {'form': form, 'authors': authors, 'username': username, 'uid': uid, 'is_superuser': is_superuser}
    return render(request, 'update/update_author.html', context)

def delete_publisher(request):
    uid = request.session.get('uid')
    is_superuser = database.child('Superusers').child(uid).get().val()

    if not is_superuser:
        return HttpResponse(status=403)

    username = is_superuser.get('username')

    #publishers = database.child('Publishers').get().val()

    if request.method == 'POST':
        form = DeletePublisherForm(request.POST)
        if form.is_valid():
            publisher_id = form.cleaned_data['PublisherID']

            # Check if the publisher exists
            publisher_exists = database.child('Publishers').child(str(publisher_id)).get().val()

            if publisher_exists:
                # Delete the publisher
                database.child('Publishers').child(str(publisher_id)).remove()

                # Update the books assigned to the deleted publisher
                books = database.child('Knjige').get().each()  # Retrieve books as a list

                for book in books:
                    book_key = book.key()
                    book_value = book.val()

                    if book_value.get('PublisherID') == publisher_id:
                        # Update the PublisherID value to 2 for books assigned to the deleted publisher
                        database.child('Knjige').child(book_key).update({'PublisherID': 2})

                messages.success(request, 'Objekt uspješno obrisan.')
            else:
                messages.error(request, 'Greška! Izdavač ne postoji.')

            return redirect(request.path)
        else:
            messages.error(request, 'Greška! Objekt nije obrisan.')
    else:
        form = DeletePublisherForm()

    context = {'form': form, 'username': username, 'uid': uid, 'is_superuser': is_superuser}
    return render(request, 'delete/delete_publisher.html', context)

def delete_author(request):
    uid = request.session.get('uid')
    is_superuser = database.child('Superusers').child(uid).get().val()

    if not is_superuser:
        return HttpResponse(status=403)

    username = is_superuser.get('username')

    #publishers = database.child('Publishers').get().val()

    if request.method == 'POST':
        form = DeleteAuthor(request.POST)
        if form.is_valid():
            author_id = form.cleaned_data['AuthorID']

            # Check if the publisher exists
            author_exists = database.child('Authors').child(str(author_id)).get().val()

            if author_exists:
                # Delete the publisher
                database.child('Authors').child(str(author_id)).remove()

                # Update the books assigned to the deleted author
                books = database.child('Knjige').get().each()  # Retrieve books as a list

                for book in books:
                    book_key = book.key()
                    book_value = book.val()

                    if book_value.get('AuthorID') == author_id:
                        # Update the AuthorID value to 2 for books assigned to the deleted author
                        database.child('Knjige').child(book_key).update({'AuthorID': 2})

                messages.success(request, 'Objekt uspješno obrisan.')
            else:
                messages.error(request, 'Greška! Autor ne postoji.')

            return redirect(request.path)
        else:
            messages.error(request, 'Greška! Objekt nije obrisan.')
    else:
        form = DeleteAuthor()

    context = {'form': form, 'username': username, 'uid': uid, 'is_superuser': is_superuser}
    return render(request, 'delete/delete_author.html', context)

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
        
    # Check if the user has already borrowed the maximum number of books
    if len(borrowed_books) >= 5:
        return redirect('main:user')

    # Check if the book is already borrowed by the user
    if knjiga_id in borrowed_books:
        # Book already borrowed by the user, so don't add it again
        return redirect('main:user')

    # Retrieve the data for the specified book
    book = database.child('Knjige').child(knjiga_id).get().val()

    # Decrease the quantity of the book by 1
    quantity = book.get('Quantity')
    if quantity > 0:
        quantity -= 1
        database.child('Knjige').child(knjiga_id).child('Quantity').set(quantity)
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
            quantity = book.get('Quantity')
            quantity += 1
            database.child('Knjige').child(book_id).child('Quantity').set(quantity)
        
        # Check if the borrowed list is now empty
        if not borrowed_books:
            # Add the "Empty" item back to the borrowed list
            borrowed_books.append('Empty')
        
        # Update the borrowed list in the Firebase's database   
        database.child('Users').child(uid).child('borrowed').set(borrowed_books)
        
        # Add the book ID and user email to the "Approve_book_return" node
        approve_data = {'book_id': book_id, 'user_email': user_data['email'], 
                        'date_requested_return': datetime.datetime.now().strftime('%d-%m-%Y')}
        database.child('Approve_book_return').push(approve_data)
        
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
            
            # Retrieve the publisher ID from the book node
            publisher_id = book.get('PublisherID')
        
            # Retrieve the publisher data from the "Publishers" node using the publisher ID
            publisher_data = database.child('Publishers').child(publisher_id).get().val()
        
            # Get the "Publisher" attribute from the publisher data
            publisher_name = publisher_data.get('Publisher')
        
            # Replace the "PublisherID" with the retrieved "Publisher" value
            book['Publisher'] = publisher_name
            
            author_id = book.get('AuthorID')
            author_data = database.child('Authors').child(author_id).get().val()
            author_name = author_data.get('Author')
            book['Author'] = author_name
            
            if search_type == 'title' and search_term.lower() in book['Title'].lower():
                book['Genre'] = ', '.join(book['Genre'])
                books.append(book)
            elif search_type == 'author' and search_term.lower() in book['Author'].lower():
                book['Genre'] = ', '.join(book['Genre'])
                books.append(book)
            elif search_type == 'publisher' and search_term.lower() in book['Publisher'].lower():
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
        elif search_type == 'publisher':
            url = reverse('main:book-publisher-search') + '?publisher=' + search_term
            context = {'books': books, 'search_term': search_term, 'uid': uid, 'url': url, 'is_superuser': is_superuser}
            return render(request, 'search/book_publisher_search.html', context)
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
        return render(request, 'search/book_search.html')
    
def book_publisher_search(request):
    if request.method == 'POST':
        search_term = request.POST['search_book']
        books = []
        keys = database.child('Knjige').shallow().get().val()
        for key in keys:
            book = database.child('Knjige').child(key).get().val()
            if search_term.lower() in book['Publisher'].lower():
                book['Genre'] = ', '.join(book['Genre'])
                books.append(book)
        books.sort(key=lambda x: int(x['ID']))
        uid = request.session.get('uid')
        return render(request, 'search/book_search.html', {'books': books, 'search_term': search_term, 'uid': uid})
    else:
        return render(request, 'book_search.html')

def books_by_author(request, author):
   
    keys = database.child('Knjige').shallow().get().val()

    books = []

    for key in keys:
        book = database.child('Knjige').child(key).get().val()
        
        book['Genre']=', '.join(book['Genre'])
        
        # Retrieve the publisher ID from the book node
        publisher_id = book.get('PublisherID')
        
        # Retrieve the publisher data from the "Publishers" node using the publisher ID
        publisher_data = database.child('Publishers').child(publisher_id).get().val()
        
        # Get the "Publisher" attribute from the publisher data
        publisher_name = publisher_data.get('Publisher')
        
        # Replace the "PublisherID" with the retrieved "Publisher" value
        book['Publisher'] = publisher_name
        
        author_id = book.get('AuthorID')
        author_data = database.child('Authors').child(author_id).get().val()
        author_name = author_data.get('Author')
        book['Author'] = author_name
        
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
        book = database.child('Knjige').child(key).get().val()
        
        # Join the values in the 'Genre' array with a comma and space separator
        book['Genre'] = ', '.join(book['Genre'])
        
        # Retrieve the publisher ID from the book node
        publisher_id = book.get('PublisherID')
        
        # Retrieve the publisher data from the "Publishers" node using the publisher ID
        publisher_data = database.child('Publishers').child(publisher_id).get().val()
        
        # Get the "Publisher" attribute from the publisher data
        publisher_name = publisher_data.get('Publisher')
        
        # Replace the "PublisherID" with the retrieved "Publisher" value
        book['Publisher'] = publisher_name
        
        author_id = book.get('AuthorID')
        author_data = database.child('Authors').child(author_id).get().val()
        author_name = author_data.get('Author')
        book['Author'] = author_name
        
        # Check if the book's publisher matches the selected publisher
        if publisher_name == publisher:
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
         return render(request, 'books_by/books_by_publisher.html', context)
    else:
        context = {'publisher': publisher, 'books': books}
        return render(request, 'books_by/books_by_publisher.html', context)
    
def books_by_genre(request, genre):
    # Query the Firebase database to retrieve all books with the specified genre
    books = []
    keys = database.child('Knjige').shallow().get().val()
    for key in keys:
        book = database.child('Knjige').child(key).get().val()
        
        # Retrieve the publisher ID from the book node
        publisher_id = book.get('PublisherID')
        
        # Retrieve the publisher data from the "Publishers" node using the publisher ID
        publisher_data = database.child('Publishers').child(publisher_id).get().val()
        
        # Get the "Publisher" attribute from the publisher data
        publisher_name = publisher_data.get('Publisher')
        
        # Replace the "PublisherID" with the retrieved "Publisher" value
        book['Publisher'] = publisher_name
        
        author_id = book.get('AuthorID')
        author_data = database.child('Authors').child(author_id).get().val()
        author_name = author_data.get('Author')
        book['Author'] = author_name
        
        if genre in book['Genre']:
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
         context = {"books": books, "genre": genre, 'uid': uid, 'username' :username, 'is_superuser': is_superuser}   
         return render(request, 'books_by/books_by_genre.html', context)
     
       else: 
         # Retrieve the user data from the Firebase's database
         user_data = database.child('Users').child(uid).get().val()
         username = user_data.get('username')
         context = {"books": books, "genre": genre, 'uid': uid, 'username' :username}
         return render(request, 'books_by/books_by_genre.html', context)
    else:
        context = {"books": books, "genre": genre}
        return render(request, 'books_by/books_by_genre.html', context)