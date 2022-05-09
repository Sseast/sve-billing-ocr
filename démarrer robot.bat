@ECHO OFF
FOR /f %%p in ('where python') do SET PYTHONPATH=%%p

python "T:\INFORMATIQUE\Rex Rotary\Robot Analyse Facture\robot_facture.py"

@pause
