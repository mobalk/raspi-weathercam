# Részletes telepítési útmutató

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
    
Ha az egy perc sem elég, elindíthatjuk az élőképet időkorlát nélkül is (ilyenkor Ctrl + C megnyomásával lehet a programból kilépni):

    raspistill -t 0

Ha azt tapasztaljuk, hogy a lencsétől csak néhány mm-re rajzol éles képet az objektív, akkor felmerül, hogy bennmaradt a "C/CS-mount" közgyűrű. Vegyük ki.

## Időjárás figyelő telepítése
- [ ] **TODO**
