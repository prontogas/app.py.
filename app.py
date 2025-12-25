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
st.title("🚀 Gestor Pronto Gás (Corrigido)")

# Inicializar Sessão
if 'vendas' not in st.session_state: st.session_state.vendas = []
if 'despesas' not in st.session_state: st.session_state.despesas = []

# Função para limpar os campos após salvar (Evita duplicidade)
def limpar_campos():
    st.session_state.temp_cliente = ""
    st.session_state.temp_obs = ""
    st.session_state.temp_dinheiro = 0.0

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("💾 Backup")
    if len(st.session_state.vendas) > 0:
        df_export = pd.DataFrame(st.session_state.vendas)
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ BAIXAR CÓPIA", csv, "vendas.csv", "text/csv")
    
    uploaded_file = st.file_uploader("📂 Carregar Cópia", type="csv")
    if uploaded_file is not None:
        try:
            df_import = pd.read_csv(uploaded_file)
            st.session_state.vendas = df_import.to_dict('records')
            st.success("✅ Recuperado!")
        except:
            st.error("Erro no arquivo.")

    st.markdown("---")
    st.header("📝 Novo Lançamento")
    tipo = st.radio("Tipo", ["Venda", "Despesa"])

    # --- ÁREA DE VENDA (SEM FORMULÁRIO TRAVADO) ---
    if tipo == "Venda":
        st.markdown("### 👤 Dados do Pedido")
        
        # Usamos 'key' para o sistema limpar depois
        cliente = st.text_input("Nome do Cliente", key="temp_cliente")
        
        produto = st.selectbox("Produto", list(PRODUTOS_PADRAO.keys()))
        
        # Preço Automático
        preco_base = PRODUTOS_PADRAO[produto]["sugerido"]
        if cliente in CLIENTES_VIP and produto == "Gás P13":
            preco_base = CLIENTES_VIP[cliente]
            st.caption(f"⭐ Preço VIP aplicado!")
        
        col_p, col_q = st.columns(2)
        preco_unit = col_p.number_input("Preço Unit.", value=float(preco_base), step=1.0)
        qtd = col_q.number_input("Qtd", min_value=1, value=1, step=1)
        
        total_venda = preco_unit * qtd
        
        # Mostrador Grande de Valor
        st.markdown(f"""
        <div style="padding:10px; background-color:#2e7b53; border-radius:10px; text-align:center; margin-bottom:10px;">
            <h2 style="color:white; margin:0;">Total: R$ {total_venda:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 💰 Pagamento")
        forma_pag = st.selectbox("Forma de Pagamento", 
                                 ["Dinheiro", "Pix", "Cartão", "Fiado", "MISTO (Dinheiro + Pix)"])
        
        texto_pagamento = forma_pag
        
        # --- LÓGICA DO MISTO (APARECE NA HORA) ---
        pode_salvar = True # Trava de segurança
        
        if forma_pag == "MISTO (Dinheiro + Pix)":
            val_dinheiro = st.number_input("Quanto recebeu em DINHEIRO?", min_value=0.0, step=1.0, key="temp_dinheiro")
            val_pix = total_venda - val_dinheiro
            
            if val_pix < 0:
                st.error("⚠️ Erro: O valor em dinheiro é maior que a venda!")
                pode_salvar = False
            else:
                st.info(f"👉 Restante no Pix: **R$ {val_pix:.2f}**")
                texto_pagamento = f"Din: {val_dinheiro:.0f} | Pix: {val_pix:.0f}"

        endereco = st.text_input("Endereço", key="temp_endereco")
        obs = st.text_input("Obs", key="temp_obs")

        st.markdown("---")
        
        # BOTÃO DE SALVAR (Só faz algo se clicar AQUI)
        if st.button("✅ FINALIZAR VENDA", type="primary", use_container_width=True):
            if pode_salvar:
                hora = datetime.now() - timedelta(hours=3)
                custo = PRODUTOS_PADRAO[produto]["custo"] * qtd
                lucro = total_venda - custo
                
                st.session_state.vendas.append({
                    "Hora": hora.strftime("%H:%M"),
                    "Cliente": cliente,
                    "Produto": produto,
                    "Qtd": qtd,
                    "Unitario": preco_unit,
                    "Total": total_venda,
                    "Lucro": lucro,
                    "Pagamento": texto_pagamento,
                    "Local": endereco
                })
                st.success("Venda registrada com sucesso!")
                limpar_campos() # Limpa os campos para a próxima
                st.rerun() # Atualiza a tabela

    # --- ÁREA DE DESPESA (Pode manter formulário simples) ---
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

    # --- ADMIN ---
    st.markdown("---")
    st.header("🔐 Admin")
    modo_admin = st.checkbox("Ativar Exclusão")
    senha_ok = False
    if modo_admin:
        senha = st.text_input("Senha", type="password")
        if senha == SENHA_ADMIN:
            senha_ok = True
            st.success("Liberado!")

# --- PAINEL PRINCIPAL ---
df_v = pd.DataFrame(st.session_state.vendas)
df_d = pd.DataFrame(st.session_state.despesas)

fat = df_v["Total"].sum() if not df_v.empty else 0.0
gastos = df_d["Valor"].sum() if not df_d.empty else 0.0
lucro = (df_v["Lucro"].sum() if not df_v.empty else 0.0) - gastos

c1, c2, c3 = st.columns(3)
c1.metric("Faturamento", f"R$ {fat:.2f}")
c2.metric("Gastos", f"R$ {gastos:.2f}")
c3.metric("Lucro Líquido", f"R$ {lucro:.2f}")

st.markdown("---")

col_v, col_d = st.columns([2,1])

with col_v:
    st.subheader("📋 Vendas do Dia")
    if not df_v.empty:
        st.dataframe(df_v[["Hora", "Cliente", "Produto", "Total", "Pagamento"]], use_container_width=True)
        
        if senha_ok:
            st.warning("⚠️ Apagar Venda")
            id_apagar = st.number_input("Linha para apagar", min_value=0, max_value=len(df_v)-1, step=1)
            if st.button("🗑️ APAGAR VENDA"):
                st.session_state.vendas.pop(id_apagar)
                st.rerun()
    else:
        st.info("Nenhuma venda.")

with col_d:
    st.subheader("💸 Despesas")
    if not df_d.empty:
        st.dataframe(df_d, use_container_width=True)
        if senha_ok:
            st.warning("⚠️ Apagar Despesa")
            id_d_apagar = st.number_input("Linha Despesa", min_value=0, max_value=len(df_d)-1, step=1, key="del_d")
            if st.button("🗑️ APAGAR DESPESA"):
                st.session_state.despesas.pop(id_d_apagar)
                st.rerun()

# IA
if not df_v.empty:
    st.markdown("---")
    st.header("🧠 Análise")
    txt = f"Fat: {fat}, Lucro: {lucro}. Vendas: {df_v.to_string(index=False)}"
    st.text_area("Copie para a IA:", value=txt)

           

   
   
  

                
      

   
            
                    
  


           
                
                    


    
 
         
        



        
            

       
                
