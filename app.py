import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 🔧 CONFIGURAÇÃO (PREÇOS PADRÃO) ---
# Aqui definimos o PREÇO SUGERIDO (Padrão) e o CUSTO
PRODUTOS_PADRAO = {
    "Gás P13":   {"sugerido": 105.00, "custo": 82.00},
    "Água 20L":  {"sugerido": 12.00,  "custo": 5.00},
    "Outros":    {"sugerido": 0.00,   "custo": 0.00}
}

# --- 👥 LISTA DE CLIENTES ESPECIAIS (Simulação de Memória) ---
# Se você digitar esses nomes exatos, o sistema muda o preço sozinho
CLIENTES_VIP = {
    "Dona Maria": 100.00, # Ela paga mais barato
    "Sr. João": 95.00,    # Preço de amigo
    "Comércio": 90.00     # Preço de atacado
}
# -----------------------------------------------------------

st.set_page_config(page_title="Gestor Flexível", layout="wide")
st.title("🚀 Gestor Pronto Gás (Preço Livre)")

if 'vendas' not in st.session_state:
    st.session_state.vendas = []
if 'despesas' not in st.session_state:
    st.session_state.despesas = []

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📝 Novo Lançamento")
    tipo = st.radio("Tipo", ["Venda", "Despesa"])

    if tipo == "Venda":
        with st.form("form_venda"):
            # 1. Identificação
            st.markdown("### 👤 Cliente & Produto")
            cliente = st.text_input("Nome do Cliente")
            
            # Se o cliente for VIP, avisa
            msg_vip = ""
            if cliente in CLIENTES_VIP:
                msg_vip = f"⭐ Cliente VIP detectado! Preço sugerido: R$ {CLIENTES_VIP[cliente]:.2f}"
                st.caption(msg_vip)

            produto_selecionado = st.selectbox("Produto", list(PRODUTOS_PADRAO.keys()))
            
            # 2. Definição de Preço (A MÁGICA ACONTECE AQUI)
            st.markdown("### 💲 Negociação")
            
            # Lógica para decidir qual preço sugerir na tela
            preco_base = PRODUTOS_PADRAO[produto_selecionado]["sugerido"]
            if cliente in CLIENTES_VIP and produto_selecionado == "Gás P13":
                preco_base = CLIENTES_VIP[cliente]
            
            # Campo editável do preço unitário
            preco_unitario_cobrado = st.number_input(
                "Preço Unitário (Pode alterar)", 
                value=float(preco_base),
                step=1.0,
                format="%.2f"
            )
            
            qtd = st.number_input("Quantidade", min_value=1, value=1, step=1)
            
            # Cálculo automático do total na tela
            total_calculado = preco_unitario_cobrado * qtd
            
            st.markdown(f"### Total a Receber: **R$ {total_calculado:.2f}**")
            
            # Detalhes finais
            st.markdown("---")
            pagamento = st.selectbox("Pagamento", ["Dinheiro", "Pix", "Cartão", "Fiado"])
            endereco = st.text_input("Endereço")
            obs = st.text_input("Obs")
            
            submitted = st.form_submit_button("✅ Lançar Venda")
            
            if submitted:
                hora_brasil = datetime.now() - timedelta(hours=3)
                
                # Pega o custo fixo para calcular lucro certo
                custo_unitario = PRODUTOS_PADRAO[produto_selecionado]["custo"]
                custo_total = custo_unitario * qtd
                lucro_venda = total_calculado - custo_total
                
                st.session_state.vendas.append({
                    "Hora": hora_brasil.strftime("%H:%M"),
                    "Cliente": cliente,
                    "Produto": produto_selecionado,
                    "Qtd": qtd,
                    "Unitario": preco_unitario_cobrado,
                    "Total": total_calculado,
                    "Lucro": lucro_venda,
                    "Pagamento": pagamento,
                    "Local": endereco
                })
                st.success(f"Venda de R$ {total_calculado:.2f} lançada!")

    elif tipo == "Despesa":
        st.info("Lance seus gastos do dia")
        with st.form("form_despesa"):
            desc = st.text_input("Descrição")
            valor = st.number_input("Valor (R$)", min_value=0.0, step=1.0)
            cat = st.selectbox("Categoria", ["Gasolina", "Alimentação", "Outros"])
            if st.form_submit_button("Lançar Gasto"):
                hora = datetime.now() - timedelta(hours=3)
                st.session_state.despesas.append({
                    "Hora": hora.strftime("%H:%M"),
                    "Descrição": desc,
                    "Valor": valor,
                    "Categoria": cat
                })
                st.success("Despesa salva!")

# --- PAINEL PRINCIPAL ---
col1, col2, col3 = st.columns(3)

df_v = pd.DataFrame(st.session_state.vendas)
df_d = pd.DataFrame(st.session_state.despesas)

total_fat = df_v["Total"].sum() if not df_v.empty else 0.0
total_lucro = df_v["Lucro"].sum() if not df_v.empty else 0.0
total_gastos = df_d["Valor"].sum() if not df_d.empty else 0.0
liquido = total_lucro - total_gastos

with col1: st.metric("Faturamento", f"R$ {total_fat:.2f}")
with col2: st.metric("Gastos Extras", f"R$ {total_gastos:.2f}")
with col3: st.metric("Lucro no Bolso", f"R$ {liquido:.2f}")

st.markdown("---")

c1, c2 = st.columns([2,1])
with c1:
    st.subheader("Histórico de Vendas")
    if not df_v.empty:
        # Mostrando o preço unitário que foi cobrado
        st.dataframe(df_v[["Hora", "Cliente", "Produto", "Qtd", "Unitario", "Total"]], use_container_width=True)
    else:
        st.info("Sem vendas.")

with c2:
    st.subheader("Gastos")
    if not df_d.empty:
        st.dataframe(df_d, use_container_width=True)

# --- IA ---
if not df_v.empty:
    st.markdown("---")
    st.header("🧠 Análise")
    txt_ia = f"""
    Analise meu dia de vendas de Gás.
    Faturamento: R$ {total_fat:.2f}
    Lucro Líquido: R$ {liquido:.2f}
    
    VENDAS:
    {df_v.to_string(index=False)}
    
    Me dê dicas para aumentar o lucro amanhã.
    """
    st.text_area("Copie para a IA:", value=txt_ia)

 
   


  




    
    



  




 
