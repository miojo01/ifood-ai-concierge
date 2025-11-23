import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import tool
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
import random

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="iFood AI Concierge", page_icon="🍔")
st.title("🍔 iFood Concierge - Pedidos")

# --- CONFIGURAÇÃO DE SEGURANÇA ---
# Tenta pegar a chave dos segredos do sistema (Produção/Local seguro)
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    # Se não achar (ex: rodando na máquina de alguém sem config), pede na tela
    api_key = st.sidebar.text_input("Cole sua Google API Key", type="password")

if not api_key:
    st.warning("⚠️ Configuração de API necessária.")
    st.stop()

# --- 2. DADOS E MEMÓRIA ---
MENU = {
    "X-Burger": 25.00,
    "Pizza": 45.00,
    "Refrigerante": 8.00,
    "Açaí": 18.00
}

# Inicialização do Session State para persistência de dados durante reruns do Streamlit
if "PEDIDOS" not in st.session_state:
    st.session_state["PEDIDOS"] = {}

# --- 3. FERRAMENTAS ---
@tool
def ver_cardapio(dummy: str = None):
    return str(MENU)

@tool
def fazer_pedido(pedido_texto: str):
    try:
        if "," in pedido_texto:
            item, qtd = pedido_texto.split(",")
        else:
            item = pedido_texto
            qtd = 1
            
        item = item.strip()
        # Tratamento simples para remover 'x' se o usuario digitar '2x burguer'
        item = item.replace("x ", "").replace("X ", "")
        qtd = int(str(qtd).strip())
        
        # Correção para capitalização (x-burger -> X-Burger)
        # Procura o item no menu ignorando maiúsculas/minúsculas
        item_no_menu = None
        for menu_item in MENU:
            if menu_item.lower() in item.lower():
                item_no_menu = menu_item
                break
        
        if item_no_menu:
            item = item_no_menu
        else:
            return f"Erro: Não temos '{item}'. Consulte o cardápio."

    except:
        return "Erro: Formato inválido. Tente 'Item, Quantidade'."

    # Geração de ID e persistência no Session State
    id_p = str(random.randint(100, 999))
    total = MENU[item] * qtd
    
    st.session_state["PEDIDOS"][id_p] = {"item": item, "qtd": qtd, "status": "Cozinhando 🔥"}
    
    return f"Pedido #{id_p} ({qtd}x {item}) confirmado! Total: R$ {total}"

@tool
def ver_status(id_pedido: str):
    #Consulta o status atual de um pedido baseado no ID numérico.
    id_pedido = str(id_pedido).strip().replace("#", "")
    
    pedidos_db = st.session_state["PEDIDOS"]
    
    if id_pedido in pedidos_db:
        return f"Pedido #{id_pedido}: {pedidos_db[id_pedido]['status']}"
    return f"Pedido #{id_pedido} não encontrado. Pedidos ativos: {list(pedidos_db.keys())}"

tools = [ver_cardapio, fazer_pedido, ver_status]

# --- 4. CÉREBRO ---
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", 
        google_api_key=api_key, 
        temperature=0
    )
except Exception as e:
    st.error(f"Erro IA: {e}")
    st.stop()

agent_executor = initialize_agent(
    tools=tools, 
    llm=llm, 
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

# --- 5. CHAT ---
msgs = StreamlitChatMessageHistory(key="chat_memoria_fixa")
if len(msgs.messages) == 0:
    msgs.add_ai_message("Oi! Sou o iFood Concierge. O que vai querer? 🍔")

for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

if input_user := st.chat_input("Digite aqui..."):
    st.chat_message("human").write(input_user)
    with st.chat_message("ai"):
        try:
            resp = agent_executor.run(input_user)
            
            resp = resp.replace("R$", "Reais ").replace("$", "")
            
            msgs.add_user_message(input_user)
            msgs.add_ai_message(resp)
            st.write(resp)
        except Exception as e:
            st.error(f"Erro: {e}")