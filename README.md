# ProjLab
Projektēšanas laboratorijas kursa darbs

# Apraksts
Kursa darba apraksts pieejams /Docs/

# Uzstādīšana
## Nepieciešams
* Python 3.12.4 vai jaunāks
* Microsoft C++ Build Tools - priekš Greenlet
* poppler-utils - PDF apstrādei
* pytesseract lang packages for Latvian, Estonian, Lithuanian
* .env fails kas satur informāciju par programmatūras darba vidi
```
FLASK_APP=app
FLASK_ENV=development
pytesseract.pytesseract.tesseract_cmd = C:\Program Files\Tesseract-OCR\tesseract.exe
API_KEY=asddasjl1lekj123j21lj3l
PATH_TO_DEFAULT_SERVICE_VALUES_CSV=C:\Program Files\mydata.csv
```
### Tesseract instalācija
* UNIX sistēmām ```sudo apt get install tesseract```
* Windows </br>
sekot instrukcijām no https://stackoverflow.com/questions/50951955/pytesseract-tesseractnotfound-error-tesseract-is-not-installed-or-its-not-i
* Instalēt tesseract no https://github.com/UB-Mannheim/tesseract/wiki
* Pievienot tesseract pie path C:\Users\<lietotājvārds>\AppData\Local\Tesseract-OCR
* ```pip install pytesseract```
* ```pip install tesseract```
* Restart of computer is required
* startējot programmu, kā viens no env mainīgajiem, jānorāda pytesseract.pytesseract.tesseract_cmd</br>
piem. pytesseract.pytesseract.tesseract_cmd = 'C:/OCR/Tesseract-OCR/tesseract.exe'


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


# Konfigurācija background-ocr
### Vispirms izdzēsiet eksistējošo datubāzi no `temp` foldera
### Lai varētu veikt rēķinu apstrādi fonā ir nepieciešama redis datubāze, kura uzglabā pieprasījumus līdz celery ir gatavs tos apstrādāt
### Redis tiešā veidā strādā tikai uz linux, tāpēc ir nepieciešams izmantot wsl vai docker, lai to palaistu - zemāk ir aprakstīti abi varianti

## 1.1 Redis ar WSL
### Tiks aprakstīt, kā uzinstalēt wsl2 (iespējams, ka var izmantot arī wsl1, bet to es nepārbaudīju) - Papildus info par wsl instalāciju: [Microsoft Docs](https://learn.microsoft.com/en-us/windows/wsl/install)
### Atver Powershell un izpilda komandas:
```powershell
wsl --set-default-version 2
wsl --install <<-- šo vajag pildīt tikai tad, ja vēl datorā neesat instalējuši wsl
```

### Gadījumā, ja instalācija iesprūst pie 0% vai ir cita kļūda, wsl var instalēt caur Microsoft Store - meklējat ar search funkciju un izvēlaties kādu ubuntu versiju
### Pagaidiet kamēr uzinstalējas wsl (Ja instalēja caur Microsoft Store, tad iespējams, ka ilgi rādīsies tas 'Intalling, this may take a few minutes' - tādā gadījumā pēc dažām minūtēm var nospiest Ctrl + C un tad mēģināt palaist vēlreiz, šoreiz to var darīt arī no Powershell) - ja tas nepalīdz, iespējami problēmu risinājumi atrodams [Github Issues](https://github.com/microsoft/WSL/issues/6405)
### Iespējams tiks prasīts izveidot lietotāju un paroli (iesaku tos neaizmirst)
### Izpildīt komandas (iegūtas no [Redis docs](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-windows/)):
```powershell
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

sudo apt-get update
sudo apt-get install redis
sudo service redis-server start
redis-cli
```

### Var ievadīt `ping`, lai pārbaudītu vai strādā. Ja atbild `PONG`, tad viss kārtībā.
### Konkrēto termināļa logu var taisīt ciet
### WSL un Redis vajadzētu palaisties pašam katru reizi, kad ieslēdz datoru, bet, ja nē, tad tas būs jāatver izmantojot komandas PowerShell:
```powershell
wsl
sudo service redis-server start
```
Ja nepieciešams, tad apturēt redis var ar komandu:
```
sudo service redis-server stop
```

## 1.2 Redis ar Docker
### Ja lieto docker, tad nepieciešams uzinstalēt docker desktop
### Powershell izpilda komandas:
```powershell
docker pull redis
docker run -d -p 6379:6379 --name redis redis
```
### Ja izlec firewall paziņojums, nospiest Allow Access
### Kad restartēs datoru būs nepieciešams atkārtoti startēt konteineru
```powershell
docker start redis
```

### 2. Tagad var palaist flask kā parasti
### 2.1. Tiem, kam ir env fails vai environment variables iestata manuāli, iespējams, šo soli nevajag pildīt. Man vajadzēja, jo izmantoju Pycharm 
Powershell manuāli iestata API atslēgas "environment variable":
```powershell
$env:API_KEY=GEMINI_AI_API_ATSLEGA
```
### 3. Powershell logā atvērt python virtuālo vidi (venv) un izpildīt komandu:
```powershell
celery -A app.celery_init worker --loglevel=INFO --pool=solo
```
### Šeit būs redzams outputs no celery_utils funkcijām, kas tiks izpildītas apstrādājot konkŗeto rēķinu, kā arī, cik daudz laika tām vajadzēja
### Šo komandu var izpildīt un atstāt, viņa NAV jārestartē katru reizi, kad restartē flask
### Kad beidz darbu, to var apturēt ar Ctrl + C


