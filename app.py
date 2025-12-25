import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO DE CUSTOS (Quanto você paga no produto) ---
# Altere os valores abaixo conforme o seu custo real
CUSTOS_PRODUTOS = {
    "Gás P13": 75.00,    # Exemplo: Você paga 75
    "Água 20L": 6.00,    # Exemplo: Você paga 6
    "Outros": 0.00       # Outros produtos
}

# Configuração da página
st.set_page_config(page_title="Gestor Pronto Gás", layout="wide")
st.title("🚀 Gestor Pronto Gás & Clientes")

# Inicializar banco de dados na sessão
if 'vendas' not in st.session_state:
    st.session_state.vendas = []
if 'despesas' not in st.session_state:
    st.session_state.despesas = []

# --- BARRA LATERAL (Lançamentos) ---
with st.sidebar:
    st.header("📝 Novo Pedido")
    tipo = st.radio("Tipo de Lançamento", ["Venda", "Despesa"])

    if tipo == "Venda":
        with st.form("form_venda"):
            st.markdown("### 👤 Cliente")
            cliente_nome = st.text_input("Nome do Cliente")
            cliente_tel = st.text_input("WhatsApp/Telefone")
            
            st.markdown("### 🛒 Pedido")
            # Lista de produtos baseada nos custos configurados
            produto_selecionado = st.selectbox("Produto", list(CUSTOS_PRODUTOS.keys()))
            
            valor_venda = st.number_input("Valor da Venda (R$)", min_value=0.0, step=1.0, value=110.0 if "Gás" in produto_selecionado else 12.0)
            pagamento = st.selectbox("Forma Pagamento", ["Dinheiro", "Pix", "Cartão", "Fiado"])
            endereco = st.text_input("Endereço/Bairro")
            obs = st.text_input("Obs (Ex: Deixar na portaria)")
            
            submitted = st.form_submit_button("✅ Registrar Venda")
            
            if submitted:
                # Ajuste de Horário Brasil (-3h)
                hora_brasil = datetime.now() - timedelta(hours=3)
                
                # Calcular Lucro Automaticamente
                custo_produto = CUSTOS_PRODUTOS.get(produto_selecionado, 0.00)
                lucro_venda = valor_venda - custo_produto
                
                st.session_state.vendas.append({
                    "Hora": hora_brasil.strftime("%H:%M"),
                    "Cliente": cliente_nome,
                    "Telefone": cliente_tel,
                    "Produto": produto_selecionado,
                    "Valor Venda": valor_venda,
                    "Custo": custo_produto,
                    "Lucro Real": lucro_venda,
                    "Pagamento": pagamento,
                    "Local": endereco,
                    "Obs": obs
                })
                st.success(f"Venda para {cliente_nome} registrada! Lucro estimado: R$ {lucro_venda:.2f}")

    elif tipo == "Despesa":
        with st.form("form_despesa"):
            desc_despesa = st.text_input("Descrição (Ex: Gasolina)")
            valor_despesa = st.number_input("Valor (R$)", min_value=0.0, step=1.0)
            categoria = st.selectbox("Categoria", ["Combustível", "Alimentação", "Pessoal", "Outros"])
            
            submitted_d = st.form_submit_button("🔴 Registrar Despesa")
            if submitted_d:
                hora_brasil = datetime.now() - timedelta(hours=3)
                st.session_state.despesas.append({
                    "Hora": hora_brasil.strftime("%H:%M"),
                    "Descrição": desc_despesa,
                    "Valor": valor_despesa,
                    "Categoria": categoria
                })
                st.success("Despesa registrada!")

# --- ÁREA PRINCIPAL (Relatórios) ---

col1, col2, col3 = st.columns(3)

# Converter dados
df_vendas = pd.DataFrame(st.session_state.vendas)
df_despesas = pd.DataFrame(st.session_state.despesas)

# Cálculos Totais
total_vendas = df_vendas["Valor Venda"].sum() if not df_vendas.empty else 0.0
total_lucro_produtos = df_vendas["Lucro Real"].sum() if not df_vendas.empty else 0.0
total_despesas_extras = df_despesas["Valor"].sum() if not df_despesas.empty else 0.0
lucro_liquido_final = total_lucro_produtos - total_despesas_extras

with col1:
    st.metric("Faturamento (Bruto)", f"R$ {total_vendas:.2f}")
with col2:
    st.metric("Despesas do Dia", f"R$ {total_despesas_extras:.2f}")
with col3:
    # Mostra o lucro VERDADEIRO (Venda - Custo Produto - Despesas Extras)
    st.metric("Lucro Líquido Real", f"R$ {lucro_liquido_final:.2f}", delta_color="normal")

st.markdown("---")

# Tabelas Detalhadas
tab1, tab2 = st.tabs(["📄 Histórico de Vendas", "📉 Despesas"])

with tab1:
    if not df_vendas.empty:
        st.dataframe(df_vendas, use_container_width=True)
        # Botão para baixar cadastro de clientes
        csv = df_vendas.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Planilha do Dia (Excel)", data=csv, file_name="vendas_hoje.csv", mime="text/csv")
    else:
        st.info("Nenhuma venda hoje.")

with tab2:
    if not df_despesas.empty:
        st.dataframe(df_despesas, use_container_width=True)
    else:
        st.info("Sem despesas extras.")

st.markdown("---")

# --- IA ESPECIALISTA ---
st.header("🧠 Análise Estratégica")

if not df_vendas.empty:
    prompt_ia = f"""
    Aja como meu Gerente Comercial. Aqui estão os dados de hoje:
    
    FINANCEIRO REAL:
    - Vendeu: R$ {total_vendas:.2f}
    - Custo Produtos: R$ {total_vendas - total_lucro_produtos:.2f}
    - Despesas Extras: R$ {total_despesas_extras:.2f}
    - DINHEIRO NO BOLSO (LUCRO): R$ {lucro_liquido_final:.2f}
    
    CLIENTES ATENDIDOS HOJE:
    {df_vendas[['Cliente', 'Telefone', 'Produto', 'Local']].to_string(index=False)}
    
    Analise e me diga:
    1. Meu lucro real está saudável ou as despesas comeram tudo?
    2. Com base na lista de clientes, quem eu devo fidelizar?
    3. Qual a estratégia para amanhã?
    """
    st.text_area("Copie para a IA:", value=prompt_ia, height=250)

         
           




    
    



  




 
