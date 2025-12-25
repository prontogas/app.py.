import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

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
st.title("🚀 Gestor Pronto Gás (Oficial)")

# Inicializar Sessão
if 'vendas' not in st.session_state: st.session_state.vendas = []
if 'despesas' not in st.session_state: st.session_state.despesas = []

# --- 🧹 SISTEMA DE LIMPEZA (CORREÇÃO DO ERRO) ---
# Isso roda no TOPO do script, antes de criar qualquer botão
if st.session_state.get('resetar_campos'):
    # Lista de chaves para apagar da memória
    chaves_para_limpar = ['temp_cliente', 'temp_obs', 'temp_endereco', 'v1', 'm1', 'm2']
    for chave in chaves_para_limpar:
        if chave in st.session_state:
            del st.session_state[chave]
    
    # Desliga o reset e avisa
    st.session_state.resetar_campos = False
    st.toast("✅ Venda Salva com Sucesso!", icon="🎉")

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

    # --- ÁREA DE VENDA ---
    if tipo == "Venda":
        st.markdown("### 👤 Dados")
        
        # As 'keys' (chaves) são essenciais para o reset funcionar
        cliente = st.text_input("Nome do Cliente", key="temp_cliente")
        produto = st.selectbox("Produto", list(PRODUTOS_PADRAO.keys()))
        
        # Preço Automático
        preco_base = PRODUTOS_PADRAO[produto]["sugerido"]
        if cliente in CLIENTES_VIP and produto == "Gás P13":
            preco_base = CLIENTES_VIP[cliente]
        
        col_p, col_q = st.columns(2)
        preco_unit = col_p.number_input("Preço Unit.", value=float(preco_base), step=1.0)
        qtd = col_q.number_input("Qtd", min_value=1, value=1, step=1)
        
        total_venda = preco_unit * qtd
        
        st.markdown(f"""
        <div style="padding:10px; background-color:#2e7b53; border-radius:10px; text-align:center; margin-bottom:10px;">
            <h2 style="color:white; margin:0;">Total: R$ {total_venda:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 💰 Pagamento")
        modo_pag = st.selectbox("Modo de Pagamento", ["Simples (Uma forma)", "COMBINADO (Duas formas)"])
        
        texto_pagamento = ""
        pode_salvar = True

        if modo_pag == "Simples (Uma forma)":
            forma = st.selectbox("Forma", ["Dinheiro", "Pix", "Cartão", "Fiado"])
            texto_pagamento = forma

        else: # MISTO
            st.info("👇 Configure a divisão:")
            c1, c2 = st.columns(2)
            with c1:
                metodo1 = st.selectbox("1ª Parte (Entrada)", ["Dinheiro", "Pix", "Cartão"], key="m1")
                val1 = st.number_input(f"Valor em {metodo1}", min_value=0.0, step=1.0, key="v1")
            with c2:
                metodo2 = st.selectbox("2ª Parte (Restante)", ["Pix", "Cartão", "Fiado", "Dinheiro"], key="m2")
                val2 = total_venda - val1
                
                if val2 < 0:
                    st.error(f"⚠️ A entrada é maior que o total!")
                    pode_salvar = False
                else:
                    st.write(f"Falta em {metodo2}:")
                    st.markdown(f"#### R$ {val2:.2f}")
            
            texto_pagamento = f"{metodo1}: {val1:.0f} | {metodo2}: {val2:.0f}"

        endereco = st.text_input("Endereço", key="temp_endereco")
        obs = st.text_input("Obs", key="temp_obs")

        st.markdown("---")
        
        # --- BOTÃO FINAL ---
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
                
                # AQUI É O TRUQUE: Apenas marcamos para limpar na próxima volta
                st.session_state.resetar_campos = True 
                st.rerun() # Reinicia a página imediatamente

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

            
    
 

    
      
           
               
              
              
   
       

       
          

    
               
            




          
                   






                
      

   
            
                    
  


           
                
                    


    
 
         
        



        
            

       
                
