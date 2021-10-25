# Részletes telepítési útmutató

Útmutató az alapoktól: ha csak most ismerkedsz a Raspberry Pi-jal, kezd az elején.

Ha egyből a lényegre térnél, ugorj ide: [Időjárás figyelő telepítése](TELEPITES.md#időjárás-figyelő-telepítése) 

## Kellékek
### Hardware

* Raspberry Pi mini számítógép
  * A programot a [Raspberry Pi 3B+](https://www.raspberrypi.com/products/raspberry-pi-3-model-b-plus/)
    és [Raspberry Pi 3A](https://www.raspberrypi.com/products/raspberry-pi-3-model-a-plus/) modellekkel teszteltem.
    Minden valószínűség szerint az újabb modellekkel is együtt tud működni, de ha csak égkép-fotózásra  használod,
    bőven elég a fenti két régebbi - és olcsóbb - modell.
* gyári tápegység
* [HQ Camera](https://www.raspberrypi.com/products/raspberry-pi-high-quality-camera/)
  * A jobb felbontás, az alacsonyabb zajszint (éjszakai felvételek esetén), és a cserélhető lencsék miatt esett erre a választásom.
  * Meggyőződésem - bár nem teszteltem - , hogy az olcsóbb [Camera V2](https://www.raspberrypi.com/products/camera-module-v2/)-vel
    is ugyanúgy tud működni a software.
* ["CGL" 6 mm CS-mount objektív](https://www.sparkfun.com/products/16762)
  * A HQ Camera mellett forgalmazott két lencse közül ez a szélesebb látószögő. Saját tapasztalatból, nekem a 
    [16mm-es lencse](https://www.sparkfun.com/products/16761) picit talán élesebb képet, viszont túl szűk képkivágást eredményezett.
    Az ideális fókusztávolság valahol a kettő között lenne. A 6mm-es lencse a kép szélein hordó torzítással
    rajzol, szerencsére ezeket a szoftverrel - egy szűkebb kivágást beállítva - le lehet vágni.
 * [DHT22](https://www.sparkfun.com/products/10167) hőmérséklet és páratartalom szenzor
   * ár/érték arányban megfelelő hőmérséklet szenzor. Könnyen programozható és nem utolsó sorban egy egyszerű
     telefonzsinórral a RPi-től távol is telepíthető. 
 * Egyéb kiegészítők
   * A RPi csak egy kompakt számítógép, szükséged lesz perifériákra, legalább az üzembe helyezéskor
     * monitor (a RPi-nek HDMI kimenete van, kellhet egy HDMI - VGA átalakító)
     * billentyűzet, egér. A RPi 3A-nak egyetlen USB kimenete van, ehhez én egy touchpad-del ellátott vezeték nélküli
       billentyűzetet használtam.
     * SD kártya: A RPi-nek ez a belső tárhelye, az operációs rendszer és az alkalmazás is erről fut.

- [ ] **TODO** képek

### Software
- [ ] **TODO**

## Raspberry Pi üzembe helyezése
### Raspberry Pi OS telepítése
A RPi-t megvásárolhatod a gyári operációs rendszerrel, vagy anélkül is. Ha nincs operációs rendszered, könnyen rámásolhatsz egyet
egy SD kártyára a Raspberry Pi Imager segítségével.

1. Telepítsd a [Raspberry Pi Imager-t](https://www.raspberrypi.com/software/) a számítógépedre
2. A program indítása után a felkínált operációs rendsszerek közül válaszd az alapértelmezett "Raspberry Pi OS (32bit)"-t
3. Ments rá az SD kártya

### A Raspberry Pi összeszerelése
1. Helyezzük az SD káryát a Raspberry Pi 3 kártya foglalatába
2. Csatlakoztassuk az USB billenytűzetet
3. Csatlakoztassuk a monitor HDMI csatlakozóját
4. Dugjuk rá a tápegység csatlakozóját, majd helyezzük áram alá.

Ha minden jól megy, a piros led felvillan, és a monitoron megjelenik a **RaspberryPi OS** betöltő-képernyője.

### Az OS (operációs rendszer) beállítása
* Az első elindulás után adjuk meg országot, nyelvet, időzónát
* **Változtassuk meg az alapértelmezett jelszót**
* Csatlakozzunk a WiFi hálózatra

Az operációs rendszer ezután frissítéseket fog keresni és telepíteni.
Újraindítás után változtassunk meg néhány rendszer beállítást:

Start menü (málna ikon) → Beállítások → **"Raspberry Pi Configuration"**
* "Interfaces" fül: 
	* Camera: Enable
	* SSH: Enable
	* VNC: Enable
* "Performance" fül:
	* GPU Memory: 256 Mb
* "OK" → indítsuk újra az eszközt

### Az eszköz távoli elérése
Sok esetben praktikus, ha a RPi-t távolról is el tudjuk érni. Ehhez többek között VNC-t vagy SSH-t használhatunk.

* VNC segítségével
  * Lásd még: [hivatalos leírás](https://www.raspberrypi.com/documentation/computers/remote-access.html#virtual-network-computing-vnc)
  * Telepítsük a [VNC klienset](https://www.realvnc.com/en/connect/download/viewer/) a számítógépünkre:
  * Ha a beállításokban engedélyeztük, akkor a RPi újraindítása után elindul a VNC szerver.
    * A jobb felső sarokban lévő VNC ikonra kattintva láthatjuk az IP címet amire a számítógépünkkel csatlakozhatunk.
* SSH
  * amennyiben fent rendszer szinten engedélyeztük az SSH-t, már meg is próbálkozhatunk a RPi-hez csatlakozni.
  * Windowsról tipikusan [PuTTY](https://www.putty.org/) segítségével
  * Lásd még: [segédlet](https://linuxize.com/post/how-to-enable-ssh-on-raspberry-pi/)
	

### Kamera összeszerelése
Lásd még: [hivatalos leírás](https://projects.raspberrypi.org/en/projects/getting-started-with-picamera)

#### A lencse felhelyezése
* A HQ Camera-t rögzítsük az állványon, a védő kupakot távolítsuk el.
* A vásárolt lencsénktől függően (pl. "CS mount" esetén) lehet, hogy a védőkupak mögötti közgyűrűt is ki kell csavarnunk.
* Csavarjuk a lencsét a menetbe, amennyire csak lehet.

#### Szalagkábel rögzítése
* Állítsuk le a RPi-t és áramtalanítsuk.
* Az alaplapon keressük meg a "CAMERA" feliratú kábelbemenetet.
* A fekete reteszt a tetején körömmel vagy lapos csavarhúzóval emeljük ki.
* Illesszük be a szalagkábelt úgy, hogy a fényes erezete a fém csatlakozók felé nézzen (vagyis a kékre festett felület a fekete retesz felé).
* Toljuk vissza a reteszt és indítsuk újra a RPi-t

#### Tesztfotó
Az LXTerminal ablakba írjuk be:

    raspistill -o Desktop/foto.jpg

Ha minden jól megy, egy pár másodperc után elkészül az első fotónk.

#### Élesség állítás
Indítsuk el ismét a fotó alkalmazást, de most nem készítünk képet, csak az élő képet szeretnék tartósan megjeleníteni (1 percig)

    raspistill -t 60000
    
Az élőkép segítségével próbáljuk a lencsét a fókusz gyűrűvel élesre állítani.

A reteszt a teljesen nyitott pozíciónál egy kicsit lejjebb reteszeltem, abban bízva, hogy a mélységéllesség és az objektív rajzolata is kedvezőbb lesz. A teljes reteszelést az éjszakai fotók miatt kerültem.

Ha egy perc nem volt elég, elindíthatjuk az élőképet időkorlát nélkül is (ilyenkor Ctrl + C megnyomásával lehet a programból kilépni):

    raspistill -t 0

Ha azt tapasztaljuk, hogy a lencsétől csak néhány mm-re rajzol éles képet az objektív, akkor felmerül, hogy bennmaradt a "C/CS-mount" közgyűrű. Vegyük ki.

### Hőmérő szenzor bekötése
Lásd még: [angol nyelvű leírás](https://pimylifeup.com/raspberry-pi-humidity-sensor-dht22/)

A DHT22 szenzor lábait kössük a megfelelő GPIO tüskékre:
1. táp. Alapesetben 3.3V (1. fizikai tüske)
2. adat. Valamely GPIO tüske. Alapesetben a [GPIO4](https://pinout.xyz/pinout/pin7_gpio4#)-en várja a program az adatot. `config.ini`-ben konfigurálható.
3. nem használt
4. föld, pl. 6. fizikai tüske

Felhúzó ellenállást nem szükséges bekötni, a RPi adat tüskéjét a program szoftveresen felhúzza 1-es szintre.

#### Alternatív táp megoldások
Ha a szenzor nagyon távol (> 5m) van a RPi-től gyengülhet a jel. Ha problémát tapasztalunk a nagy távolság miatt, megpróbálhatjuk a a DHT22-t 5V-ra kötni.

Az én esetemben a nagy távolság (de lehet, hogy egyéb kontakt problémák) miatt a DHT22 rendszeresen leállt, nem lehetett adatot kiolvasni. Ilyenkor a csatlakozó fizikai széthúzása és összedugása megoldotta a problémát. Ennek nyomán megpróbáltam egy távolról vezérelhető be/ki kapcsolót a programba építeni.

A szenzor bekötése annyiban változik, hogy a tápot nem a fix 3.3V-ról vesszük, hanem az egyik GPIO tüskét használom kimenetnek.
Ha a program 5 egymást követő alkalommal sem tud a DHT22-vel kommunikálni, leveszi a 'táp' GPIO tüske jelszintjét 0-ra, majd pár másodperc múlva visszaállítja 1-re. Ezzel a trükkel sikerült tartós megoldást találni az egyébként nehezen kinyomozható instabilitásra.

Ha a fenti GPIO-ról vezérelt tápot szeretnénk alkalmazni, módosítsuk a `config.ini`-t például az alábbiak szerint:

    PowerPin = 22

Ezzel a program a [GPIO22](https://pinout.xyz/pinout/pin15_gpio22#) tüskét fogja vezérelni. A DHT22-es tápját erre kössük rá.

###

## Idokep.hu regisztráció
Ha fel szeretnénk tölteni a kamera képét az idokep.hu-ra, regisztrálnunk kell egy felhasználót:
https://www.idokep.hu/regisztracio

Ha csak kamera-képet szeretnénk feltölteni, választhatjuk a "Kezdő szintű" regisztrációt. 

Ha a hőmérsékletet is meg szeretnénk osztani, ahhoz "Haladó szintű" regisztrációra van szükség. Ezt megelőzően érdemes átfutni a [Meterológiai alapismereteket](https://www.idokep.hu/alapismeretek), mert a regisztráció mellett egy rövid teszten kell jó eredmélnyt elérni.

A közvetítéshez érdemes még az [Időkép GY.I.K-et](https://wiki.idokep.hu/) is átolvasni.

## Időjárás figyelő telepítése
Kezdjük a RPi frissítésével a szokásos módon.

    sudo apt update
    sudo apt full-upgrade

Másoljuk le a szoftvercsomagot az eszközre ("klónozzuk a repo-t").

    git clone https://github.com/mobalk/raspi-weathercam.git
    cd raspi-weathercam
    ls
    
Ha minden jól ment, az eszközön rajta vannak a szükséges file-ok.

### Külső software-függőségek
A DHT22 hőmérséklet szenzor használatához a következő Python könyvtárakra lesz szükség.

    pip3 install adafruit-circuitpython-dht
    sudo apt install libgpiod2

A `viewerstat.sh` parancsfile automatikus E-Mail küldésre az `msmtp` programot használja. Beállítását lásd később.

    sudo apt install msmtp
    
#### Opcionális programok
Jól jöhet egy egyszerű képszerkesztő a kamera-képkivágás paraméterezéséhez. 

    sudo apt install mirage
    
A log file-ok egyidejű vizsgálatához ajánlott:

    sudo apt install multitail
    
Egy példa *alias* a használatára, amit a `~/.bash_aliases` file-ba másolhatunk:

```shell
echo "alias log='multitail -s 2 -sn 1,3 ~/raspi-weathercam/weathercam.log ~/raspi-weathercam/temperature.log ~/.raspi-weathercam/sendTemp.log ~/.raspi-weathercam/viewerstat.csv'" >> ~/.bash_aliases
```

### Beállítások
A program-beállításokat két file tartalmazza:

* [config.ini](config.ini) - ez tartalmazza az általános beállításokat
* [userauth.ini](userauth.ini-TEMPLATE) - ebben tároljuk a személyes adatokat, amelyekkel pl. az idokep.hu-ra be tudunk lépni

```shell
nano config.ini
```

Nézzük át az alapértelmezett beállításokat:
* adatbázis neve és helye
* a személyes beállításokat tartalmazó file neve és helye
* a kívánt kamera felbontás - erről később még lesz szó
* stb.

Másoljuk át a személyes beállításokat tartalmazó TEMPLATE file-t a kívánt helyre és módosítsuk azt.

    mkdir ~/.raspi-weathercam
    cp userauth.ini-TEMPLATE ~/.raspi-weathercam/userauth.ini
    nano ~/.raspi-weathercam/userauth.ini

Írjuk be az idokep.hu regisztrációs adatainkat és hogy milyen e-mail címre jöjjön a levél leállás esetén.

### Automatikus e-mail
A következő cikkeket javaslom a helyes konfigurációhoz: 

* https://techrapiduk.blogspot.com/2017/04/send-email-on-raspberry-pi-with-msmtp.html
* https://www.howtoraspberry.com/2021/06/how-to-send-mail-from-a-raspberry-pi/
* A google account-ot is be kell állítani, hogy elfogadja a nem túl biztonságos csak jelszó alapú autentikációt.
  Lehet, hogy célszerű ehhez egy csak erre használt új Gmail email cím készítése:
  https://stackoverflow.com/questions/38391412/raspberry-pi-send-mail-from-command-line-using-gmail-smtp-server

## Az időjárás-figyelő indítása
### Égkép fotózása és feltöltése

    cd ~/raspi-weathercam
    python3 camloop.py
    
A futási log-ot itt tekinthetjük meg:

    tail -f weathercam.log
    
Az elkészült képeket a `config.ini`-ben beállított mappában (`~/Pictures/idokep`) találjuk.
Ha az idokep account-ot még nem állítottuk be a `userAuth.ini` file-ban, akkor a program csak elmenti a képeket, de nem tölti fel őket.

### Hőmérséklet mérése

    cd ~/raspi-weathercam
    python3 thermometer.py

A futási log-ot itt tekinthetjük meg:

    tail -f temperature.log
    
A mérési eredményeket a program `config.ini`-ben beállított adatbázisban tárolja.

### Mért adatok megjelenítése
A napi hőmérsékleti adatokat kirajzolhatjik grafikonokon.
Ehhez szükség van további segéd könyvtárak telepítésére:

    pip3 install pandas
    
Napi hőmérséklet és páratartalom grafikon

    python3 plot_today_temp.py
    
Napi hőmérséklet az elmúlt hét átlagával együtt

    python3 plot_temp_stat.py

### Időzített futtatások
Ha a fenti programok gond nélkül üzemelnek, ismerkedjünk meg további parancsfile-okkal amelyeket időzítetten célszerű futtatni.

**Fontos**, hogy mielőtt az időképre feltöltjük az adatainkat, győződjünk meg arról, hogy a hőmérő program tartósan (napokon keresztül) helyesen működik.
Vessük össze a mért adatainkat a környékről beküldött más automaták mintáival.

Az időzített parancsokhoz Linux cron bejegyzéseket készítünk.

    crontab -e

Másoljuk be a lenti beállításokat `cron` bejegyzések végére:

```shell
# m h  dom mon dow   command
*/3 * * * *  /home/pi/raspi-weathercam/sendTemperature.py
59 5,9,13,17,21,23 * * * /home/pi/raspi-weathercam/viewerstat.sh
0 1 * * * /home/pi/raspi-weathercam/arch.py > /home/pi/.raspi-weathercam/arch_cron.log 2>&1
```

* `sendTemperate.py` - 3 percenként elküldi az utolsó hőmérsékleti adatok átlagát
* `viewerstat.sh` - Naponta hatszor ránéz a kameraképünkre és elmenti a látogatószámot. Ha a kamerakép nem elérhető, email-t küld.
* `arch.py` - naponta archiválja az x napnál régebbi képeket (lekicsinyíti és dátum szerint az `~/Pictures/idokep/arch` könyvtárba másolja.
   Az eredeti törlésre kerül.

Fenti időzített futásokat átmenetileg kikapcsolhatjuk, ha a megfelelő parancsot egy sor eleji `#`-el kikommentezzük.

# Kérdés, észrevétel, panasz

    mobalkhu at gmail dot com
