import os
import re
import time
import requests

from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm


# ============================================================
# CAPÍTULOS QUE VOCÊ QUER BAIXAR
# ============================================================
#
# Coloque aqui SOMENTE os capítulos que deseja.
#
# Exemplos:
#
# "86"
# "100"
# "167.1"
# "167.2"
#
# Não precisa colocar os links.
# O programa monta os links automaticamente.
#
# A ordem abaixo será mantida.

CAPITULOS = [
"1",
"2",
"3",
"4",
"5",
"6",
"7",
"8",
"9",
"10",
"11",
"12",
"13",
"14",
"15",
"16",
"17",
"18",
"19",
"20",
"21",
"22",
"23",
"24",
"25",
"26",
"27",
"28",
"29",
"30",
"31",
"32",
"33",
"34",
"35",
"36",
"37",
"38",
"39",
"40",
"41",
"42",
"43",
"44",
"45",
"46",
"47",
"48",
"49",
"50",
"51",
"52",
"53",
"54",
"55",
"56",
"57",
"58",
"59",
"60",
"61",
"62",
"63",
"64",
"65",
"66",
"67",
"68",
"69",
"70",
"71",
"72",
"73",
"74",
"75",
"76",
"77",
"78",
"79",
"80",
"81",
"82",
"83",
"84",
"85",
"86",
"87",
"88",
"89",
"90",
"91",
"92",
"93",
"94",
"95",
"96",
"97",
"98",
"99",
"100",
"101",
"102",
"103",
"104",
"105",
"106",
"107",
"108",
"109",
"110",
"111",
"112",
"113",
"114",
"115",
"116",
"117",
"118",
"119",
"120",
"121",
"122",
"123",
"124",
"125",
"126",
"127",
"128",
"129",
"130",
"131",
"132",
"133",
"134",
"135",
"136",
"137",
"138",
"139",
"140",
"140.1",
"140.2",
"141",
"142",
"143",
"144",
"145",
"146",
"147",
"148",
"149",
"150",
"151",
"152",
"153",
"154",
"155",
"156",
"157",
"158",
"159",
"160",
"161",
"162",
"162.2",
"163",
"164",
"165",
"166",
"167",
"167.1",
"167.2",
"168",
"169",
"170",
]


# ============================================================
# SITE
# ============================================================

SITE = (
    "https://mangalivre.to/"
    "manga/gachiakuta-ptbr"
)


# ============================================================
# PASTA PRINCIPAL
# ============================================================

PASTA_PRINCIPAL = "Gachiakuta"


# ============================================================
# TEMPOS
# ============================================================

TEMPO_INICIAL = 5
TEMPO_ROLAGEM = 2


# ============================================================
# TENTATIVAS DE DOWNLOAD
# ============================================================

MAX_TENTATIVAS = 3


# ============================================================
# HEADERS
# ============================================================

HEADERS = {

    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/149.0 Safari/537.36"
    )
}


# ============================================================
# MONTA OS LINKS AUTOMATICAMENTE
# ============================================================

URLS = [

    f"{SITE}/capitulo-{capitulo}/"

    for capitulo in CAPITULOS

]


# ============================================================
# NOME DA PASTA
# ============================================================

def nome_do_capitulo(numero):

    nome = f"capitulo-{numero}"

    nome = re.sub(
        r'[<>:"/\\|?*]',
        "_",
        nome
    )

    return nome


# ============================================================
# ENCONTRA AS IMAGENS
# ============================================================

def encontrar_imagens(driver):

    imagens = driver.find_elements(
        "tag name",
        "img"
    )

    urls = []

    for imagem in imagens:

        atributos = [

            "src",
            "data-src",
            "data-lazy-src",
            "data-original",
            "data-url"

        ]

        url = None

        for atributo in atributos:

            valor = imagem.get_attribute(
                atributo
            )

            if (
                valor
                and valor.startswith("http")
            ):

                url = valor

                break

        if not url:
            continue

        # Ignora imagens pequenas
        # como logos e ícones.

        try:

            largura = imagem.size["width"]
            altura = imagem.size["height"]

            if (
                largura < 200
                or altura < 200
            ):
                continue

        except Exception:

            pass

        if url not in urls:

            urls.append(url)

    return urls


# ============================================================
# CARREGA TODAS AS IMAGENS
# ============================================================

def carregar_todas_as_imagens(driver):

    print(
        "      Carregando imagens..."
    )

    altura_anterior = 0

    tentativas_sem_mudanca = 0

    while True:

        driver.execute_script(
            "window.scrollTo("
            "0, "
            "document.body.scrollHeight"
            ");"
        )

        time.sleep(
            TEMPO_ROLAGEM
        )

        altura_atual = driver.execute_script(
            "return document.body.scrollHeight"
        )

        if altura_atual == altura_anterior:

            tentativas_sem_mudanca += 1

        else:

            tentativas_sem_mudanca = 0

        altura_anterior = altura_atual

        if tentativas_sem_mudanca >= 3:

            break

    # Volta para o começo.

    driver.execute_script(
        "window.scrollTo(0, 0);"
    )

    time.sleep(2)


# ============================================================
# BAIXA UMA IMAGEM
# ============================================================

def baixar_imagem(
    session,
    url,
    nome_arquivo
):

    for tentativa in range(
        1,
        MAX_TENTATIVAS + 1
    ):

        try:

            resposta = session.get(
                url,
                timeout=30
            )

            resposta.raise_for_status()

            imagem = Image.open(
                BytesIO(
                    resposta.content
                )
            )

            if imagem.mode != "RGB":

                imagem = imagem.convert(
                    "RGB"
                )

            imagem.save(
                nome_arquivo,
                "JPEG",
                quality=95
            )

            imagem.close()

            return True

        except Exception as erro:

            if tentativa >= MAX_TENTATIVAS:

                print()

                print(
                    f"      ✗ Falhou após "
                    f"{MAX_TENTATIVAS} tentativas:"
                )

                print(
                    f"        {erro}"
                )

            else:

                time.sleep(2)

    return False


# ============================================================
# BAIXA TODAS AS IMAGENS DO CAPÍTULO
# ============================================================

def baixar_imagens(
    urls_imagens,
    pasta_capitulo,
    url_capitulo
):

    arquivos = []

    session = requests.Session()

    session.headers.update({

        **HEADERS,

        "Referer": url_capitulo

    })


    # ========================================================
    # BARRA DE PROGRESSO DAS PÁGINAS
    # ========================================================

    barra = tqdm(

        enumerate(
            urls_imagens,
            start=1
        ),

        total=len(urls_imagens),

        desc="      Páginas",

        unit=" pág",

        ncols=85

    )


    for numero, url in barra:

        nome_arquivo = os.path.join(

            pasta_capitulo,

            f"{numero:03d}.jpg"

        )


        # ====================================================
        # SE JÁ EXISTE, NÃO BAIXA NOVAMENTE
        # ====================================================

        if os.path.exists(
            nome_arquivo
        ):

            arquivos.append(
                nome_arquivo
            )

            barra.set_postfix(
                status="já existe"
            )

            continue


        # ====================================================
        # DOWNLOAD
        # ====================================================

        sucesso = baixar_imagem(

            session,

            url,

            nome_arquivo

        )


        if sucesso:

            arquivos.append(
                nome_arquivo
            )

            barra.set_postfix(
                status="OK"
            )

        else:

            barra.set_postfix(
                status="ERRO"
            )


    barra.close()

    return arquivos


# ============================================================
# CRIA PDF
# ============================================================

def criar_pdf(
    arquivos,
    pasta_capitulo,
    nome_capitulo
):

    if not arquivos:

        return False


    caminho_pdf = os.path.join(

        pasta_capitulo,

        f"{nome_capitulo}.pdf"

    )


    # ========================================================
    # SE O PDF JÁ EXISTE, NÃO CRIA NOVAMENTE
    # ========================================================

    if os.path.exists(
        caminho_pdf
    ):

        print(
            "      ✓ PDF já existe."
        )

        return True


    print(
        "      Criando PDF..."
    )


    imagens = []


    for arquivo in arquivos:

        try:

            imagem = Image.open(
                arquivo
            )

            if imagem.mode != "RGB":

                imagem = imagem.convert(
                    "RGB"
                )

            imagens.append(
                imagem
            )

        except Exception as erro:

            print(
                f"      Erro ao abrir "
                f"{arquivo}: {erro}"
            )


    if not imagens:

        return False


    # ========================================================
    # SALVA PDF
    # ========================================================

    primeira = imagens[0]


    primeira.save(

        caminho_pdf,

        "PDF",

        resolution=150.0,

        save_all=True,

        append_images=imagens[1:]

    )


    # Fecha as imagens.

    for imagem in imagens:

        imagem.close()


    return True


# ============================================================
# CONFIGURA O CHROME
# ============================================================

options = Options()


# ============================================================
# CHROME EM SEGUNDO PLANO
# ============================================================
#
# O navegador não vai abrir uma janela visível.
#
# Você pode continuar usando o computador normalmente.
#
# Se quiser VER o Chrome trabalhando, coloque # na frente:
#
# # options.add_argument("--headless=new")
#

options.add_argument(
    "--headless=new"
)

options.add_argument(
    "--window-size=1920,1080"
)

options.add_argument(
    "--disable-notifications"
)

options.add_argument(
    "--disable-gpu"
)


# ============================================================
# CRIA PASTA PRINCIPAL
# ============================================================

os.makedirs(

    PASTA_PRINCIPAL,

    exist_ok=True

)


# ============================================================
# INICIA CHROME
# ============================================================

driver = webdriver.Chrome(

    options=options

)


# ============================================================
# CONTADORES
# ============================================================

capitulos_ok = 0

capitulos_erro = 0

capitulos_pulados = 0

total_paginas = 0

erros = []


# ============================================================
# BARRA DE PROGRESSO DOS CAPÍTULOS
# ============================================================

barra_capitulos = tqdm(

    enumerate(
        URLS,
        start=1
    ),

    total=len(URLS),

    desc="CAPÍTULOS",

    unit=" cap",

    ncols=85

)


# ============================================================
# PROCESSAMENTO
# ============================================================

try:

    for indice, url in barra_capitulos:

        numero_capitulo = CAPITULOS[
            indice - 1
        ]


        # ====================================================
        # NOME DO CAPÍTULO
        # ====================================================

        nome_capitulo = nome_do_capitulo(

            numero_capitulo

        )


        # ====================================================
        # PASTA DO CAPÍTULO
        # ====================================================

        pasta_capitulo = os.path.join(

            PASTA_PRINCIPAL,

            nome_capitulo

        )


        os.makedirs(

            pasta_capitulo,

            exist_ok=True

        )


        # ====================================================
        # CAMINHO DO PDF
        # ====================================================

        caminho_pdf = os.path.join(

            pasta_capitulo,

            f"{nome_capitulo}.pdf"

        )


        # ====================================================
        # SE JÁ EXISTE, PULA
        # ====================================================

        if os.path.exists(
            caminho_pdf
        ):

            capitulos_pulados += 1

            barra_capitulos.set_postfix(

                cap=numero_capitulo,

                status="já baixado"

            )

            continue


        # ====================================================
        # ABRE CAPÍTULO
        # ====================================================

        barra_capitulos.set_postfix(

            cap=numero_capitulo,

            status="abrindo"

        )


        driver.get(

            url

        )


        time.sleep(

            TEMPO_INICIAL

        )


        # ====================================================
        # CARREGA IMAGENS
        # ====================================================

        barra_capitulos.set_postfix(

            cap=numero_capitulo,

            status="carregando"

        )


        carregar_todas_as_imagens(

            driver

        )


        # ====================================================
        # ENCONTRA IMAGENS
        # ====================================================

        urls_imagens = encontrar_imagens(

            driver

        )


        if not urls_imagens:

            capitulos_erro += 1

            erros.append(

                numero_capitulo

            )

            barra_capitulos.set_postfix(

                cap=numero_capitulo,

                status="SEM IMAGENS"

            )

            continue


        # ====================================================
        # BAIXA IMAGENS
        # ====================================================

        barra_capitulos.set_postfix(

            cap=numero_capitulo,

            status=f"{len(urls_imagens)} páginas"

        )


        arquivos = baixar_imagens(

            urls_imagens,

            pasta_capitulo,

            url

        )


        total_paginas += len(

            arquivos

        )


        if not arquivos:

            capitulos_erro += 1

            erros.append(

                numero_capitulo

            )

            barra_capitulos.set_postfix(

                cap=numero_capitulo,

                status="ERRO"

            )

            continue


        # ====================================================
        # CRIA PDF
        # ====================================================

        sucesso = criar_pdf(

            arquivos,

            pasta_capitulo,

            nome_capitulo

        )


        if sucesso:

            capitulos_ok += 1

            barra_capitulos.set_postfix(

                cap=numero_capitulo,

                status="CONCLUÍDO"

            )

        else:

            capitulos_erro += 1

            erros.append(

                numero_capitulo

            )

            barra_capitulos.set_postfix(

                cap=numero_capitulo,

                status="PDF ERRO"

            )


finally:

    barra_capitulos.close()

    driver.quit()


# ============================================================
# RESUMO FINAL
# ============================================================

print()

print(
    "=" * 70
)

print(
    "                    FINALIZADO"
)

print(
    "=" * 70
)

print()

print(
    f"✓ Capítulos concluídos: "
    f"{capitulos_ok}"
)

print(
    f"↻ Já existentes:        "
    f"{capitulos_pulados}"
)

print(
    f"✗ Capítulos com erro:   "
    f"{capitulos_erro}"
)

print(
    f"📄 Páginas baixadas:    "
    f"{total_paginas}"
)


# ============================================================
# MOSTRA CAPÍTULOS COM ERRO
# ============================================================

if erros:

    print()

    print(
        "Capítulos com erro:"
    )

    for erro in erros:

        print(
            f"  - {erro}"
        )


# ============================================================
# LOCAL DOS ARQUIVOS
# ============================================================

print()

print(
    "Pasta:"
)

print(
    os.path.abspath(
        PASTA_PRINCIPAL
    )
)

print()

print(
    "=" * 70
)

input(
    "Pressione ENTER para fechar..."
)