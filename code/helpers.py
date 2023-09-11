from datetime import datetime
from time import sleep

import requests
from bs4 import BeautifulSoup


def trata_html(input: str) -> str:
    """
    Limpa o código HTML.

    Params:
        input -> código HTML

    Return:
        Código HTML limpo, sem espaços desproporcionais.
    """
    return " ".join(input.split()).replace("> <", "><")


def obj_soup_league(league_url: str) -> BeautifulSoup:
    """
    Raspa o código HTML e transforma em soup.

    Params:
        url de uma liga no casa de apostas.

    Return:
        Soup com HTML da liga.
    """
    r = requests.get(league_url)
    html = trata_html(r.text)
    soup = BeautifulSoup(html, "html.parser")
    return soup


def encontrar_equipes(soup) -> list:
    """
    Pega a tabela e verifica qual time é empatão (times com 25% ou mais de empates).

    Return:
        times qualificados como empatão.
    """
    times_qualificados = []

    tbodys = soup.findAll("tbody")
    table = tbodys[1]
    times = table.findAll("tr")

    # quem é empatão
    for time in times:
        linha_da_tabela = time.findAll("td")
        partidas_disputadas = int(
            0 if linha_da_tabela[3].text == "" else linha_da_tabela[3].text
        )
        qt_empates = int(
            0 if linha_da_tabela[5].text == "" else linha_da_tabela[5].text
        )
        nome_do_time = (
            linha_da_tabela[1].a["href"].split("/")[-2].replace("-", " ")
        )  # pegar nome sempre da url para evitar erros
        if qt_empates > partidas_disputadas * 0.25:
            times_qualificados.append(nome_do_time)

    return times_qualificados


def analisar_jogos(soup, empatoes: list) -> list:
    """
    Analisa cada jogo da rodada atual se está padrão de odd.

    Params:
        soup -> html da página em soup.

    Return:
        jogos confirmados
    """
    # Round Matchs
    round_table = soup.findAll("table")[2]
    matchs = round_table.findAll("tr")
    confirm_team = []

    # create a dict to analyze
    for match in matchs:
        match_details = match.findAll("td")
        home_team = (
            match_details[2].a["href"].split("/")[-2].replace("-", " ")
        )  # pegar nome sempre da url para evitar erros
        away_team = (
            match_details[4].a["href"].split("/")[-2].replace("-", " ")
        )  # pegar nome sempre da url para evitar erros
        versus = match_details[3].text == " vs "
        match_url = match_details[3].find("a").attrs["href"]
        possible_bet = {}
        match_day = int(match_details[1].text.split()[0].split(".")[0])

        # Only analyze if game is today
        if match_day != datetime.now().day:
            #     print(f'{home_team} x {away_team} - Day of the match: {match_day} (Will be analyze in the same day of the match.)')
            continue

        if versus and home_team in empatoes or away_team in empatoes:
            possible_bet["mandante"] = home_team
            possible_bet["visitante"] = away_team
            possible_bet["url"] = match_url
            possible_bet["rodada"] = soup.find("td", id="week-gr").span.text
            possible_bet["home_units_to_bet"] = 0
            possible_bet["away_units_to_bet"] = 0

            # Verify in DB if is gale necessary and set units
            if home_team in empatoes:
                possible_bet["home_units_to_bet"] = 1
            if away_team in empatoes:
                possible_bet["away_units_to_bet"] = 1

            confirm_team.append(possible_bet)

    retorna_jogos = []
    # print(confirm_team)
    for match_dict in confirm_team:
        try:
            match_request = requests.get(match_dict["url"])
            html = trata_html(match_request.text)
            soup = BeautifulSoup(html, "html.parser")

            tds = soup.find_all("td")
            odd_draw = float(
                tds[5].findAll("a", attrs={"aria-label": "betfair"})[2].text
            )

            match_dict["odd"] = odd_draw

            if odd_draw > 3:
                retorna_jogos.append(match_dict)
        except Exception as e:
            print(f"ERRO na analise (FAÇA MANUALMENTE) {match_dict['url']}")
        finally:
            sleep(3)

    return retorna_jogos
