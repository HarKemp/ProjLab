# ProjLab
Projektēšanas laboratorijas kursa darbs

# Apraksts
Kursa darba apraksts pieejams /Docs/

# Uzstādīšana
## Nepieciešams
* Python 3.12.4 vai jaunāks

# Šim setup vajadzētu strādāt uz visual studio code (Pycharm drošvien līdzīgi)
## 1. Kad noklonē ProjLab github repozitoriju, jāatver terminālis (powershell vai cmd) un jānomaina pašreizējo direktoriju uz `Application`.
## 2. Izveido jaunu virtuālo python vidi:
`python -m venv venv` 
## 3. Aktivizē jauno virtuālo vidi: 
`\venv\Scripts\Activate` <br><br>
Ja komanda nestrādā tad jāizpilda </br>
`Set-ExecutionPolicy RemoteSigned -Scope Process`
vai arī jāizpilda bez sķērsvītras
`venv\Scripts\Activate`</br>
Terminālim jāizskatās apmēram šādi - `(venv) PS C:\Users\Lietotajs\Desktop\ProjLab\ProjLab\Application> `
## 4. Instalē dependencies:
`pip install -r requirements.txt` 
## 5. Konfigurē flask izstrādes vidi:
### Ja caur powershell:
`$env:FLASK_ENV="development"` <br><br>
Pēc tam var pārbaudīt vai pareizi iestatījās ar komandu: `echo $env:FLASK_ENV` 
### Ja caur cmd:
`set FLASK_ENV=development` <br><br>
Pārbauda vai pareizi `echo %FLASK_ENV%`
## 6. Iestata Flask aplikācijas direktoriju
`set FLASK_APP=app` 
## 7. Palaiž web serveri uz localhost: 
`flask run` 
## 8. Pārlūkprogrammā var atvērt:
`http://127.0.0.1:5000` 
## 9. Kad nepieciešams, virtuālo vidi var deaktivizēt (virtuālai videi tehniski jābūt aktivizētai tikai tad, kad veic izmaiņas flask web servera konfigurācijā vai kad to palaiž ar `flask run`):
`deactivate`
