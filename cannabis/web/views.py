from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from requests import HTTPError
from web.models import *
import uuid

genai.configure(api_key='AIzaSyA1o3HbOLZx25GIy56lzsfBqm2CKoDbp-I')
model = genai.GenerativeModel('gemini-pro')
initalization_prompt="Imagine you are a pharmacist, you will be responsible for listening to patient's issues and creating a solution for them using aryuvedic medicines."
"""safety=[{"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]"""
"""
        HarmCategory.HARM_CATEGORY_VIOLENCE: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DEROGATORY: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_MEDICAL: HarmBlockThreshold.BLOCK_NONE
"""
safety = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
       
    }
history = None
# Create your views here.
def index(request):
    return render(request, "web/index.html")

def about_view(request):
    return render(request, "web/about.html")

def process_view(request):
    return render(request, "web/process.html")

def login_view(request):
    if request.method == "GET":
        return render(request, "web/login.html")
    else:
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return HttpResponseRedirect(reverse("web:dashboard"))
        else:
            # Return an 'invalid login' error message.
            return render(request, "web/login.html", {"Error": "Login Invalid"})


def register(request):
    if request.method == 'POST':
        email = request.POST["email"]
        username = request.POST["username"]
        fname = request.POST["username"]
        lname = request.POST["username"]
        password = request.POST["password"]
        c_password = request.POST["confirm_password"]
        if c_password == password and User.objects.get(username=username).DoesNotExist:
            us = User(username=username, email=email, password=password, first_name=fname, last_name=lname)
            us.save()
            login(request, us)  # Log in the new user
            return HttpResponseRedirect(reverse('web:dashboard'))  # Redirect to homepage after successful registration
        else:
            return render(request, 'web/register.html', {"Error": "Registration Failed"})
    else:
        return render(request, 'web/register.html')



@login_required(login_url='/login')
def logout_view(request):
    logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect(reverse("web:login"))


@login_required(login_url='/login')
def dashboard_view(request):
    if request.method == "GET":
        return render(request, "web/dashboard.html", {"remedies": Solution.objects.filter(for_user=request.user)})

@login_required(login_url='/login')
def new_solution_view(request):
    if request.method == "GET":
        return render(request, "web/newSolution.html")
    else:
        problem = request.POST["question"]
        mod = Problem(problem_statement=problem, from_user=request.user, uuid=uuid.uuid4())
        mod.save()
        lk = model.start_chat(history=[])
        lk.send_message(initalization_prompt, safety_settings=safety)
        xt = lk.send_message("Here is a client's request: \n"+problem+". \n Make some questions for it, only put down the questions and nothing else. Format it as: <question>\n<question>\n<question>. Do not use any markdown. Limit to 3 questions. Do not leave any subtags or markdown in your response.", safety_settings=safety)
        print(xt.text.split("\n"))
        for k in xt.text.split("\n"):
            if k == '':
                continue
            else:
                q = Questions(question_id = uuid.uuid4(), question=k, answer_to_question=None, for_problem_statement = mod)
                q.save()
        history = lk.history
        return HttpResponseRedirect(reverse("web:questions", kwargs={"session_id":mod.uuid}))   

@login_required(login_url='/login')
def questions_view(request, session_id):
    global history
    if request.method == "GET":
        return render(request, "web/questions.html", {
            "questions": Questions.objects.filter(for_problem_statement=Problem.objects.get(uuid=session_id), answer_to_question=None),
            "session": session_id
        })
    else:
        lk = model.start_chat(history=history)
        new_sol = Solution(sol_id = uuid.uuid4(), for_user=request.user, for_problem=Problem.objects.get(uuid=session_id))
        x = Questions.objects.filter(for_problem_statement=Problem.objects.get(uuid=session_id), answer_to_question=None)
        for l in x:
            l.answer_to_question = request.POST[str(l.question_id)]
            l.save()
        xlk = Questions.objects.filter(for_problem_statement=Problem.objects.get(uuid=session_id), answer_to_question=(not None))
        prompt = "Here are the client's responses to the questions you have: \n"
        for kl in xlk:
            prompt += f"{kl.question}\n\n{kl.answer_to_question}"
        prompt += "\n Create a new solution for this client, you have three options: Pill('PIL'), Cigar/Cigarette('CIG'), Chewable('CHE'), Lotion('LOT'). \n You have to pick one of these options. ONLY GIVE THE SHORTHAND AND NOTHING ELSE. "
        
        try:
            final_solution_type = lk.send_message(prompt, safety_settings=safety)
            print(final_solution_type.text)
            new_sol.solution_type = final_solution_type.text
            new_sol.save()    
        except Exception:
            final_solution_type = lk.send_message("This does not meet the requirements, try again. \nYou have three options: Pill('PIL'), Cigar/Cigarette('CIG'), Chewable('CHE'), Lotion('LOT'). \n You have to pick one of these options. ONLY GIVE THE SHORTHAND. " , safety_settings=safety)
            print(final_solution_type.text)
            new_sol.solution_type = final_solution_type.text
            new_sol.save() 
        while True:
            try:
                ck = lk.send_message("Add a quantity of the Product (only give the number and nothing else)", safety_settings=safety)
                print(ck.text)
                new_sol.quantity = int(ck.text.split("\n")[0])
                new_sol.save()
                break
            except Exception:
                #ck = lk.send_message("This does not meet the requirements, try again. (only give the number and nothing else)", safety_settings=safety)
                continue
        while True:
            try:
                lines = lk.send_message("List the various aryuvedic medicines and the amount of it used in the solution. \n Here is an example: \n<aryuvedic-medicine>: <amount in milligrams (Don't include 'mg')>\n<aryuvedic-medicine>: <amount in milligrams (Don't include 'mg')>\n<aryuvedic-medicine>: <amount in milligrams (Don't include 'mg')>", safety_settings=safety)
                print(lines.text)
                for ty in lines.text.split("\n"):
                    name = ty.split(":")[0]
                    milligrams = int(str(ty.split(":")[1]).strip())
                    ck = lk.send_message("Add a description of the Product and its use (only the use and descripiton and nothing else). DONT USE ANY MARKDOWN. ", safety_settings=safety)
                    po = IngredientsOrdered(ingredientName=name, milligrams=milligrams, for_solution=new_sol, description=ck.text)
                    po.save()
                break
            except Exception as e:
                print(e)
                #lines = lk.send_message("This does not meet the requirements, try again. ", safety_settings=safety)
                continue
        return HttpResponseRedirect(reverse("web:solution", kwargs={"solution_id":new_sol.sol_id}))
               

@login_required(login_url='/login')
def solution_view(request, solution_id):
    sol = Solution.objects.get(sol_id=solution_id)
    ing = IngredientsOrdered.objects.filter(for_solution=sol)
    qs = Questions.objects.filter(for_problem_statement=sol.for_problem)
    if request.method == "GET":
        return render(request, "web/solution.html", {"sol": sol, "ing":ing, "q":qs})


@login_required(login_url='/login')
def del_sol_view(request, solution_id):
    sol = Solution.objects.get(sol_id=solution_id).delete()
    return HttpResponseRedirect(reverse("web:dashboard"))
