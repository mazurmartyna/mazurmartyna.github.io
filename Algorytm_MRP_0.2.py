#lt - czas realizacji
czas_realizacji_0 = 1
na_stanie_0 = 2
BOM = {
    "Długopis": {"children": [("Obudowa",1), ("Wkład",1), ("Końcówka",1), ("Mechanizm",1)], "lt":1},
    "Obudowa": {"children": [], "lt":2},
    "Wkład": {"children": [("Tusz",1)], "lt":2},
    "Końcówka": {"children": [("Kulka",1)], "lt":1},
    "Mechanizm": {"children": [("Sprężynka",1)], "lt":2},
    "Tusz": {"children": [], "lt":1},
    "Kulka": {"children": [], "lt":1},
    "Sprężynka": {"children": [], "lt":1}
}

# Algorytm GHP 
def ghp(popyt, na_stanie):
    n = len(popyt)
    
    produkcja = [0] * n
    dostepne = [0] * n
    
    # Tydzien 0
    dostepne[0] =  na_stanie - popyt[0]

    if dostepne[0] < 0:
        brak = -dostepne[0]
        produkcja[0] += brak
        dostepne[0] += brak


    # Kolejne Tygodnie
    for t in range(1, n):
        dostepne[t] = dostepne[t-1] - popyt[t] 

        if dostepne[t] < 0:
            brak = -dostepne[t]
            produkcja[t] += brak
            
            dostepne[t] += brak
    
    return produkcja, dostepne

# Algorytm MRP

def mrp (popyt, lt, na_stanie, wielkosc_partii):
    n = len(popyt)

    zapotrz_net = [0] * n # net_req / zapotrzebowanie net
    dostepne = [0] * n # projected / przew. na stanie
    planowane_zamowienia = [0] * n
    planowane_przyjęcia_zam = [0] * n
    
    dostepne[0] =  na_stanie - popyt[0]

    if dostepne[0] < 0:
        zapotrz_net[0] = -dostepne[0]
        
        planowane_przyjęcia_zam[0] = wielkosc_partii
        planowane_zamowienia[max(0, 0-lt)] = wielkosc_partii
        dostepne[0] += wielkosc_partii

    for t in range(1, n):
        dostepne[t] = dostepne[t-1] + planowane_przyjęcia_zam[t] - popyt[t]

        if dostepne[t] < 0:
            zapotrz_net[t] = -dostepne[t]
            planowane_przyjęcia_zam[t] = wielkosc_partii

            tydzien_zamowienia = max(0, t - lt)
            planowane_zamowienia[tydzien_zamowienia] += wielkosc_partii

            dostepne[t] += wielkosc_partii

    return {
        "calkowite_zapotrzebowanie": popyt,
        "przewidywane_na_stanie": dostepne,
        "zapotrzebowanie_netto": zapotrz_net,
        "planowane_zamowienia": planowane_zamowienia,
        "planowane_przyjecia": planowane_przyjęcia_zam
    }

def run_mrp(product, produkcja_ghp, BOM, na_stanie, wielkosc_partii):
    results = {}

    def licz_element(item, zapotrzebowanie):
        lt = BOM[item]["lt"]

        dane = mrp(zapotrzebowanie, lt, na_stanie.get(item,0), wielkosc_partii.get(item,1))
        results[item] = dane

        planned_orders = dane["planowane_zamowienia"]

        for child, qty in BOM[item]["children"]:
            child_gross = [0] * len(zapotrzebowanie)

            for t in range(len(zapotrzebowanie)):
                if planned_orders[t]>0:
                   child_gross[t] += planned_orders[t] * qty

            licz_element(child, child_gross)

    # poziom 0 → poziom 1
    for child, qty in BOM[product]["children"]:
        child_gross = [0]*len(produkcja_ghp)

        for t in range(len(produkcja_ghp)):
            if produkcja_ghp[t] > 0:
                t_child = max(0, t - BOM[product]["lt"])
                child_gross[t_child] += produkcja_ghp[t] * qty

        licz_element(child, child_gross)

    return results

# Wizualizacja 

def drukuj_tabele_ghp(popyt, czas_realizacji, na_stanie, produkcja, dostepne):
    n = len(popyt)

    print("GHP")
    print("")

    print("Okres            ||", end=" ")
    for i in range(n):
        print(f"{i+1:3}", end=" ")
    print()

    print("Popyt            ||", end=" ")
    for x in popyt:
        print(f"{x:3}", end=" ")
    print()

    print("Produkcja        ||", end=" ")
    for x in produkcja:
        print(f"{x:3}", end=" ")
    print()

    print("Dostępne         ||", end=" ")
    for x in dostepne:
        print(f"{x:3}", end=" ")
    print()

    print("\nParametry:")
    print("Czas realizacji =", czas_realizacji)
    print("Stan początkowy =", na_stanie)
    
def drukuj_tabele_MRP(nazwa, dane):
    n = len(dane["calkowite_zapotrzebowanie"])

    print(f"\n{nazwa}")
    print("Okres              ||", end=" ")
    for i in range(n):
        print(f"{i+1:3}", end=" ")
    print()

    print("Całkowite zapotrz. ||", end=" ")
    for x in dane["calkowite_zapotrzebowanie"]:
        print(f"{x:3}", end=" ")
    print()

    
    print("Przewidywane stan  ||", end=" ")
    for x in dane["przewidywane_na_stanie"]:
        print(f"{x:3}", end=" ")
    print()

    print("Zapotrzebowanie net||", end=" ")
    for x in dane["zapotrzebowanie_netto"]:
        print(f"{x:3}", end=" ")
    print()

    print("Planowane zamów.   ||", end=" ")
    for x in dane["planowane_zamowienia"]:
        print(f"{x:3}", end=" ")
    print()
    
    print("Planowane przyjęcia||", end=" ")
    for x in dane["planowane_przyjecia"]:
        print(f"{x:3}", end=" ")
    print()

popyt = [0,0,0,0,20,0,40,0,0,0] # popyt w podanych tygodniach na poziomie 0

na_stanie = {
    "Długopis": 2,
    "Wkład": 22,
    "Tusz": 0
}

wielkosc_partii = {
    "Długopis": 40,
    "Wkład": 40,
    "Tusz": 50,
    "Obudowa": 40,
    "Końcówka": 40,
    "Kulka": 50,
    "Mechanizm": 40,
    "Sprężynka": 50
}


czas_realizacji = {
    "Długopis": cz_r_Dlugopis,
    "Wkład": cz_r_Wklad,
    "Tusz": cz_r_Tusz,
    "Obudowa": cz_r_Obudowa,
    "Końcówka": cz_r_Koncowka,
    "Kulka": cz_r_Kulka,
    "Mechanizm": cz_r_Mechanizm,
    "Sprężynka": cz_r_Sprezynka
}

produkcja, dostepne = ghp(popyt, na_stanie["Długopis"])
wyniki = run_mrp("Długopis", produkcja, BOM, na_stanie, wielkosc_partii)

drukuj_tabele_ghp(popyt, czas_realizacji_0, na_stanie_0, produkcja, dostepne)
for nazwa, dane in wyniki.items():
    drukuj_tabele_MRP(nazwa,dane)
