import os
import requests
from simple_salesforce import Salesforce
from dotenv import load_dotenv

load_dotenv()

def get_salesforce_connection():
    consumer_key = os.getenv("SF_CONSUMER_KEY")
    consumer_secret = os.getenv("SF_CONSUMER_SECRET")
    domain = os.getenv("SF_DOMAIN")

    if not all([consumer_key, consumer_secret, domain]): 
        print("❌ CONFIG ERRO: Faltam variáveis no .env")
        return None

    token_url = f"{domain}/services/oauth2/token"
    payload = {
        'grant_type': 'client_credentials',
        'client_id': consumer_key,
        'client_secret': consumer_secret
    }

from simple_salesforce import Salesforce
import requests

def get_salesforce_connection():
    try:
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        auth_data = response.json()

        sf = Salesforce(
            instance_url=auth_data['instance_url'],
            session_id=auth_data['access_token']
        )

        # adiciona header para ativar regra de atribuição
        sf.headers.update({'Sforce-Auto-Assign': 'TRUE'})

        return sf

    except Exception as e:
        print(f"❌ Erro Auth Salesforce: {e}")
        return None


def criar_lead_salesforce(nome, contato, resumo):
    sf = get_salesforce_connection()
    if not sf:
        return False

def criar_lead_salesforce(nome, contato, resumo):
    sf = get_salesforce_connection()
    if not sf: return False

    try:
        partes_nome = nome.strip().split(' ')
        first_name = partes_nome[0]
        last_name = ' '.join(partes_nome[1:]) if len(partes_nome) > 1 else 'Lead'

        if not resumo or len(resumo) < 3 or resumo == "-":
            descricao_final = f"CONTATO: {contato} (Cliente não detalhou a dor)"
        else:
            descricao_final = f"RESUMO IA:\n{resumo}\n\nCONTATO: {contato}"

        novo_lead = {
            'FirstName': first_name,
            'LastName': last_name,
            'Company': 'Portfolio Lead', 
            'Phone': contato,
            'Description': descricao_final,
            'LeadSource': 'Other',
            'Status': 'Open - Not Contacted'
        }

        print(f"📡 Tentando criar lead: {first_name} | {contato}")
        resultado = sf.Lead.create(novo_lead)
        
        if resultado.get('success'):
            print(f"✅ SUCESSO! Lead criado. ID: {resultado.get('id')}")
            return True
        
        print("❌ Salesforce recusou.")
        return False

    except Exception as e:
        print(f"❌ Erro Crítico Python: {e}")
        return False