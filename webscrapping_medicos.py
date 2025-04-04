import requests
import json
import pandas as pd

especialidades = {
    "Pediatria": "58",
    "Cardiologia": "17",
    "Psiquiatria": "39",
    "Dermatologia": "18",
    "Ortopedia": "46",
    "Ginecologia": "25",
    "Oftalmologia": "31",
    "Neurologia": "35",
    "Endocrinologia": "22",
    "Gastroenterologia": "23"
}

def get_especialidade_code(nome_especialidade):
    return especialidades.get(nome_especialidade.capitalize(), None)

def get_medico_detalhes(crm, uf, security_hash):
    url_detalhes = "https://portal.cfm.org.br/api_rest_php/api/v1/medicos/buscar_foto/"

    payload = [{"securityHash": security_hash, "crm": crm, "uf": uf}]
    print("Payload enviado para buscar_foto:", json.dumps(payload, indent=2, ensure_ascii=False))

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response_detalhes = requests.post(url_detalhes, data=json.dumps(payload), headers=headers)

    print(f"Status Code buscar_foto: {response_detalhes.status_code}")

    if response_detalhes.status_code == 200:
        try:
            data_detalhes = response_detalhes.json()
            print("Resposta JSON da API buscar_foto:", json.dumps(data_detalhes, indent=2, ensure_ascii=False))

            if "dados" in data_detalhes and isinstance(data_detalhes["dados"], list) and len(data_detalhes["dados"]) > 0:
                medico_info = data_detalhes["dados"][0]
                return {
                    "Telefone": medico_info.get("TELEFONE", "Não disponível"),
                    "Endereço": medico_info.get("ENDERECO", "Não disponível")
                }
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON da resposta da API buscar_foto.")

    print(f"Erro ao buscar detalhes do médico {crm}/{uf}.")
    return {"Telefone": "Erro", "Endereço": "Erro"}

def salvar_para_excel(dados, estado, especialidade):
    df = pd.DataFrame(dados)
    nome_arquivo = f'{estado}_{especialidade}.xlsx'
    df.to_excel(nome_arquivo, index=False)
    print(f"Arquivo '{nome_arquivo}' salvo com sucesso!")
    files.download(nome_arquivo)

nome_especialidade = "Psiquiatria"
codigo_especialidade = get_especialidade_code(nome_especialidade)
estado = "MG"
nome = "ABADIA GILDA BUSO MATOSO"

if codigo_especialidade:
    url = 'https://portal.cfm.org.br/api_rest_php/api/v1/medicos/buscar_medicos'

    payload = [
        {
            "useCaptchav2": False,
            "captcha": "",
            "medico": {
                "nome": nome,
                "ufMedico": estado,
                "crmMedico": "",
                "municipioMedico": "",
                "tipoInscricaoMedico": "",
                "situacaoMedico": "",
                "detalheSituacaoMedico": "",
                "especialidadeMedico": "",
                "areaAtuacaoMedico": ""
            },
            "page": 1,
            "pageNumber": 1,
            "pageSize": 100
        }
    ]

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers)

    print(f"Status Code buscar_medicos: {response.status_code}")

    if response.status_code == 200:
        try:
            data = response.json()
            print("Resposta JSON da API buscar_medicos:", json.dumps(data, indent=2, ensure_ascii=False))

            if "dados" in data and isinstance(data["dados"], list):
                lista_medicos = []
                for medico in data["dados"]:
                    nome = medico.get("NM_MEDICO", "Não disponível")
                    crm = medico.get("NU_CRM", "Não disponível")
                    uf = medico.get("SG_UF", "Não disponível")
                    especialidade = medico.get("ESPECIALIDADE", "Não disponível")
                    security_hash = medico.get("SECURITYHASH", "")

                    detalhes = get_medico_detalhes(crm, uf, security_hash)

                    lista_medicos.append({
                        "Nome": nome,
                        "CRM": crm,
                        "Estado": uf,
                        "Especialidade": especialidade,
                        "Telefone": detalhes["Telefone"],
                        "Endereço": detalhes["Endereço"]
                    })

                salvar_para_excel(lista_medicos, estado, nome_especialidade)
            else:
                print("Nenhum médico encontrado com os parâmetros fornecidos.")
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON da resposta da API buscar_medicos.")
    else:
        print(f"Erro ao acessar a API: {response.status_code}")
else:
    print(f"Especialidade '{nome_especialidade}' não encontrada.")
