import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Gerenciador de Vendas & IA", layout="wide")
st.title("🚀 Painel de Controle de Vendas")

# Inicializar banco de dados temporário na sessão
if 'vendas' not in st.session_state:
    st.session_state.vendas = []
if 'despesas' not in st.session_state:
    st.session_state.despesas = []

# --- BARRA LATERAL (Lançamentos) ---
with st.sidebar:
    st.header("📝 Novo Lançamento")
    tipo = st.radio("O que vamos lançar?", ["Venda", "Despesa"])

    if tipo == "Venda":
        with st.form("form_venda"):
            produto = st.text_input("Produto")
            valor = st.number_input("Valor (R$)", min_value=0.0, step=1.0)
            pagamento = st.selectbox("Forma Pagamento", ["Dinheiro", "Pix", "Cartão", "Fiado"])
            endereco = st.text_input("Endereço/Bairro")
            obs = st.text_input("Obs (Ex: Cliente novo)")
            
            submitted = st.form_submit_button("Lançar Venda")
            if submitted:
                st.session_state.vendas.append({
                    "Hora": datetime.now().strftime("%H:%M"),
                    "Produto": produto,
                    "Valor": valor,
                    "Pagamento": pagamento,
                    "Local": endereco,
                    "Obs": obs
                })
                st.success("Venda registrada!")

    elif tipo == "Despesa":
        with st.form("form_despesa"):
            desc_despesa = st.text_input("Descrição da Despesa")
            valor_despesa = st.number_input("Valor (R$)", min_value=0.0, step=1.0)
            categoria = st.selectbox("Categoria", ["Combustível", "Alimentação", "Fornecedor", "Outros"])
            
            submitted_d = st.form_submit_button("Lançar Despesa")
            if submitted_d:
                st.session_state.despesas.append({
                    "Hora": datetime.now().strftime("%H:%M"),
                    "Descrição": desc_despesa,
                    "Valor": valor_despesa,
                    "Categoria": categoria
                })
                st.success("Despesa registrada!")

# --- ÁREA PRINCIPAL (Visualização) ---

col1, col2 = st.columns(2)

# Converter listas para Tabelas (DataFrames)
df_vendas = pd.DataFrame(st.session_state.vendas)
df_despesas = pd.DataFrame(st.session_state.despesas)

with col1:
    st.subheader("💰 Vendas do Dia")
    if not df_vendas.empty:
        st.dataframe(df_vendas, use_container_width=True)
        total_vendas = df_vendas["Valor"].sum()
        st.metric("Total Bruto", f"R$ {total_vendas:.2f}")
    else:
        st.info("Nenhuma venda lançada hoje.")

with col2:
    st.subheader("💸 Despesas do Dia")
    if not df_despesas.empty:
        st.dataframe(df_despesas, use_container_width=True)
        total_despesas = df_despesas["Valor"].sum()
        st.metric("Total Despesas", f"R$ {total_despesas:.2f}")
    else:
        st.info("Nenhuma despesa lançada hoje.")

st.markdown("---")

# --- A MÁGICA DA IA ---
st.header("🧠 Análise do Especialista")

if not df_vendas.empty:
    lucro = df_vendas["Valor"].sum() - (df_despesas["Valor"].sum() if not df_despesas.empty else 0)
    
    # Criar o texto pronto para a IA
    prompt_ia = f"""
    Aja como meu Especialista em Estratégia de Vendas.
    Aqui está o resumo do meu dia de hoje:
    
    RESUMO FINANCEIRO:
    - Faturamento: R$ {df_vendas["Valor"].sum():.2f}
    - Despesas: R$ {(df_despesas["Valor"].sum() if not df_despesas.empty else 0):.2f}
    - Lucro Líquido: R$ {lucro:.2f}
    
    DETALHE DAS VENDAS:
    {df_vendas.to_string(index=False)}
    
    DETALHE DAS DESPESAS:
    {df_despesas.to_string(index=False) if not df_despesas.empty else "Sem despesas"}
    
    Por favor, analise esses dados e me dê:
    1. Uma análise do desempenho hoje (pontos fortes e fracos).
    2. Identifique padrões no endereço ou forma de pagamento.
    3. 3 Ações práticas para eu vender mais amanhã.
    """

    st.text_area("Copie este texto abaixo e envie para sua IA (ChatGPT/Gemini):", value=prompt_ia, height=300)
    
else:
    st.warning("Lance pelo menos uma venda para gerar a análise.")
