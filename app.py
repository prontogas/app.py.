import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 🔧 ÁREA DE CONFIGURAÇÃO (MEXA AQUI!) ---
# Coloque aqui quanto VOCÊ paga no produto (Preço de Custo)
CUSTOS_PRODUTOS = {
    "Gás P13": 82.00,     
    "Água 20L": 4.80,     
    "Outros": 0.00        
}
# --------------------------------------------

# Configuração da página
st.set_page_config(page_title="Gestor Pronto Gás", layout="wide")
st.title("🚀 Gestor Pronto Gás (Com Estoque)")

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
            st.markdown("### Detalhes do Pedido")
            cliente = st.text_input("Nome do Cliente") # <--- CAMPO NOVO
            produto_selecionado = st.selectbox("Produto", list(CUSTOS_PRODUTOS.keys()))
            qtd = st.number_input("Quantidade", min_value=1, value=1, step=1) # <--- CAMPO NOVO
            
            st.markdown("### Financeiro")
            # Atenção: Aqui você coloca o VALOR TOTAL que o cliente pagou
            valor_venda = st.number_input("Valor TOTAL Recebido (R$)", min_value=0.0, step=1.0, value=105.00)
            pagamento = st.selectbox("Forma Pagamento", ["Dinheiro", "Pix", "Cartão", "Fiado"])
            endereco = st.text_input("Endereço/Bairro")
            obs = st.text_input("Obs (Ex: Cliente novo)")
            
            submitted = st.form_submit_button("Lançar Venda")
            if submitted:
                # Ajuste de Fuso Horário (-3h para Brasil)
                hora_brasil = datetime.now() - timedelta(hours=3)
                
                # CÁLCULOS AUTOMÁTICOS
                custo_unitario = CUSTOS_PRODUTOS[produto_selecionado]
                custo_total = custo_unitario * qtd  # Multiplica o custo pela quantidade
                lucro_venda = valor_venda - custo_total
                
                st.session_state.vendas.append({
                    "Hora": hora_brasil.strftime("%H:%M"),
                    "Cliente": cliente,
                    "Produto": produto_selecionado,
                    "Qtd": qtd,
                    "Venda": valor_venda,
                    "Custo": custo_total,
                    "Lucro": lucro_venda,
                    "Pagamento": pagamento,
                    "Local": endereco,
                    "Obs": obs
                })
                st.success(f"Venda registrada! Lucro: R$ {lucro_venda:.2f}")

    elif tipo == "Despesa":
        st.info("Lance aqui gastos extras (Gasolina, Almoço, Panfletos)")
        with st.form("form_despesa"):
            desc_despesa = st.text_input("Descrição")
            valor_despesa = st.number_input("Valor (R$)", min_value=0.0, step=1.0)
            categoria = st.selectbox("Categoria", ["Combustível", "Alimentação", "Veículo", "Outros"])
            
            submitted_d = st.form_submit_button("Lançar Despesa")
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

# Transformar dados em tabelas
df_vendas = pd.DataFrame(st.session_state.vendas)
df_despesas = pd.DataFrame(st.session_state.despesas)

# Cálculos Totais
total_faturado = df_vendas["Venda"].sum() if not df_vendas.empty else 0.0
total_custos_produtos = df_vendas["Custo"].sum() if not df_vendas.empty else 0.0
total_despesas_extras = df_despesas["Valor"].sum() if not df_despesas.empty else 0.0

# Lucro Real = (Vendas - Custo dos Produtos) - Despesas Extras
lucro_liquido = total_faturado - total_custos_produtos - total_despesas_extras

with col1:
    st.metric("💰 Faturamento (Caixa)", f"R$ {total_faturado:.2f}")
with col2:
    st.metric("📉 Custos + Despesas", f"R$ {(total_custos_produtos + total_despesas_extras):.2f}")
with col3:
    st.metric("💵 Lucro Líquido (Bolso)", f"R$ {lucro_liquido:.2f}", delta_color="normal")

st.markdown("---")

# Tabelas Detalhadas
col_E, col_D = st.columns(2)

with col_E:
    st.subheader("📋 Histórico de Vendas")
    if not df_vendas.empty:
        # Mostra as colunas novas (Cliente e Qtd)
        colunas_para_mostrar = ["Hora", "Cliente", "Produto", "Qtd", "Venda", "Lucro", "Local"]
        # Filtrar apenas as colunas que existem (para evitar erro se a tabela estiver vazia de campos)
        st.dataframe(df_vendas[colunas_para_mostrar], use_container_width=True)
    else:
        st.info("Nenhuma venda hoje.")

with col_D:
    st.subheader("💸 Gastos Extras")
    if not df_despesas.empty:
        st.dataframe(df_despesas, use_container_width=True)
    else:
        st.info("Nenhum gasto extra lançado.")

st.markdown("---")

# --- CÉREBRO DA IA ---
if not df_vendas.empty:
    st.header("🧠 Copie para o Especialista de Vendas")
    
    # Contagem de produtos vendidos
    resumo_produtos = df_vendas["Produto"].value_counts().to_string()
    
    prompt_ia = f"""
    Aja como meu Gerente de Negócios. Aqui está o fechamento de hoje:
    
    FINANCEIRO:
    - Faturamento Total: R$ {total_faturado:.2f}
    - Custo das Mercadorias: R$ {total_custos_produtos:.2f}
    - Despesas Operacionais: R$ {total_despesas_extras:.2f}
    - LUCRO LÍQUIDO REAL: R$ {lucro_liquido:.2f}
    
    DETALHE DAS VENDAS (Com Clientes):
    {df_vendas.to_string(index=False)}
    
    Analise e me diga:
    1. Quem foi o melhor cliente do dia?
    2. Minha margem de lucro hoje está saudável?
    3. Pelo horário e local, qual a estratégia para amanhã?
    """
    
    st.text_area("Texto pronto para análise:", value=prompt_ia, height=250)


               


  




    
    



  




 
