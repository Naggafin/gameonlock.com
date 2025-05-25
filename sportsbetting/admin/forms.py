from django import forms

from ..models import Sport


class GenerateTicketForm(forms.Form):
    """Form to select multiple sport and governing body combinations for ticket generation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically generate checkbox fields based on sports and governing bodies
        sports = Sport.objects.prefetch_related("governing_bodies").all()
        for sport in sports:
            choices = [(gb.full_key, gb.name) for gb in sport.governing_bodies.all()]
            if choices:  # Only add field if there are governing bodies
                self.fields[f"sport_{sport.slug_name}"] = forms.MultipleChoiceField(
                    label=sport.name,
                    choices=choices,
                    widget=forms.CheckboxSelectMultiple,
                    required=False,
                )

    def get_selected_keys(self):
        """Return a list of selected sport_governing_body keys."""
        selected = []
        for _, value in self.cleaned_data.items():
            if value:  # If any checkboxes are selected for this sport
                selected.extend(value)
        return selected
