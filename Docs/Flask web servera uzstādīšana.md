# Šim setup vajadzētu strādāt uz visual studio code (Pycharm drošvien līdzīgi)
## 1. Kad noklonē ProjLab github repozitoriju, jānomaina pašreizējo direktoriju uz `Application`.
## 2. Izveido jaunu virtuālo python vidi:
`python -m venv venv` 
## 3. Aktivizē jauno virtuālo vidi: 
`\venv\Scripts\Activate` <br>
Terminālim jāizskatās apmēram šādi - `(venv) PS D:\Desktop\ProjLab\ProjLab\Application> `
## 4. Instalē dependencies:
`pip install -r requirements.txt` 
## 5. Konfigurē flask izstrādes vidi (šis ir caur powershell):
`$env:FLASK_ENV="development"` <br>
Pēc tam var pārbaudīt vai pareizi iestatījās ar komandu: `echo $env:FLASK_ENV` 
## 6. Iestata Flask aplikācijas direktoriju
`set FLASK_APP=app` 
## 7. Palaiž web serveri uz localhost: 
`flask run` 
## 8. Pārlūkprogrammā var atvērt:
`http://127.0.0.1:5000` 
## 9. Kad nepieciešams, virtuālo vidi var deaktivizēt (virtuālai videi tehniski jābūt aktivizētai tikai tad, kad veic izmaiņas flask web servera konfigurācijā vai kad to palaiž ar `flask run`):
`deactivate`
