from django import forms
from .models import ReviewRating, Product

class ReviewForm(forms.ModelForm):

    class Meta:
        model = ReviewRating
        fields = ['subject', 'review']

class ProductForm(forms.ModelForm):
    gallery_images = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'multiple': True})
    )

    class Meta:
        model = Product
        fields = ['category', 'product_name', 'description', 'price', 'images', 'stock', 'is_available']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
