
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ==========================================
# 🔧 ÁREA DE CONFIGURAÇÃO (MECHA AQUI!)
# ==========================================
# Coloque aqui quanto VOCÊ paga no produto (Preço de Custo)
CUSTOS_PRODUTOS = {
    "Gás P13": 82.00    # <--- MUDE ESSE VALOR PARA O SEU CUSTO REAL
    "Água 20L": 4.80,    # <--- MUDE ESSE VALOR PARA O CUSTO DA ÁGUA
    "Outros": 0.00
}
# ==========================================

# Configuração da página
st.set_page_config(page_title="Gestor Pronto Gás", layout="wide")
st.title("🚀 Gestor Pronto Gás (Com Estoque)")

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
            produto_selecionado = st.selectbox("Produto", list(CUSTOS_PRODUTOS.keys()))
            
            # NOVO: Campo de Quantidade
            col_qtd, col_val = st.columns(2)
            with col_qtd:
                quantidade = st.number_input("Qtd", min_value=1, value=1, step=1)
            with col_val:
                valor_unitario = st.number_input("Valor Unitário (R$)", min_value=0.0, step=1.0, value=110.0 if "Gás" in produto_selecionado else 12.0)
            
            pagamento = st.selectbox("Forma Pagamento", ["Dinheiro", "Pix", "Cartão", "Fiado"])
            endereco = st.text_input("Endereço/Bairro")
            obs = st.text_input("Obs (Ex: Deixar na portaria)")
            
            submitted = st.form_submit_button("✅ Registrar Venda")
            
            if submitted:
                # Ajuste de Horário Brasil (-3h)
                hora_brasil = datetime.now() - timedelta(hours=3)
                
                # CÁLCULOS AUTOMÁTICOS
                custo_unitario = CUSTOS_PRODUTOS.get(produto_selecionado, 0.00)
                
                total_venda = valor_unitario * quantidade  # Preço x Quantidade
                total_custo = custo_unitario * quantidade  # Custo x Quantidade
                lucro_real = total_venda - total_custo
                
                st.session_state.vendas.append({
                    "Hora": hora_brasil.strftime("%H:%M"),
                    "Cliente": cliente_nome,
                    "Telefone": cliente_tel,
                    "Produto": produto_selecionado,
                    "Qtd": quantidade,
                    "Valor Total": total_venda,
                    "Lucro Real": lucro_real,
                    "Pagamento": pagamento,
                    "Local": endereco
                })
                st.success(f"Venda registrada! Total: R$ {total_venda:.2f} (Lucro: R$ {lucro_real:.2f})")

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

df_vendas = pd.DataFrame(st.session_state.vendas)
df_despesas = pd.DataFrame(st.session_state.despesas)

# Cálculos Totais
total_faturamento = df_vendas["Valor Total"].sum() if not df_vendas.empty else 0.0
total_lucro_produtos = df_vendas["Lucro Real"].sum() if not df_vendas.empty else 0.0
total_despesas_extras = df_despesas["Valor"].sum() if not df_despesas.empty else 0.0
lucro_liquido_final = total_lucro_produtos - total_despesas_extras

with col1:
    st.metric("Faturamento (Bruto)", f"R$ {total_faturamento:.2f}")
with col2:
    st.metric("Despesas Extras", f"R$ {total_despesas_extras:.2f}")
with col3:
    st.metric("Lucro Líquido Real", f"R$ {lucro_liquido_final:.2f}", delta_color="normal")

st.markdown("---")

tab1, tab2 = st.tabs(["📄 Histórico de Vendas", "📉 Despesas"])

with tab1:
    if not df_vendas.empty:
        st.dataframe(df_vendas, use_container_width=True)
        csv = df_vendas.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Planilha (Excel/CSV)", data=csv, file_name="vendas_hoje.csv", mime="text/csv")
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
    - Faturamento Total: R$ {total_faturamento:.2f}
    - Lucro Bruto (Vendas): R$ {total_lucro_produtos:.2f}
    - Despesas Operacionais: R$ {total_despesas_extras:.2f}
    - LUCRO LÍQUIDO FINAL: R$ {lucro_liquido_final:.2f}
    
    VENDAS DETALHADAS:
    {df_vendas[['Cliente', 'Produto', 'Qtd', 'Valor Total', 'Local']].to_string(index=False)}
    
    Analise e me diga:
    1. O ticket médio e se houve vendas múltiplas (mais de 1 item).
    2. Sugestões para vender mais para os mesmos clientes amanhã.
    """
    st.text_area("Copie para a IA:", value=prompt_ia, height=250)
        
    


  
   
           




    
    



  




 
