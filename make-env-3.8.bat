start /MAX cmd /c "cls && title Prepare Environment && py -3.8 -m venv venv38 && cd venv38/scripts && activate && cd ../.. && python -m pip install --upgrade pip && pip install -r requirements.txt && deactivate && timeout /t 5 /nobreak"
