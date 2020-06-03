from django import forms

from .models import Invoice

class InvoiceUpdateForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = '__all__'

    def clean_number(self):
        number = self.cleaned_data['number']
        print(number)
        if number in [i.number for i in Invoice.objects.all()]:
            print('validation error')
        return number