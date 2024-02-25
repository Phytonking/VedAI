from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Problem(models.Model): # official order made
    uuid = models.UUIDField(null=True)
    from_user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="patient")
    problem_statement = models.TextField()

#solution_type = {"CIG":"Cigar/Cigarette", "PIL":"Pill", "CHE":"Chewables"}
class Solution(models.Model): #medicinal solution
    STATUS_CHOICES = (
        ('PIL', 'Pill'),
        ('CIG', 'Cigar/Cigarette'),
        ('CHE', 'Chewable'),
        ('LOT', 'Lotion')
    )
    pill = 'PIL'
    cigarette = 'CIG'
    chewable = 'CHE'
    lotion = 'LOT'
    sol_id = models.UUIDField(null=True)
    solution_type = models.CharField(max_length=3, choices=STATUS_CHOICES, default=pill)
    quantity = models.IntegerField(null=True)
    for_problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="patient_issue")
    for_user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="patient_user")
    


class IngredientsOrdered(models.Model): #ingredients needed for one solution
    ingredientName = models.TextField()
    milligrams = models.IntegerField()
    for_solution = models.ForeignKey(Solution, on_delete=models.CASCADE, related_name="solution")
    description = models.TextField(null=True)



class Questions(models.Model):
    question_id = models.UUIDField(null=True)
    question = models.TextField()
    answer_to_question = models.TextField(null=True)
    for_problem_statement = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="for_problem")


