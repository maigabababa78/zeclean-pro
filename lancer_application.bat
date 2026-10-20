@echo off
title ZeClean Pro - Gestion Societe de Nettoyage
echo ========================================================
echo   Demarrage de ZeClean Pro (Application Web Django)
echo   URL : http://127.0.0.1:8000
echo ========================================================
start http://127.0.0.1:8000
".venv\Scripts\python.exe" manage.py runserver 0.0.0.0:8000
pause
