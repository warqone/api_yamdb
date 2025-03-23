from django.db.models import Avg


def get_avg_score(calc_field):
    avg_score = calc_field.reviews.aggregate(Avg('score'))['score__avg']
    calc_field.rating = round(avg_score) if avg_score is not None else None
    calc_field.save(update_fields=['rating'])
