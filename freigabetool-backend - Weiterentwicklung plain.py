import datetime
import json,requests
import datetime
from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *
import eel
import numpy as np
from threading import Thread
import csv
import config


lplus_client_id= config.lplus_client_id
lplus_client_secret= config.lplus_client_secret


eel.init("web")

def oauth():
    global access_token

    client_id=config.client_id
    client_secret=config.client_secret
    auth_url=config.auth_url
    code_url=config.code_url
    code=config.code
    refresh_token=config.refresh_token

    client_id=client_id
    client_secret=client_secret
    auth_url=auth_url
    code_url=code_url
    code=code
    url="https://webexapis.com/v1/authorize"

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    """
    r= requests.post(url=code_url,headers=headers)
    print(r.text)
    """
    """
    with open("access_token_webex.txt","r") as f:
        access_token=f.read()
    
    with open("refresh_token_webex.txt","r") as g:
        refresh_token=g.read()


    url="https://webexapis.com/v1/people/me"

    headers={
        "Authorization": f"Bearer {access_token}",
        "content-type": "application/x-www-form-urlencoded; charset=utf-8;"
    }
    
    r = requests.get(url,headers=headers)
    if r.status_code==200:
        pass
    
    else:
    """
    url=f"https://webexapis.com/v1/access_token?grant_type=refresh_token&client_id={client_id}&client_secret={client_secret}&refresh_token={refresh_token}"

    r = requests.post(url,headers=headers)
    r=json.loads(r.text)
    r=r["access_token"]

    """
    with open("access_token_webex.txt","w") as f:
        f.write(r)
    """

    access_token=r

    return access_token

@eel.expose
def meeting_informationen_abrufen():
    global liste1
    access_token=oauth()
    heute_datum=datetime.now().date()
    beginn=datetime(heute_datum.year, heute_datum.month, heute_datum.day, 0, 0, 0).isoformat()
    ende=datetime(heute_datum.year, heute_datum.month, heute_datum.day, 21, 0, 0).isoformat()

    url=f"https://webexapis.com/v1/meetings?meetingType=scheduledMeeting&scheduledType=meeting&from={str(beginn)}&to={str(ende)}"
                                                        
    headers={
        "Authorization": f"Bearer {access_token}"
    }
        
    r = requests.get(url, headers=headers)
    daten=json.loads(r.text)
    daten=daten["items"]

    heute=datetime.now().strftime("%Y-%m-%d")

    liste1=[]
    liste2=[]
    for count,i in enumerate(daten):
        
        if heute in daten[count]["start"]:
            liste1=liste1+[[daten[count]["id"],daten[count]["start"],daten[count]["title"]]]
            liste2.append(daten[count]["title"])

    return liste2


@eel.expose
def tn_abrufen(meeting_auswahl):
    global liste1,personen_webex_meeting
    access_token=oauth()
    
    for count,i in enumerate(liste1):
        if meeting_auswahl == liste1[count][2]:
            prüfungs_id=liste1[count][0]
    url=f"https://webexapis.com/v1/meetingParticipants?meetingId={prüfungs_id}&max=100"
                                                      
    headers={
        "Authorization": f"Bearer {access_token}"
    }

    r = requests.get(url, headers=headers)
    daten_tn=json.loads(r.text)
    daten_tn=daten_tn["items"]

    head=r.headers
    while "link" in head.keys():
        url=head["link"]
        url=url[1:]

        while ">" in url:
            url=url[:-1]
                                                        
        headers={
            "Authorization": f"Bearer {access_token}"
        }

        r = requests.get(url, headers=headers)

        daten_erweiterte_abfrage=(json.loads(r.text))["items"][0]
        daten_tn.append(daten_erweiterte_abfrage)

        head=r.headers


    personen_webex_meeting=[]

    for count,einträge in enumerate(daten_tn):

        zedatname=daten_tn[count]["email"]
        
        while "@" in zedatname:
            zedatname=zedatname[:-1]
        if zedatname!="eexamwebex" and daten_tn[count]["state"]=="joined":
            personen_webex_meeting=personen_webex_meeting+[[daten_tn[count]["displayName"],zedatname,"❌"]]


    return personen_webex_meeting


@eel.expose
def lplus_lizenzen_abrufen(benutzername,passwort):
    global lizenzdaten,token,benutzername_py, passwort_py,headers,lplus_client_id,lplus_client_secret
    
    benutzername_py=benutzername
    passwort_py=passwort
    payload = {
    'grant_type': 'password',
    'client_id': lplus_client_id,
    'client_secret': lplus_client_secret,
    'username': benutzername,
    'password': passwort
    }

    
    r = requests.post("https://fub.lplus-teststudio.de/token", 
        data=payload)

    if r.status_code!=200:
        login=bool(0)
        return login

    else:
        token=json.loads(r.text)["access_token"]

        headers={
            "Authorization": f"Bearer {token}"
            }

        r = requests.get("https://fub.lplus-teststudio.de/publicapi/v1/licences", 
            headers=headers)


        lizenzen=json.loads(r.text)
        lizenznamen=[]
        lizenzdaten={}
        
        def auswahl_gültigkeitszeitraum(lizenznamen,lizenzdaten): #Hier werden die Lizenzen nach Gültigkeitszeitraum gefiltert
            zähler=-1
            for eintrag in lizenzen:
                zähler+=1
                if (lizenzen[zähler]["licenceTimeLimits"]!=[]):
                    #print(json.dumps(i, sort_keys=True, indent=4, separators=(",", ": ")))
                    
                    
                    zeiträume=lizenzen[zähler]["licenceTimeLimits"]
                    if type(zeiträume)==list:
                        counter=-1
                        for timeslots in zeiträume:
                            counter+=1
                            uhrzeit_lizenz=lizenzen[zähler]["licenceTimeLimits"][counter]["from"][11:16]
                            uhrzeit_lizenz=datetime.strptime(uhrzeit_lizenz,"%H:%M")+timedelta(hours=2)
                            uhrzeit_lizenz=uhrzeit_lizenz.time()
                            lizenzen[zähler]["licenceTimeLimits"][counter]["from"]=(isoparse(lizenzen[zähler]["licenceTimeLimits"][counter]["from"])+timedelta(hours=2)).date()
                            heute=datetime.now().date()
                            if lizenzen[zähler]["licenceTimeLimits"][counter]["from"]==heute:
                                lizenznamen=lizenznamen+[f'{lizenzen[zähler]["name"]}|{lizenzen[zähler]["id"]}']
                                lizenzdaten.update({lizenzen[zähler]["name"]:lizenzen[zähler]["id"]})
                    
                    else:
                        uhrzeit_lizenz=lizenzen[zähler]["licenceTimeLimits"][counter]["from"][11:16]
                        uhrzeit_lizenz=datetime.strptime(uhrzeit_lizenz,"%H:%M")+timedelta(hours=2)
                        uhrzeit_lizenz=uhrzeit_lizenz.time()
                        lizenzen[zähler]["licenceTimeLimits"][0]["from"]=(isoparse(lizenzen[zähler]["licenceTimeLimits"][0]["from"])+timedelta(hours=2)).date()
                        heute=datetime.now().date()
                        if lizenzen[zähler]["licenceTimeLimits"][0]["from"]==heute:
                            lizenznamen=lizenznamen+[f'{lizenzen[zähler]["name"]}|{lizenzen[zähler]["id"]}']
                            lizenzdaten.update({lizenzen[zähler]["name"]:lizenzen[zähler]["id"]})

            return lizenznamen

        def auswahl_alle_lizenzen(lizenznamen,lizenzdaten):
            for count,eintrag in enumerate(lizenzen):
                lizenznamen=lizenznamen+[f'{lizenzen[count]["name"]} | {lizenzen[count]["id"]}']
                
                lizenzdaten.update({lizenzen[count]["name"]:lizenzen[count]["id"]})
            return lizenznamen

        lizenznamen=auswahl_alle_lizenzen(lizenznamen,lizenzdaten)

        if lizenznamen==[]:
            lizenznamen="Keine Lizenzen"


        return lizenznamen

@eel.expose
def lplus_fächer_abrufen(fach):
    global liste_fächer_vollständig
    headers={
    "Authorization": f"Bearer {token}"
    }

    liste_fächer=[]
    liste_fächer_vollständig={}

    for key,item in lizenzdaten.items():

        if key in fach:
            lizenz_id=item
            r = requests.get(f"https://fub.lplus-teststudio.de/publicapi/v1/licences/{lizenz_id}/subjects", 
                headers=headers)
            alle_fächer=json.loads(r.text)
            for eintrag in alle_fächer:
                liste_fächer=liste_fächer+[f'{eintrag["name"]} |{eintrag["id"]}']
                liste_fächer_vollständig.update({eintrag["name"]:eintrag["id"]})

    
    return liste_fächer
    
@eel.expose
def prüfung_freigeben(lizenz_id,fächer_id_array):
    global freigabezähler,excel_download_liste
    while "|" in lizenz_id:
        lizenz_id=lizenz_id[1:]


    for count,eintrag in enumerate(fächer_id_array):
        while "|" in fächer_id_array[count]:
            fächer_id_array[count]=fächer_id_array[count][1:]
    
    r = requests.get(f"https://fub.lplus-teststudio.de/publicapi/v1/licences/{lizenz_id}/candidateRelations", 
    headers=headers)

    daten_gemeldete_nutzer=json.loads(r.text)

    if len(daten_gemeldete_nutzer)<10:
        for eintrag in daten_gemeldete_nutzer:
            tn_id=eintrag["userDetailId"]
            r = requests.get(f"https://fub.lplus-teststudio.de/publicapi/v1/candidate/{tn_id}", 
            headers=headers)

            if r.status_code==200:
                eel.progess_abgerufene_personen(1)

            tn_name=json.loads(r.text)

            matrikelnummer=tn_name["importKey"]
            eintrag.update({"matrikelnummer":matrikelnummer})
                
            if not isinstance(tn_name["firstName"], str):
                tn_name["firstName"]=""
            if not isinstance(tn_name["lastName"], str):
                tn_name["lastName"]=""
            tn_klarname=f'{tn_name["firstName"]} {tn_name["lastName"]}'
            tn_name=tn_name["userName"]

            eintrag.update({"tn_name":tn_name})
            eintrag.update({"klarname":tn_klarname})


    if len(daten_gemeldete_nutzer)>=10:
        pieces = 10
        new_arrays = np.array_split(daten_gemeldete_nutzer, pieces)


        master_liste_gemeldete_nutzer=[]

        def nutzernamen_ziehen(array):
            daten_gemeldete_nutzer1=array
            for eintrag in daten_gemeldete_nutzer1:
                tn_id=eintrag["userDetailId"]
                r = requests.get(f"https://fub.lplus-teststudio.de/publicapi/v1/candidate/{tn_id}", 
                headers=headers)

                if r.status_code==200:
                    eel.progess_abgerufene_personen(1)

                tn_name=json.loads(r.text)

                matrikelnummer=tn_name["importKey"]
                eintrag.update({"matrikelnummer":matrikelnummer})
                
                if not isinstance(tn_name["firstName"], str):
                    tn_name["firstName"]=""
                if not isinstance(tn_name["lastName"], str):
                    tn_name["lastName"]=""
                tn_klarname=tn_name["firstName"]+" "+tn_name["lastName"]
                tn_name=tn_name["userName"]

                eintrag.update({"tn_name":tn_name})
                eintrag.update({"klarname":tn_klarname})
                master_liste_gemeldete_nutzer.append(eintrag)

        threads = []
        for i in range(0,10):
            threads.append(Thread(target=nutzernamen_ziehen, args=(new_arrays[i],)))
            threads[-1].start()
        for thread in threads:
            thread.join()
        
        daten_gemeldete_nutzer=master_liste_gemeldete_nutzer


    
    headers2={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    freigabezähler=0
    if len(personen_webex_meeting)<10:
        for eintrag1 in personen_webex_meeting:
            for eintrag2 in daten_gemeldete_nutzer:
                if eintrag1[0] == eintrag2["klarname"]:
      
                    for eintrag3 in fächer_id_array:            
                        payload={

                            "LicenceId":eintrag2["licenceId"],
                            "ExaminationpartId":eintrag3,
                            "IsReleased":bool(1)

                        }
                        payload=json.dumps(payload)
                        url= f"https://fub.lplus-teststudio.de/publicapi/v1/candidates/{eintrag2['userDetailId']}/releases/"
                        r = requests.post(url, headers=headers2, data=payload)

                        json_data = json.loads(r.text)

                        if r.status_code==200:
                            eintrag1[2]="✔️"
                            freigabezähler+=1
                            eintrag1.append(eintrag2["matrikelnummer"])
                            eel.progess_freigegebene_prüfungen(1)
                            
                        else:
                            pass
                 
    if len(personen_webex_meeting)>=10:

        pieces = 10
        new_arrays = np.array_split(personen_webex_meeting, pieces)

        
        def freigabe_thread(array):
            global freigabezähler
            for eintrag1 in array:
                for eintrag2 in daten_gemeldete_nutzer:
                    if eintrag1[0] == eintrag2["klarname"]:
                    
                        for eintrag3 in fächer_id_array:            
                            payload={

                                "LicenceId":eintrag2["licenceId"],
                                "ExaminationpartId":eintrag3,
                                "IsReleased":bool(1)

                            }
                            payload=json.dumps(payload)
                            url= f"https://fub.lplus-teststudio.de/publicapi/v1/candidate/{eintrag2['userDetailId']}/releases/"
                            r = requests.post(url, headers=headers2, data=payload)

                            json_data = json.loads(r.text)
                    
                            if r.status_code==200:
                                freigabezähler+=1
                                eel.freigegebene_prüfungen_anzahl(1)
                                for eintrag in personen_webex_meeting:
                                    if eintrag2["klarname"] in eintrag[0]:
                                        eintrag.append(eintrag2["matrikelnummer"])
                                        eintrag[2]="✔️"

                            else:
                                pass
 
        threads = []
        for i in range(0,10):
            threads.append(Thread(target=freigabe_thread, args=(new_arrays[i],)))
            threads[-1].start()
        for thread in threads:
            thread.join()
        
    personen_webex_meeting.sort()
    excel_download_liste=personen_webex_meeting

    excel_download_liste=daten_gemeldete_nutzer
    
    if personen_webex_meeting!=[]:
        for eintrag in excel_download_liste:
            for i in personen_webex_meeting:
                print( eintrag["klarname"],i[0])
                if eintrag["klarname"] == i[0]: 
                    eintrag["Webex anwesend"]="Ja"
                    print("hier")
                    eintrag["Prüfung freigegeben"]="Ja"

                else:
                    eintrag["Webex anwesend"]="Nein"
                    eintrag["Prüfung freigegeben"]="Nein"
    else:
        for eintrag in excel_download_liste:
            eintrag["Webex anwesend"]="Nein"
    print(excel_download_liste)

    return personen_webex_meeting,freigabezähler
            

@eel.expose
def übersicht_anzahl_kandidaten(lizenz_id_übersicht,fächer_id_array_übersicht):
    lizenz_id=lizenz_id_übersicht
    fächer_id_array=fächer_id_array_übersicht
    while "|" in lizenz_id:
        lizenz_id=lizenz_id[1:]

    zähler=-1
    for eintrag in fächer_id_array:
        zähler+=1
        while "|" in fächer_id_array[zähler]:
            fächer_id_array[zähler]=fächer_id_array[zähler][1:]

    r = requests.get(f"https://fub.lplus-teststudio.de/publicapi/v1/licences/{lizenz_id}/candidateRelations", 
    headers=headers)

    daten_gemeldete_nutzer=json.loads(r.text)
    anzahl_prüflinge=0
    anzahl_fächer_freigaben=0

    for eintrag in daten_gemeldete_nutzer:
        anzahl_prüflinge+=1

        for fach in eintrag["examinationPartIds"]:
            if str(fach) in fächer_id_array:
                anzahl_fächer_freigaben+=1

    return [anzahl_prüflinge,anzahl_fächer_freigaben]

@eel.expose
def alle_prüfungen_freigeben(lizenz_id,fächer_id_array):
    global freigabezähler,personen_webex_meeting,excel_download_liste

    if 'personen_webex_meeting' not in globals():
        personen_webex_meeting=[]

    while "|" in lizenz_id:
        lizenz_id=lizenz_id[1:]

    zähler=-1
    for eintrag in fächer_id_array:
        zähler+=1
        while "|" in fächer_id_array[zähler]:
            fächer_id_array[zähler]=fächer_id_array[zähler][1:]
    
    r = requests.get(f"https://fub.lplus-teststudio.de/publicapi/v1/licences/{lizenz_id}/candidateRelations", 
    headers=headers)

    daten_gemeldete_nutzer=json.loads(r.text)

    if len(daten_gemeldete_nutzer)<10:
        for eintrag in daten_gemeldete_nutzer:
            tn_id=eintrag["userDetailId"]
            r = requests.get(f"https://fub.lplus-teststudio.de/publicapi/v1/candidate/{tn_id}", 
            headers=headers)
            
            if r.status_code==200:
                eel.progess_abgerufene_personen(1)

            tn_name=json.loads(r.text)

            matrikelnummer=tn_name["importKey"]
            eintrag.update({"matrikelnummer":matrikelnummer})

            if not isinstance(tn_name["firstName"], str):
                tn_name["firstName"]=""
            if not isinstance(tn_name["lastName"], str):
                tn_name["lastName"]=""
            tn_klarname=tn_name["firstName"]+" "+tn_name["lastName"]
            tn_name=tn_name["userName"]
 
            eintrag.update({"tn_name":tn_name})
            eintrag.update({"klarname":tn_klarname})

    
    if len(daten_gemeldete_nutzer)>=10:
        pieces = 10
        new_arrays = np.array_split(daten_gemeldete_nutzer, pieces)


        master_liste_gemeldete_nutzer=[]

        def nutzernamen_ziehen(array):
            daten_gemeldete_nutzer1=array
            for eintrag in daten_gemeldete_nutzer1:

                tn_id=eintrag["userDetailId"]
                r = requests.get(f"https://fub.lplus-teststudio.de/publicapi/v1/candidate/{tn_id}", 
                headers=headers)

                if r.status_code==200:
                    eel.progess_abgerufene_personen(1)

                tn_name=json.loads(r.text)

                matrikelnummer=tn_name["importKey"]
                eintrag.update({"matrikelnummer":matrikelnummer})

                if not isinstance(tn_name["firstName"], str):
                    tn_name["firstName"]=""
                if not isinstance(tn_name["lastName"], str):
                    tn_name["lastName"]=""
                tn_klarname=tn_name["firstName"]+" "+tn_name["lastName"]
                tn_name=tn_name["userName"]

                eintrag.update({"tn_name":tn_name})
                eintrag.update({"klarname":tn_klarname})
                master_liste_gemeldete_nutzer.append(eintrag)

        threads = []
        for i in range(0,10):
            threads.append(Thread(target=nutzernamen_ziehen, args=(new_arrays[i],)))
            threads[-1].start()
        for thread in threads:
            thread.join()
    
        daten_gemeldete_nutzer=master_liste_gemeldete_nutzer
    

    headers2={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    freigabezähler=0
    if len(daten_gemeldete_nutzer)<10:
        for eintrag2 in daten_gemeldete_nutzer:
                
            for eintrag3 in fächer_id_array:            
                payload={

                    "LicenceId":eintrag2["licenceId"],
                    "ExaminationpartId":eintrag3,
                    "IsReleased":bool(1)

                }
                payload=json.dumps(payload)
                url= f"https://fub.lplus-teststudio.de/publicapi/v1/candidate/{eintrag2['userDetailId']}/releases/"
                r = requests.post(url, headers=headers2, data=payload)

                json_data = json.loads(r.text)
        
                if r.status_code==200:
                    freigabezähler+=1
                    eel.progess_freigegebene_prüfungen(1)

                    for eintrag in personen_webex_meeting:
                        if eintrag2["klarname"] == eintrag[0]:
                            eintrag[2]="✔️"

                else:
                    pass
    
    if len(daten_gemeldete_nutzer)>=10:
        pieces = 10
        new_arrays = np.array_split(daten_gemeldete_nutzer, pieces)

        def freigabe_thread(array):
            global freigabezähler
            for eintrag2 in array:
                for eintrag3 in fächer_id_array:            
                    payload={

                        "LicenceId":eintrag2["licenceId"],
                        "ExaminationpartId":eintrag3,
                        "IsReleased":bool(1)

                    }
                    payload=json.dumps(payload)
                    url= f"https://fub.lplus-teststudio.de/publicapi/v1/candidate/{eintrag2['userDetailId']}/releases/"
                    r = requests.post(url, headers=headers2, data=payload)

                    json_data = json.loads(r.text)
            
                    if r.status_code==200:
                        freigabezähler+=1
                        eel.progess_freigegebene_prüfungen(1)

                        for eintrag in personen_webex_meeting:
                            if eintrag2["klarname"] == eintrag[0]:
                                eintrag[2]="✔️"

                    else:
                        pass

        threads = []
        for i in range(0,10):
            threads.append(Thread(target=freigabe_thread, args=(new_arrays[i],)))
            threads[-1].start()
        for thread in threads:
            thread.join()  


    personen_webex_meeting.sort()
    
    excel_download_liste=daten_gemeldete_nutzer
    
    if personen_webex_meeting!=[]:
        for eintrag in excel_download_liste:
            for i in personen_webex_meeting:
                if eintrag["klarname"] == i[0]: 
                    eintrag["Webex anwesend"]="Ja"
                    eintrag["Prüfung freigegeben"]="Ja"

                else:
                    eintrag["Webex anwesend"]="Nein"
                    eintrag["Prüfung freigegeben"]="Ja"
    else:
        for eintrag in excel_download_liste:
            eintrag["Webex anwesend"]="Nein"
            eintrag["Prüfung freigegeben"]="Ja"

    return personen_webex_meeting,freigabezähler

@eel.expose
def anzeige_freigabeauswahl_confirm(lizenz_id_übersicht,fächer_id_array_übersicht):
    text=f"Auswahl: \nLizenz: {lizenz_id_übersicht}"
    for i in fächer_id_array_übersicht:
        text=text+f"\n      - Fach: {i}"
    
    return text


@eel.expose
def alle_prüfungen_zurückziehen(lizenz_id_übersicht,fächer_id_array_übersicht_zurückziehen):
    global freigabezähler_zurückziehen,freigabezähler_zurückziehen_tatsächlich
    
    while "|" in lizenz_id_übersicht:
        lizenz_id_übersicht=lizenz_id_übersicht[1:]

    zähler=-1
    for eintrag in fächer_id_array_übersicht_zurückziehen:
        zähler+=1
        while "|" in fächer_id_array_übersicht_zurückziehen[zähler]:
            fächer_id_array_übersicht_zurückziehen[zähler]=fächer_id_array_übersicht_zurückziehen[zähler][1:]


    r = requests.get(f"https://fub.lplus-teststudio.de/publicapi/v1/licences/{lizenz_id_übersicht}/candidateRelations", 
    headers=headers)

    daten_gemeldete_nutzer=json.loads(r.text)


    headers2={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    freigabezähler_zurückziehen=0
    freigabezähler_zurückziehen_tatsächlich=0

    if len(daten_gemeldete_nutzer)<10:
        for eintrag2 in daten_gemeldete_nutzer:
                
            for eintrag3 in fächer_id_array_übersicht_zurückziehen:            
                payload={

                    "LicenceId":eintrag2["licenceId"],
                    "ExaminationpartId":eintrag3,
                    "IsReleased":bool(0)

                }
                payload=json.dumps(payload)
                url= f"https://fub.lplus-teststudio.de/publicapi/v1/candidate/{eintrag2['userDetailId']}/releases/"
                r = requests.post(url, headers=headers2, data=payload)

                json_data = json.loads(r.text)
                

                if r.status_code==200:
                    freigabezähler_zurückziehen+=1
                    eel.progess_abgerufene_personen_zurückziehen(1)
                    if json_data["countResettedExamRelease"]!=0:
                        freigabezähler_zurückziehen_tatsächlich+=1
                        eel.progess_zurückgezogene_prüfungen(1)
                
                    

                else:
                    pass


    if len(daten_gemeldete_nutzer)>=10:
        pieces = 10
        new_arrays = np.array_split(daten_gemeldete_nutzer, pieces)

        def zurückziehen(array):
            global freigabezähler_zurückziehen,freigabezähler_zurückziehen_tatsächlich
            for eintrag2 in array:
                    
                for eintrag3 in fächer_id_array_übersicht_zurückziehen:            
                    payload={

                        "LicenceId":eintrag2["licenceId"],
                        "ExaminationpartId":eintrag3,
                        "IsReleased":bool(0)

                    }
                    payload=json.dumps(payload)
                    url= f"https://fub.lplus-teststudio.de/publicapi/v1/candidate/{eintrag2['userDetailId']}/releases/"
                    r = requests.post(url, headers=headers2, data=payload)

                    json_data = json.loads(r.text)
            
                    if r.status_code==200:
                        freigabezähler_zurückziehen+=1
                        eel.progess_abgerufene_personen_zurückziehen(1)
                        if json_data["countResettedExamRelease"]!=0:
                            freigabezähler_zurückziehen_tatsächlich+=1
                            eel.progess_zurückgezogene_prüfungen(1)

                    else:
                        pass

        threads = []
        for i in range(0,10):
            threads.append(Thread(target=zurückziehen, args=(new_arrays[i],)))
            threads[-1].start()
        for thread in threads:
            thread.join()

@eel.expose
def zurückziehen_übersicht(lizenz_id_übersicht,fächer_id_array_übersicht_zurückziehen):
    print(lizenz_id_übersicht,fächer_id_array_übersicht_zurückziehen)

    text=f"Sollen alle Teilnehmer:innen für folgende Auswahl zurückgezogen werden: \nLizenz: {lizenz_id_übersicht}"
    for i in fächer_id_array_übersicht_zurückziehen:
        text=text+f"\n      - Fach: {i}"
    
    return text

@eel.expose
def excelliste_generieren(meeting_auswahl):
    header = ['Name', 'Matrikelnummer', 'In Webex anwesend',"Prüfung freigegeben"]
    datum=datetime.now().strftime("%Y-%m-%d")
    meeting_name_csv=f"Meeting_{meeting_auswahl}_{datum}.csv"
    
    #for eintrag in excel_download_liste:
    if len(excel_download_liste[0])>4:
        with open(meeting_name_csv, 'w+', newline='') as myfile:
            wr = csv.writer(myfile,delimiter=";")
            wr.writerow(header)
            for eintrag in excel_download_liste:
                daten=[eintrag["klarname"],eintrag["matrikelnummer"],eintrag["Webex anwesend"],eintrag["Prüfung freigegeben"]]
                wr.writerow(daten)

    elif len(excel_download_liste[0])<=4:
        with open(meeting_name_csv, 'w+', newline='') as myfile:
            wr = csv.writer(myfile,delimiter=";")
            wr.writerow(header)
            for eintrag in excel_download_liste:

                if "✔️" in eintrag:
                    anwesend="Ja"
                else:
                    anwesend="Nein"
                
                if eintrag[-1]=="❌":
                    eintrag[-1]=""

                daten=[eintrag[0],eintrag[-1],anwesend]

                wr.writerow(daten)

    erfolgreich=True
    return erfolgreich


eel.start("index.html",size=(1200, 830))
