from __future__ import annotations

from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    """Form used on the product detail page to submit a review."""

    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(choices=[(i, f"{i} ★") for i in range(1, 6)]),
            "comment": forms.Textarea(attrs={"rows": 3, "placeholder": "Ваш відгук..."}),
        }
