
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

# --- 🔧 CONFIGURAÇÕES ---
SENHA_ADMIN = "1234"

PRODUTOS_PADRAO = {
    "Gás P13":   {"sugerido": 105.00, "custo": 82.00},
    "Água 20L":  {"sugerido": 12.00,  "custo": 5.00},
    "Outros":    {"sugerido": 0.00,   "custo": 0.00}
}

CLIENTES_VIP = {
    "Dona Maria": 100.00,
    "Sr. João": 95.00,
    "Comércio": 90.00
}

st.set_page_config(page_title="Gestor Pronto Gás", layout="wide")
st.title("🚀 Gestor Pronto Gás (Com Backup)")

# Inicializar Sessão
if 'vendas' not in st.session_state:
    st.session_state.vendas = []
if 'despesas' not in st.session_state:
    st.session_state.despesas = []

# --- BARRA LATERAL (Tudo acontece aqui) ---
with st.sidebar:
    st.header("💾 Sistema de Backup")
    st.info("O app zera se fechar. Use os botões abaixo para não perder dados!")
    
    # 1. BOTÃO PARA BAIXAR (SALVAR)
    if len(st.session_state.vendas) > 0:
        df_export = pd.DataFrame(st.session_state.vendas)
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ BAIXAR CÓPIA DO DIA",
            data=csv,
            file_name="vendas_hoje.csv",
            mime="text/csv",
        )
    
    # 2. BOTÃO PARA CARREGAR (RESTAURAR)
    uploaded_file = st.file_uploader("📂 Carregar Cópia Salva", type="csv")
    if uploaded_file is not None:
        try:
            df_import = pd.read_csv(uploaded_file)
            st.session_state.vendas = df_import.to_dict('records')
            st.success("✅ Dados recuperados com sucesso!")
        except:
            st.error("Erro ao ler arquivo.")

    st.markdown("---")
    st.header("📝 Novo Lançamento")
    tipo = st.radio("Tipo", ["Venda", "Despesa"])

    if tipo == "Venda":
        with st.form("form_venda", clear_on_submit=True):
            cliente = st.text_input("Nome do Cliente")
            if cliente in CLIENTES_VIP:
                st.caption(f"⭐ VIP! Preço: R$ {CLIENTES_VIP[cliente]:.2f}")

            produto = st.selectbox("Produto", list(PRODUTOS_PADRAO.keys()))
            
            preco_base = PRODUTOS_PADRAO[produto]["sugerido"]
            if cliente in CLIENTES_VIP and produto == "Gás P13":
                preco_base = CLIENTES_VIP[cliente]
            
            col_p, col_q = st.columns(2)
            preco_unit = col_p.number_input("Preço Unit.", value=float(preco_base), step=1.0)
            qtd = col_q.number_input("Qtd", min_value=1, value=1)
            
            total_est = preco_unit * qtd
            st.write(f"**Total: R$ {total_est:.2f}**")
            
            pagamento = st.selectbox("Pagamento", ["Dinheiro", "Pix", "Cartão", "Fiado"])
            endereco = st.text_input("Endereço")
            
            if st.form_submit_button("✅ SALVAR VENDA"):
                hora = datetime.now() - timedelta(hours=3)
                custo = PRODUTOS_PADRAO[produto]["custo"] * qtd
                lucro = total_est - custo
                
                st.session_state.vendas.append({
                    "Hora": hora.strftime("%H:%M"),
                    "Cliente": cliente,
                    "Produto": produto,
                    "Qtd": qtd,
                    "Unitario": preco_unit,
                    "Total": total_est,
                    "Lucro": lucro,
                    "Pagamento": pagamento,
                    "Local": endereco
                })
                st.success("Venda Salva!")
                st.rerun()

    elif tipo == "Despesa":
        with st.form("form_despesa", clear_on_submit=True):
            desc = st.text_input("Descrição")
            valor = st.number_input("Valor (R$)", min_value=0.0)
            cat = st.selectbox("Categoria", ["Gasolina", "Alimentação", "Outros"])
            
            if st.form_submit_button("SALVAR DESPESA"):
                hora = datetime.now() - timedelta(hours=3)
                st.session_state.despesas.append({
                    "Hora": hora.strftime("%H:%M"),
                    "Descrição": desc,
                    "Valor": valor,
                    "Categoria": cat
                })
                st.success("Gasto Salvo!")
                st.rerun()

    # --- ÁREA ADMINISTRATIVA NA BARRA LATERAL ---
    st.markdown("---")
    st.header("🔐 Admin")
    modo_admin = st.checkbox("Ativar Modo de Exclusão")
    if modo_admin:
        senha = st.text_input("Senha", type="password")
        if senha == SENHA_ADMIN:
            st.success("Liberado! Veja os botões abaixo da tabela.")
        elif senha != "":
            st.error("Senha errada")

# --- PAINEL PRINCIPAL ---
df_v = pd.DataFrame(st.session_state.vendas)
df_d = pd.DataFrame(st.session_state.despesas)

# Cálculos
fat = df_v["Total"].sum() if not df_v.empty else 0.0
gastos = df_d["Valor"].sum() if not df_d.empty else 0.0
lucro = (df_v["Lucro"].sum() if not df_v.empty else 0.0) - gastos

# Métricas
c1, c2, c3 = st.columns(3)
c1.metric("Faturamento", f"R$ {fat:.2f}")
c2.metric("Gastos", f"R$ {gastos:.2f}")
c3.metric("Lucro Líquido", f"R$ {lucro:.2f}")

st.markdown("---")

# Tabelas com Exclusão
col_vendas, col_gastos = st.columns([2,1])

with col_vendas:
    st.subheader("📋 Vendas")
    if not df_v.empty:
        st.dataframe(df_v[["Hora", "Cliente", "Produto", "Qtd", "Total", "Pagamento"]], use_container_width=True)
        
        # BOTÃO DE APAGAR (SÓ APARECE SE A SENHA ESTIVER CERTA NO MENU)
        if modo_admin and senha == SENHA_ADMIN:
            st.warning("⚠️ Área de Exclusão de Venda")
            id_apagar = st.number_input("Digite o número da linha (Index) para apagar", min_value=0, max_value=len(df_v)-1, step=1)
            if st.button("🗑️ APAGAR VENDA"):
                st.session_state.vendas.pop(id_apagar)
                st.rerun()
    else:
        st.info("Nenhuma venda.")

with col_gastos:
    st.subheader("💸 Despesas")
    if not df_d.empty:
        st.dataframe(df_d, use_container_width=True)
        
        if modo_admin and senha == SENHA_ADMIN:
            st.warning("⚠️ Exclusão")
            id_d_apagar = st.number_input("Linha para apagar", min_value=0, max_value=len(df_d)-1, step=1, key="del_d")
            if st.button("🗑️ APAGAR DESPESA"):
                st.session_state.despesas.pop(id_d_apagar)
                st.rerun()

# IA
if not df_v.empty:
    st.markdown("---")
    st.header("🧠 Análise")
    txt = f"Fat: {fat}, Lucro: {lucro}. Vendas: {df_v.to_string(index=False)}"
    st.text_area("Copie para a IA:", value=txt)  

     
        
            

       
                
