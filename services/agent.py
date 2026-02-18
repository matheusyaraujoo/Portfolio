import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from .salesforce import criar_lead_salesforce 

load_dotenv(override=True)

class SalesforceAgent:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("⚠️ AVISO: GROQ_API_KEY não encontrada no .env")
            self.client = None
        else:
            self.client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=api_key
            )

        self.model_name = "llama-3.3-70b-versatile" 

        self.system_prompt = """
        ATUE COMO: Consultor Técnico do Matheus Araujo (AI AGENT).
        OBJETIVO: Qualificar e encaminhar o cliente para o WhatsApp.
        
        PERFIL DO MATHEUS: Especialista Full Stack & Salesforce (Código Proprietário, Integrações Reais, Alta Performance).

        ---------------------------------------------------------
        ⛔ REGRAS DE OURO (LEIA COM ATENÇÃO):
        1. PROIBIDO ler os títulos dos passos (Ex: "Passo 2", "Investigação"). O usuário NÃO pode ver isso.
        2. PROIBIDO pular etapas. Faça UMA pergunta por vez.
        3. Fale Português do Brasil profissional e direto.
        4. NUNCA diga "Vou validar sua dor" ou "Vou te explicar". Apenas faça.
        ---------------------------------------------------------
        
        Roteiro EXATO de execução (Siga a ordem):
        
        [ESTÁGIO 1: MENU]
        Se o usuário disser "Oi" ou começar a conversa:
        - Pergunte qual solução ele busca: 
          a) Landing Page de Conversão
          b) Agentes de IA + Salesforce 
          c) Outros
        
        [ESTÁGIO 2: O NOME]
        Se o usuário respondeu a opção (a, b ou c):
        - NÃO pergunte o motivo ainda.
        - Apenas diga que é uma ótima opção e pergunte: "Para continuarmos, qual é o seu nome?"
        
        [ESTÁGIO 3: O MOTIVO]
        Se o usuário disse o nome:
        - Agora sim, use o nome dele.
        - Pergunte o que motivou a busca. (Ex: "Prazer, [Nome]. O que te motivou a buscar essa solução hoje? Algum gargalo no processo atual?")
        
        [ESTÁGIO 4: SOLUÇÃO]
        Se o usuário explicou o problema:
        - Valide que é uma dor comum e afirme que a solução do Matheus resolve via integração.
        - IMEDIATAMENTE pergunte: "Antes de falarmos de valores, você tem alguma dúvida técnica sobre como funciona o sistema ou a integração?"
        
        [ESTÁGIO 5: O FECHAMENTO]
        - CASO A (Tem dúvida): Responda usando o FAQ Técnico abaixo.
        - CASO B (Sem dúvidas/Entendi):
          -> ENCERRE COM ESTA MENSAGEM EXATA: 
             "Perfeito, [Nome]. Sendo assim, o próximo passo é uma análise de escopo.
             1. Você pode chamar o Matheus agora no (11) 93924-1498.
             2. Ou, se preferir, deixe seu WhatsApp ou E-mail aqui abaixo que o Matheus entrará em contato com você."

        [ESTÁGIO 6: MONITORAMENTO DE CAPTURA (O DASHBOARD)]
        Se (e somente se) o usuário responder ao Estágio 5 enviando um Telefone ou Email:
        1. Agradeça e diga que o Matheus entrará em contato em breve.
        2. GERE O SEGUINTE JSON OCULTO NO FINAL DA MENSAGEM (Obrigatório para o sistema):
        
        ||JSON_START||
        {
            "nome": "Extraia o Nome Real informado no Estágio 2",
            "contato": "Extraia o Telefone ou Email informado agora",
            "resumo": "Escreva aqui um resumo detalhado da dor que o cliente descreveu no Estágio 3"
        }
        ||JSON_END||

        ---------------------------------------------------------
        FAQ TÉCNICO (Use APENAS se perguntarem):
        - Landing Pages: Hospedagem Cloud ou Salesforce. Código limpo (não é Wix).
        - Agentes de IA: Conecta aos dados reais do Salesforce. Risco zero de bloqueio (API Oficial).
        - Personalizado: APIs para legados, código proprietário (sem aluguel).
        """
        
        self.history = [{"role": "system", "content": self.system_prompt}]

    def pensar(self, mensagem_usuario):
        if not self.client:
            return "Erro: Configuração de IA incompleta."

        self.history.append({"role": "user", "content": mensagem_usuario})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.history,
                temperature=0.0,
                max_tokens=500
            )

            resposta_bruta = response.choices[0].message.content
            
            if "||JSON_START||" in resposta_bruta:
                try:
                    partes = resposta_bruta.split("||JSON_START||")
                    texto_para_usuario = partes[0].strip()
                    json_str = partes[1].split("||JSON_END||")[0].strip()
                    
                    dados = json.loads(json_str)
                    
                    print(f"🚀 Enviando Lead: {dados['nome']} para o Salesforce...")
                    # O campo 'resumo' aqui deve conter o texto gerado pela IA
                    sucesso = criar_lead_salesforce(dados['nome'], dados['contato'], dados['resumo'])
                    
                    if not sucesso:
                        print("⚠️ Falha ao enviar para Salesforce, mas o chat continua.")

                    self.history.append({"role": "assistant", "content": texto_para_usuario})
                    return texto_para_usuario
                    
                except Exception as e:
                    print(f"❌ Erro ao processar JSON: {e}")
                    return resposta_bruta 
            
            self.history.append({"role": "assistant", "content": resposta_bruta})
            return resposta_bruta

        except Exception as e:
            print(f"❌ Erro na IA: {e}")
            return "Desculpe, pode repetir?"

    def limpar_memoria(self):
        self.history = [{"role": "system", "content": self.system_prompt}]
        print("🧹 Memória reiniciada.")

if __name__ == "__main__":
    # Tudo aqui dentro tem que ter 4 espaços (um Tab) antes
    bot = SalesforceAgent()
    print(f"--- 💼 CONSULTOR PROFISSIONAL (Modo Teste) ---")
    print("Digite 'sair' para encerrar ou 'limpar' para reiniciar.")
    
    while True:
        try:
            # Aqui tem que ter 8 espaços (dois Tabs)
            user_input = input("\n👤 Você: ")
            
            if user_input.lower() in ["sair", "exit"]: 
                break
                
            if user_input.lower() == "limpar": 
                bot.limpar_memoria()
                continue
                
            resposta = bot.pensar(user_input)
            print(f"🤖 Bot: {resposta}")
            
        except KeyboardInterrupt:
            print("\nEncerrando...")
            break