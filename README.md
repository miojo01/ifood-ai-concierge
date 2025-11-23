# 🚀 Agentes Inteligentes (Delivery)

> Este projeto demonstra o uso de **Agentes Autônomos**, **RAG** e **Análise de Dados com IA**.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![LangChain](https://img.shields.io/badge/Framework-LangChain-green)
![Gemini](https://img.shields.io/badge/AI-Gemini%202.0%20Flash-orange)

## 📂 O que tem neste repositório?

Este repositório contém **duas soluções distintas** focadas em dores reais dos Deliveries:

### 1. 🍔 Concierge de Pedidos (`app.py`)
Um assistente de delivery que simula o fluxo completo de um pedido.
* **Destaque:** Memória persistente, validação de cardápio e cálculo de preços.
* **Tecnologia:** Structured Tool Chat (Agentes).

### 2. 📈 Analista de Parceiros (`dashboard.py`)
Uma IA analítica capaz de ler planilhas de vendas e gerar insights visuais.
* **Destaque:** Geração automática de código Python e Gráficos (Matplotlib) via comando de texto.
* **Tecnologia:** Pandas DataFrame Agent (LangChain Experimental).

---

## 📦 Como Rodar Localmente

1. Clone o repositório:
```bash
git clone [https://github.com/miojo01/ifood-ai-concierge](https://github.com/miojo01/ifood-ai-concierge)
cd ifood-ai-concierge
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Escolha qual projeto quer rodar:
```bash
streamlit run app.py
ou
streamlit run dashboard.py
```

4. Configuração da API Key:
- O app abrirá no navegador.
- Insira sua Google API Key na barra lateral.
- O sistema utiliza o modelo gemini-2.0-flash.