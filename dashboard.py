import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="iFood Data Analyst", page_icon="📈", layout="wide")
st.title("📈 iFood Partner - Analista de Vendas (IA)")

# --- 2. SEGURANÇA / AUTENTICAÇÃO ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Cole sua Google API Key", type="password")

if not api_key:
    st.warning("⚠️ Configuração necessária. Adicione a chave no secrets.toml ou na lateral.")
    st.stop()

# --- 3. CARREGAR DADOS ---
arquivo_csv = "vendas.csv"
try:
    df = pd.read_csv(arquivo_csv)
    
    # Mostra um pedacinho da tabela na barra lateral
    with st.sidebar.expander("👀 Ver Dados Brutos"):
        st.dataframe(df)
        
except FileNotFoundError:
    st.error(f"Erro: O arquivo '{arquivo_csv}' não foi encontrado. Crie ele na pasta do projeto!")
    st.stop()

# --- 4. CÉREBRO ---
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", 
        temperature=0, 
        google_api_key=api_key
    )
    
    # Prompt de Sistema Reforçado
    instrucoes = """
    Você é um Analista de Dados Expert.
    1. O dataframe pandas já existe e se chama `df`. NÃO tente criar dados novos.
    2. Se o usuário pedir gráfico: USE 'matplotlib.pyplot'.
    3. IMPORTANTE: Nunca escreva 'Final Answer' e 'Action' na mesma resposta.
    4. Se for gerar código, gere APENAS o código. Espere a execução para depois comentar.
    """

    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        allow_dangerous_code=True,
        handle_parsing_errors=True, # Tenta corrigir sozinho se errar
        prefix=instrucoes,
        agent_type="openai-tools", # Força um modo mais estruturado
    )
except Exception as e:
    # Se der erro no openai-tools, tentamos o padrao
    try:
        agent = create_pandas_dataframe_agent(
            llm,
            df,
            verbose=True,
            allow_dangerous_code=True,
            handle_parsing_errors=True,
            prefix=instrucoes
        )
    except:
        st.error(f"Erro crítico ao criar agente: {e}")
        st.stop()

# --- 5. CHAT ---
st.write("### 🤖 Pergunte para a sua planilha")
st.caption("Dica: Peça cálculos ('Qual faturamento total?') ou gráficos ('Gere um gráfico de barras por categoria').")

# Mantemos o histórico visual simples na tela
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe mensagens anteriores
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])
    # Se tiver gráfico salvo na mensagem, exibe (logica avançada simplificada aqui)

if prompt := st.chat_input("Digite sua pergunta de negócio..."):
    # Adiciona pergunta do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisando dados e gerando código Python..."):
            try:
                # O agente executa e retorna a resposta em texto
                response = agent.invoke(prompt)
                output_text = response["output"]
                
                st.write(output_text)
                st.session_state.messages.append({"role": "assistant", "content": output_text})
                
                # --- DETECTOR DE GRÁFICOS ---
                # O agente do Pandas cria gráficos usando matplotlib internamente (plt).
                # O Streamlit precisa de um comando explícito para mostrar o que está na memória do plt.
                fig = plt.gcf() # Pega a figura atual
                if fig and fig.get_axes(): # Se tiver eixos desenhados
                    st.pyplot(fig) # Mostra no site
                    plt.clf() # Limpa para o próximo
            except Exception as e:
                st.error(f"Erro na análise: {e}")