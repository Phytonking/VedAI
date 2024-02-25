from django.urls import path
from web.views import *

app_name = "web"
urlpatterns = [
    path("", index, name="index"),
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path("register", register, name="register"),
    path("dashboard", dashboard_view, name="dashboard"),
    path("newsolution", new_solution_view, name="newSolution"),
    path("questions/<uuid:session_id>", questions_view, name="questions"),
    path("solution/<uuid:solution_id>", solution_view, name="solution"),
    path("about", about_view, name="about"),
    path("process", process_view, name="process"),
    path("deleteSolution/<uuid:solution_id>", del_sol_view, name="delSol")
]
