from django import forms
from .models import Transaccion, Cuenta


class TransaccionForm(forms.ModelForm):
    
    fecha = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',       
            }
        ),
        label='Fecha',
    )

    class Meta:
        model = Transaccion
        fields = ['fecha', 'cuenta', 'categoria', 'descripcion', 'monto']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        
        if user is not None:
            self.fields['cuenta'].queryset = Cuenta.objects.filter(owner=user)

         
        for name, field in self.fields.items():
            css_class = 'form-control'
            if isinstance(field.widget, forms.Select):
                css_class = 'form-select'
            field.widget.attrs.setdefault('class', css_class)
