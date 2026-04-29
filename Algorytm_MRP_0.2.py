import json 

popyt = [int(x) for x in popyt]

BOM = {
    "Dlugopis": {"children": [("Obudowa",1), ("Wklad",1), ("Koncowka",1), ("Mechanizm",1)], "lt":cz_r_Dlugopis},
    "Obudowa": {"children": [], "lt":cz_r_Obudowa},
    "Wklad": {"children": [("Tusz",1)], "lt":cz_r_Wklad},
    "Koncowka": {"children": [("Kulka",1)], "lt": cz_r_Koncowka},
    "Mechanizm": {"children": [("Sprezynka",1)], "lt":cz_r_Mechanizm},
    "Tusz": {"children": [], "lt":cz_r_Tusz},
    "Kulka": {"children": [], "lt":cz_r_Kulka},
    "Sprezynka": {"children": [], "lt":cz_r_Sprezynka}
}

na_stanie = {
    "Dlugopis": ns_Dlugopis,
    "Wklad": ns_Wklad,
    "Tusz": ns_Tusz,
    "Obudowa": ns_Obudowa,
    "Koncowka": ns_Koncowka,
    "Kulka": ns_Kulka,
    "Mechanizm": ns_Mechanizm,
    "Sprezynka": ns_Sprezynka
}

wielkosc_partii = {
    "Dlugopis": w_p_Dlugopis,
    "Wklad": w_p_Wklad,
    "Tusz": w_p_Tusz,
    "Obudowa": w_p_Obudowa,
    "Koncowka": w_p_Koncowka,
    "Kulka": w_p_Kulka,
    "Mechanizm": w_p_Mechanizm,
    "Sprezynka": w_p_Sprezynka
}

def ghp(popyt, na_stanie):
    n = len(popyt)
    
    produkcja = [0] * n
    dostepne = [0] * n
    
    dostepne[0] =  na_stanie - popyt[0]

    if dostepne[0] < 0:
        brak = -dostepne[0]
        produkcja[0] += brak
        dostepne[0] += brak

    for t in range(1, n):
        dostepne[t] = dostepne[t-1] - popyt[t] 

        if dostepne[t] < 0:
            brak = -dostepne[t]
            produkcja[t] += brak
            
            dostepne[t] += brak
    
    return produkcja, dostepne

def mrp (popyt, lt, na_stanie, wielkosc_partii):
    n = len(popyt)

    zapotrz_net = [0] * n 
    plan_przyjecia = [0] * n
    dostepne = [0] * n 
    planowane_zamowienia = [0] * n
    planowane_przyjęcia_zam = [0] * n
    
    dostepne[0] =  na_stanie - popyt[0]

    if dostepne[0] < 0:
        zapotrz_net[0] = -dostepne[0]
        
        if 0 - lt < 0:
            plan_przyjecia[0] += wielkosc_partii
        else: 
            planowane_przyjęcia_zam[0] += wielkosc_partii;
            planowane_zamowienia[0-lt] += wielkosc_partii
        
        dostepne[0] += wielkosc_partii

    for t in range(1, n):

        dostepne[t] = dostepne[t-1] + planowane_przyjęcia_zam[t] + plan_przyjecia[t] - popyt[t]

        if dostepne[t] < 0:
            zapotrz_net[t] = -dostepne[t]

            if t-lt < 0:
                plan_przyjecia[t] += wielkosc_partii
            else:
                planowane_przyjęcia_zam[t] += wielkosc_partii
                planowane_zamowienia[t-lt] += wielkosc_partii

            dostepne[t] += wielkosc_partii

    return {
    "okresy": list(range(1, n+1)),
    "values": {
        "Calkowite zapotrzebowanie": popyt,
        "Planowane przyjecia": plan_przyjecia,
        "Przewidywane na stanie": dostepne,
        "Zapotrzebowanie netto": zapotrz_net,
        "Planowane zamowienia": planowane_zamowienia,
        "Planowane przyjecia zamowien": planowane_przyjęcia_zam
    }
}

def run_mrp(product, produkcja_ghp, BOM, na_stanie, wielkosc_partii):
    results = {}

    def licz_element(item, zapotrzebowanie):
        lt = BOM[item]["lt"]

        dane = mrp(zapotrzebowanie, lt, na_stanie.get(item,0), wielkosc_partii.get(item,1))
        results[item] = dane

        planned_orders = dane["values"]["Planowane zamowienia"]

        for child, qty in BOM[item]["children"]:
            child_gross = [0] * len(zapotrzebowanie)

            for t in range(len(zapotrzebowanie)):
                if planned_orders[t]>0:
                   child_gross[t] += planned_orders[t] * qty

            licz_element(child, child_gross)

    for child, qty in BOM[product]["children"]:
        child_gross = [0]*len(produkcja_ghp)

        for t in range(len(produkcja_ghp)):
            if produkcja_ghp[t] > 0:
                t_child = max(0, t - BOM[product]["lt"])
                child_gross[t_child] += produkcja_ghp[t] * qty

        licz_element(child, child_gross)

    return results


produkcja, dostepne = ghp(popyt, na_stanie["Dlugopis"])

mrp_wyniki = run_mrp("Dlugopis", produkcja, BOM, na_stanie, wielkosc_partii)

output = {
    "GHP": {
        "okresy": list(range(1, len(popyt)+1)),
        "values": {
            "Przewidywany popyt": popyt,
            "Produkcja": produkcja,
            "Dostępne": dostepne
        }
    },
    **mrp_wyniki
}