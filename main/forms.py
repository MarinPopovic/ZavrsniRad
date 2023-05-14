from django import forms

class BookForm(forms.Form):
    ID = forms.IntegerField()
    Title = forms.CharField(max_length=70, widget=forms.TextInput(attrs={'placeholder':'Book title'}))
    Author = forms.CharField(max_length=70, widget=forms.TextInput(attrs={'placeholder':'Full author name'}))
    Publisher = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'placeholder':'Publisher name'}))
    No_publisher = forms.BooleanField(required=False, initial=False, label='No publisher')
    Genre = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Zanr 1, Zanr 2, Zanr 3, ...', 'style': 'width: 200px'}), )
    Country = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder':'Country'}))
    Print_length = forms.IntegerField(min_value=0)
    Year = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'placeholder': 'Year'}))
    Kolicina = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'placeholder': 'Quantity'}))
    Description = forms.CharField(widget=forms.Textarea(attrs={'style': 'height: 50px'}))
    
class BookFormUpdate(forms.Form):
    ID = forms.IntegerField(min_value=0)
    Title = forms.CharField(max_length=70)
    Author = forms.CharField(max_length=70)
    Publisher = forms.CharField(max_length=50, required=False)
    Genre = forms.CharField(max_length=100)
    Country = forms.CharField(max_length=30, required=False)
    Print_length = forms.IntegerField(min_value=0)
    Year = forms.IntegerField(min_value=0, required=False)
    Kolicina = forms.IntegerField(min_value=0)
    Description = forms.CharField(widget=forms.Textarea, required=False)
    
