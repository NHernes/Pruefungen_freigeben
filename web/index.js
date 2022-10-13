setTimeout(function () {
    document.getElementById("tabellen-scroll").style.zIndex="1";
    element = document.getElementById('splash_text')
    element.remove()
    element = document.getElementById('splash_bild')
    element.remove()
  }, 2000)

setTimeout(function () {
document.getElementById("fächer-abruf").disabled = true;

}, 1800)


lizenzen_abrufen=document.getElementById("lizenzen_abrufen")

document.addEventListener('input', (evt) => {
    if (document.getElementById('passwort').value == "" || document.getElementById('benutzername').value == "" || document.getElementById('table').value == ""){
        lizenzen_abrufen.disabled = true;
    }
    else {
        lizenzen_abrufen.disabled = false;
    }
  });


eel.expose(abruf_webex_daten);
async function abruf_webex_daten(){
    document.getElementById('platzhalter5').id = 'loader';
    const webex_meetings_liste=await eel.meeting_informationen_abrufen()()
    
    var selectElement = document.getElementById('meeting-select');
    selectElement.innerHTML="";
    webex_meetings_liste.forEach(function (item, index) {
        selectElement.options[selectElement.options.length]= new Option(item)
      });
    
    if (webex_meetings_liste.length>0) {
        tn_abrufen=document.getElementById("tn_abrufen")
        tn_abrufen.disabled = false;
    };
    document.getElementById('loader').id = 'platzhalter5';
    
    }

eel.expose(abfrage);
async function abfrage(){
    document.getElementById('platzhalter4').id = 'loader';
    var meeting_auswahl=document.getElementById("meeting-select").value;

    const array_tn=await eel.tn_abrufen(meeting_auswahl)()
    array_tn.sort()

    var table = document.getElementById("table");
    while(table.rows.length > 1) {
        table.deleteRow(-1);
    }

    document.getElementById('meeting-name').innerHTML = `Webex-Meeting: ${meeting_auswahl}`;
    document.getElementById('gesamtzahl').innerHTML = `Gesamtzahl: ${array_tn.length}`;
    for (const value of array_tn) {
        var table = document.getElementById("table");
        var row = table.insertRow(-1);
        var cell1 = row.insertCell(0);
        var cell2 = row.insertCell(1);
        var cell3 = row.insertCell(2);

        cell1.innerHTML = value[0];
        cell2.innerHTML = value[1];
        cell3.innerHTML = value[2];


    }
    document.getElementById('loader').id = 'platzhalter4';
}

eel.expose(lplus_lizenzen)
async function lplus_lizenzen(){
    document.getElementById('platzhalter1').id = 'loader';
    var benutzername = document.getElementById("benutzername").value;
    var passwort = document.getElementById("passwort").value;
    var liste_lizenzen=await eel.lplus_lizenzen_abrufen(benutzername,passwort)();

    if (liste_lizenzen==false){
        alert("Logindaten stimmen nicht überein")
        
    }
    else if (liste_lizenzen=="Keine Lizenzen"){
        alert("Keine Lizenzen mit aktuellen Gültigkeitszeiträumen vorhanden")
    }
    else {
        var liste=document.getElementById("lplus_lizenzen");
        document.getElementById("lizenzen-abruf").setAttribute('placeholder',"Bitte Lizenz auswählen/eintippen...");
        document.getElementById('lplus_lizenzen').innerHTML = '';
        liste_lizenzen.forEach(function (item) {
            var option = document.createElement('option');
            option.value = item;
            liste.appendChild(option);
            
            
            
        });
        fächer_abrufen.disabled=false;
        document.getElementById("lizenzen-abruf").disabled = false;

      
        
    }
    document.getElementById('loader').id = 'platzhalter1';
}

eel.expose(lplus_fächer)
async function lplus_fächer(){
    document.getElementById('platzhalter2').id = 'loader';
    var fach = document.getElementById("lizenzen-abruf").value;
    const liste_fächer=await eel.lplus_fächer_abrufen(fach)();

    var selectElement = document.getElementById('fächer-abruf');
    document.getElementById("fächer-abruf").innerHTML = "";
    document.getElementById("fächer-abruf").disabled = false;
    liste_fächer.forEach(function (item, index) {
        selectElement.options[selectElement.options.length]= new Option(item)
      });
    if (liste_fächer.length>0){
        prüfungsfreigabe=document.getElementById("prüfung_freigeben")
        prüfungsfreigabe.disabled=false
        prüfungsfreigabe_alle=document.getElementById("alle_prüfungen_freigeben")
        prüfungsfreigabe_alle.disabled=false
        prüfungen_zurückziehen_button=document.getElementById("alle_prüfungen_zurückziehen")
        prüfungen_zurückziehen_button.disabled=false
    }
    document.getElementById('loader').id = 'platzhalter2';
}

eel.expose(prüfung_freigeben)
async function prüfung_freigeben(){
    var tn_aktuell=document.getElementById("table").rows.length;
    if (tn_aktuell<2){
        alert("Es liegen keine Teilnehmenden zur Freigabe vor!")
    }
    else{
        var lizenz_id=document.getElementById("lizenzen-abruf").value;
        const fächer_id=document.querySelectorAll('#fächer-abruf option:checked');
        const fächer_id_array = Array.from(fächer_id).map(el => el.value);

        text=await eel.anzeige_freigabeauswahl_confirm(lizenz_id,fächer_id_array)()

        var bestätigung=confirm(`Soll die Prüfungsfreigabe für die anwesenden Prüflinge erfolgen? \n${text}`)

        if (bestätigung){
            globalThis.abgerufene_personen_anzahl=0
            globalThis.freigegebene_prüfungen_anzahl=0
            
            darstellung_abgerufene_tn=document.getElementById("darstellung_abgerufene_tn")
            darstellung_abgerufene_tn.innerHTML=`Abgerufene Kandidat:innen: ${globalThis.abgerufene_personen_anzahl}`

            darstellung_freigegebene_prüfungen=document.getElementById("darstellung_freigegebene_prüfungen");
            darstellung_freigegebene_prüfungen.innerHTML=`Freigegebene Prüfungen: ${globalThis.freigegebene_prüfungen_anzahl}`
            document.getElementById("checkmark-1").style.color="white"
            document.getElementById("checkmark-2").style.color="white"
            modal.style.display = "block";
            
            /*
            document.getElementById('platzhalter3').id = 'loader';
            document.querySelectorAll('button').forEach(elem => {
                elem.disabled = true;
            });
            */

            const ergebnis=await eel.prüfung_freigeben(lizenz_id,fächer_id_array)();
            const daten_freigabe=ergebnis[0]
            daten_freigabe.sort()

            var table = document.getElementById("table");
            while(table.rows.length > 1) {
                table.deleteRow(-1);
            }


            for (const value of daten_freigabe) {
                var table = document.getElementById("table");
                var row = table.insertRow(-1);
                var cell1 = row.insertCell(0);
                var cell2 = row.insertCell(1);
                var cell3 = row.insertCell(2);

                cell1.innerHTML = value[0];
                cell2.innerHTML = value[1];
                cell3.innerHTML = value[2];
            }
            document.getElementById("freigegeben").innerHTML = "";
            document.getElementById("freigegeben").innerHTML = `Freigegeben: ${ergebnis[1]}`;
            
            /* 
            document.getElementById('loader').id = 'platzhalter3';
            
                      
            document.querySelectorAll('button').forEach(elem => {
                elem.disabled = false;
            });
            

            document.getElementById('loader').id = 'platzhalter3';
            */
            var button_modal = document.getElementById("bestätigung_modal");
            document.getElementById("checkmark-2").style.color="black"
            button_modal.disabled=false

            var excelliste_button = document.getElementById("excelliste_button");
            excelliste_button.disabled=false
        }
        else{
            alert("Aktion wurde abgebrochen");
            
        }
    }
}

eel.expose(alle_prüfungen_freigeben)
async function alle_prüfungen_freigeben(){

    var lizenz_id_übersicht=document.getElementById("lizenzen-abruf").value;
    const fächer_id_übersicht=document.querySelectorAll('#fächer-abruf option:checked');
    const fächer_id_array_übersicht= Array.from(fächer_id_übersicht).map(el => el.value);

    var übersicht_prüfunsdaten=await eel.übersicht_anzahl_kandidaten(lizenz_id_übersicht,fächer_id_array_übersicht)();
    var zahl_prüflinge_gesamt=übersicht_prüfunsdaten[0]
    var prüfungen_gesamt=übersicht_prüfunsdaten[1]

    text=await eel.anzeige_freigabeauswahl_confirm(lizenz_id_übersicht,fächer_id_array_übersicht)()

    var bestätigung=confirm(`Sollen ${prüfungen_gesamt} Prüfungsfreigaben für insgesamt ${zahl_prüflinge_gesamt} Prüflinge erfolgen? \n${text} `)
    if (bestätigung){
        globalThis.abgerufene_personen_anzahl=0
        globalThis.freigegebene_prüfungen_anzahl=0
        darstellung_abgerufene_tn=document.getElementById("darstellung_abgerufene_tn")
        darstellung_abgerufene_tn.innerHTML=`Abgerufene Kandidat:innen: ${globalThis.abgerufene_personen_anzahl}`
        darstellung_freigegebene_prüfungen=document.getElementById("darstellung_freigegebene_prüfungen");
        darstellung_freigegebene_prüfungen.innerHTML=`Freigegebene Prüfungen: ${globalThis.freigegebene_prüfungen_anzahl}`
        document.getElementById("checkmark-1").style.color="white"
        document.getElementById("checkmark-2").style.color="white"
        modal.style.display = "block";
        
        /*
        document.getElementById('platzhalter6').id = 'loader';
        
        document.querySelectorAll('button').forEach(elem => {
            elem.disabled = true;
          });
          */
        var lizenz_id=document.getElementById("lizenzen-abruf").value;
        const fächer_id=document.querySelectorAll('#fächer-abruf option:checked');
        const fächer_id_array = Array.from(fächer_id).map(el => el.value);
        ergebnis=await eel.alle_prüfungen_freigeben(lizenz_id,fächer_id_array)();
        const daten_freigabe=ergebnis[0];
        daten_freigabe.sort();

        var table = document.getElementById("table");
        while(table.rows.length > 1) {
            table.deleteRow(-1);
        }


        for (const value of daten_freigabe) {
            var table = document.getElementById("table");
            var row = table.insertRow(-1);
            var cell1 = row.insertCell(0);
            var cell2 = row.insertCell(1);
            var cell3 = row.insertCell(2);

            cell1.innerHTML = value[0];
            cell2.innerHTML = value[1];
            cell3.innerHTML = value[2];
        }
        document.getElementById("freigegeben").innerHTML = "";
        document.getElementById("freigegeben").innerHTML = `Freigegeben: ${ergebnis[1]}`;
        /*
        document.querySelectorAll('button').forEach(elem => {
            elem.disabled = false;
          });
          
        document.getElementById('loader').id = 'platzhalter6';
        */
        var button_modal = document.getElementById("bestätigung_modal");
        button_modal.disabled=false;
        document.getElementById("checkmark-2").style.color="black";
        
        var excelliste_button = document.getElementById("excelliste_button");
        excelliste_button.disabled=false
    }
    else{
        alert("Aktion wurde abgebrochen");
    }
};

eel.expose(progess_abgerufene_personen);
function progess_abgerufene_personen(info_python){
    globalThis.abgerufene_personen_anzahl=globalThis.abgerufene_personen_anzahl+info_python;
    darstellung_abgerufene_tn=document.getElementById("darstellung_abgerufene_tn");
    darstellung_abgerufene_tn.innerHTML=`Abgerufene Kandidat:innen: ${globalThis.abgerufene_personen_anzahl}`
}

eel.expose(progess_freigegebene_prüfungen);
function progess_freigegebene_prüfungen(info_python){
    document.getElementById("checkmark-1").style.color="black"
    globalThis.freigegebene_prüfungen_anzahl=globalThis.freigegebene_prüfungen_anzahl+info_python;
    darstellung_freigegebene_prüfungen=document.getElementById("darstellung_freigegebene_prüfungen");
    darstellung_freigegebene_prüfungen.innerHTML=`Freigegebene Prüfungen: ${globalThis.freigegebene_prüfungen_anzahl}`
}

eel.expose(progess_abgerufene_personen_zurückziehen);
function progess_abgerufene_personen_zurückziehen(info_python){
    document.getElementById("checkmark-3").style.color="black"
    globalThis.abgerufene_personen_zurückziehen_anzahl=globalThis.abgerufene_personen_zurückziehen_anzahl+info_python;
    darstellung_abgerufene_personen_zurückziehen=document.getElementById("darstellung_abgerufene_tn_zurückziehen");
    darstellung_abgerufene_personen_zurückziehen.innerHTML=`Abgerufene Kandidat:innen: ${globalThis.abgerufene_personen_zurückziehen_anzahl}`
}

eel.expose(progess_zurückgezogene_prüfungen);
function progess_zurückgezogene_prüfungen(info_python){
    /*document.getElementById("checkmark-3").style.color="black"*/
    globalThis.zurückgezogene_prüfungen_anzahl=globalThis.zurückgezogene_prüfungen_anzahl+info_python;
    darstellung_zurückgezogene_prüfungen=document.getElementById("darstellung_zurückgezogene_prüfungen");
    darstellung_zurückgezogene_prüfungen.innerHTML=`Zurückgezogene Prüfungen: ${globalThis.zurückgezogene_prüfungen_anzahl}`
}

eel.expose(prüfungen_zurückziehen);
async function prüfungen_zurückziehen(){
    var lizenz_id_übersicht=document.getElementById("lizenzen-abruf").value;
    const fächer_id_übersicht_zurückziehen=document.querySelectorAll('#fächer-abruf option:checked');
    const fächer_id_array_übersicht_zurückziehen= Array.from(fächer_id_übersicht_zurückziehen).map(el => el.value);
    text=await eel.zurückziehen_übersicht(lizenz_id_übersicht,fächer_id_array_übersicht_zurückziehen)()
    var bestätigung_zurückziehen=confirm(`${text}`)

    if (bestätigung_zurückziehen){
        globalThis.abgerufene_personen_zurückziehen_anzahl=0
        globalThis.zurückgezogene_prüfungen_anzahl=0
        /*document.getElementById("checkmark-3").style.color="white"*/
        document.getElementById("checkmark-4").style.color="white"
        /*darstellung_abgerufene_tn_zurückziehen=document.getElementById("darstellung_abgerufene_tn_zurückziehen")*/
        /*darstellung_abgerufene_tn_zurückziehen.innerHTML=`Abgerufene Kandidat:innen: ${abgerufene_personen_zurückziehen_anzahl}`*/
        darstellung_zurückgezogene_prüfungen=document.getElementById("darstellung_zurückgezogene_prüfungen");
        darstellung_zurückgezogene_prüfungen.innerHTML=`Zurückgezogene Prüfungen: ${globalThis.zurückgezogene_prüfungen_anzahl}`;
        modal2.style.display = "block";

        ergebnis=await eel.alle_prüfungen_zurückziehen(lizenz_id_übersicht,fächer_id_array_übersicht_zurückziehen)()

        var button_modal2 = document.getElementById("bestätigung_modal2");
        document.getElementById("checkmark-4").style.color="black"
        button_modal2.disabled=false
        }
    else{
        alert("Aktion wurde abgebrochen");
    }
}

eel.expose(excelliste_generieren);
async function excelliste_generieren(){
    ergebnis=await eel.excelliste_generieren()()
    if (ergebnis){
        alert("Excelliste generiert.")
    }
    else{
        alert("Fehler beim Generieren der Excelliste")
    }
};

// Get the modal
var modal = document.getElementById("myModal");

var button_modal_bestätigung = document.getElementById("bestätigung_modal");

button_modal_bestätigung.onclick = function() {
    modal.style.display = "none";
  };

// Get the modal
var modal2 = document.getElementById("myModal2");

var button_modal_bestätigung2 = document.getElementById("bestätigung_modal2");

button_modal_bestätigung2.onclick = function() {
    modal2.style.display = "none";
  }

