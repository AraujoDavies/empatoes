from os import getenv

from dotenv import load_dotenv
from helpers import *

load_dotenv("ligas.env")

try:
    ligas = eval(getenv("LIGAS"))

    print(f"JOGOS DO DIA {datetime.now().strftime('%d/%m/%Y')}")

    for liga_url in ligas:
        liga_alias = liga_url[0]
        liga_url = liga_url[1]

        print(liga_alias)

        soup = obj_soup_league(liga_url)

        empatoes = encontrar_equipes(soup)

        entradas_confirmadas = analisar_jogos(soup, empatoes)

        for match in entradas_confirmadas:
            if match["home_units_to_bet"] + match["away_units_to_bet"] == 2:
                print(
                    f"{match['mandante']} VS {match['visitante']} - rodada: {match['rodada']} - ODD BETFAIR: {match['odd']}"
                )
            elif match["home_units_to_bet"] == 1:
                print(
                    f"{match['mandante']} - rodada: {match['rodada']} - ODD BETFAIR: {match['odd']}"
                )
            elif match["away_units_to_bet"] == 1:
                print(
                    f"{match['visitante']} - rodada: {match['rodada']} - ODD BETFAIR: {match['odd']}"
                )

        print("-------------------------------")
finally:
    input("")