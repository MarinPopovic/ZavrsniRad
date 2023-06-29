from django import forms

class BookForm(forms.Form):
    Title = forms.CharField(max_length=70, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Book title'}))
    Author = forms.ChoiceField(choices=[], label='Author')
    Publisher = forms.ChoiceField(choices=[], label='Publisher')
    Genre = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control','placeholder': 'Zanr 1, Zanr 2, Zanr 3, ...'}))
    Country = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Country'}))
    Print_length = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder':'Print length'}))
    Year = forms.IntegerField(min_value=0, required=False, widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'Year'}))
    Quantity = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'Quantity'}))
    Description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','style': 'height: 50px'}))
    
    def __init__(self, *args, **kwargs):
        publishers = kwargs.pop('publishers', None)
        authors = kwargs.pop('authors', None)
        super(BookForm, self).__init__(*args, **kwargs)
        if authors:
            authors = sorted(authors, key=lambda x: x['Author'])  # Sort authors by 'Author' key
            self.fields['Author'].choices = [(author['AuthorID'], author['Author']) for author in authors]
        if publishers:
            publishers = sorted(publishers, key=lambda x: x['Publisher'])  # Sort publishers by 'Publisher' key
            self.fields['Publisher'].choices = [(publisher['PublisherID'], publisher['Publisher']) for publisher in publishers]
            
        #super(BookForm, self).__init__(*args, **kwargs)
    
class PublisherForm(forms.Form):
    Publisher = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Publisher name'}))
    
class AuthorForm(forms.Form):
    Author = forms.CharField(max_length=70, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Author name'}))
    Image = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    
class BookFormUpdate(forms.Form):
    #ID = forms.IntegerField(min_value=0)
    Title = forms.CharField(max_length=70, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Titles'}))
    AuthorID = forms.IntegerField(min_value=0, label='Author ID', widget=forms.NumberInput(attrs={'class': 'form-control','placeholder':'Author ID'}))
    PublisherID = forms.IntegerField(min_value=0, label='Publisher ID', widget=forms.NumberInput(attrs={'class': 'form-control','placeholder':'Publisher ID'}))
    Genre = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Genre'}))
    Country = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Country'}))
    Print_length = forms.IntegerField(min_value=0,  widget=forms.NumberInput(attrs={'class': 'form-control','placeholder':'Print length'}))
    Year = forms.IntegerField(min_value=0, required=False,  widget=forms.NumberInput(attrs={'class': 'form-control','placeholder':'Year'}))
    Quantity = forms.IntegerField(min_value=0,  widget=forms.NumberInput(attrs={'class': 'form-control','placeholder':'Quantity'}))
    Description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'style': 'height: 75px'}))
    
class UpdatePublisherForm(forms.Form):
    Publisher = forms.ChoiceField(choices=[], label='Publisher')
    NewPublisherName = forms.CharField(max_length=50, label='New Publisher Name', widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'New publisher name'}))

    def __init__(self, *args, **kwargs):
        publishers = kwargs.pop('publishers', None)
        super(UpdatePublisherForm, self).__init__(*args, **kwargs)
        if publishers:
            publishers = sorted(publishers, key=lambda x: x['Publisher'])  # Sort publishers by 'Publisher' key
            self.fields['Publisher'].choices = [(publisher['PublisherID'], publisher['Publisher']) for publisher in publishers]

class UpdateAuthorForm(forms.Form):
    Author = forms.ChoiceField(choices=[], label='Author')
    NewAuthorName = forms.CharField(max_length=50, label='New Author Name', widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'New author name'}))
    Image = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        authors = kwargs.pop('authors', None)
        super(UpdateAuthorForm, self).__init__(*args, **kwargs)
        if authors:
            authors = sorted(authors, key=lambda x: x['Author'])  # Sort authors by 'Author' key
            self.fields['Author'].choices = [(author['AuthorID'], author['Author']) for author in authors]  
    
class DeletePublisherForm(forms.Form):
    #PublisherID = forms.ChoiceField(choices=[], label='Publisher')

    #def __init__(self, *args, **kwargs):
    #    publishers = kwargs.pop('publishers', None)
    #    super(DeletePublisherForm, self).__init__(*args, **kwargs)
    #    if publishers:
    #        publishers = sorted(publishers, key=lambda x: x['Publisher'])  # Sort publishers by 'Publisher' key
    #        self.fields['PublisherID'].choices = [(publisher['PublisherID'], publisher['Publisher']) for publisher in publishers]
    PublisherID = forms.IntegerField(min_value=0, label='Publisher ID',  widget=forms.NumberInput(attrs={'class': 'form-control'}))
    
class DeleteAuthor(forms.Form):
    AuthorID = forms.IntegerField(min_value=0, label='Author ID', widget=forms.NumberInput(attrs={'class': 'form-control'}))