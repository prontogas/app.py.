

        
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
st.title("🚀 Gestor Pronto Gás (Pagamento Flexível)")

# Inicializar Sessão
if 'vendas' not in st.session_state:
    st.session_state.vendas = []
if 'despesas' not in st.session_state:
    st.session_state.despesas = []

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("💾 Backup e Segurança")
    
    # 1. BAIXAR
    if len(st.session_state.vendas) > 0:
        df_export = pd.DataFrame(st.session_state.vendas)
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ BAIXAR CÓPIA DO DIA",
            data=csv,
            file_name="vendas_hoje.csv",
            mime="text/csv",
        )
    
    # 2. CARREGAR
    uploaded_file = st.file_uploader("📂 Carregar Cópia Salva", type="csv")
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

    if tipo == "Venda":
        with st.form("form_venda", clear_on_submit=True):
            st.markdown("### 👤 Cliente & Produto")
            cliente = st.text_input("Nome do Cliente")
            if cliente in CLIENTES_VIP:
                st.caption(f"⭐ VIP! Preço: R$ {CLIENTES_VIP[cliente]:.2f}")

            produto = st.selectbox("Produto", list(PRODUTOS_PADRAO.keys()))
            
            # Preço Base
            preco_base = PRODUTOS_PADRAO[produto]["sugerido"]
            if cliente in CLIENTES_VIP and produto == "Gás P13":
                preco_base = CLIENTES_VIP[cliente]
            
            col_p, col_q = st.columns(2)
            preco_unit = col_p.number_input("Preço Unit.", value=float(preco_base), step=1.0)
            qtd = col_q.number_input("Qtd", min_value=1, value=1)
            
            total_est = preco_unit * qtd
            st.info(f"Valor Total da Venda: R$ {total_est:.2f}")
            
            st.markdown("---")
            st.markdown("### 💰 Forma de Pagamento")
            
            # Opções de pagamento
            forma_pag = st.selectbox("Como o cliente pagou?", 
                                     ["Dinheiro", "Pix", "Cartão", "Fiado", "MISTO / COMBINADO"])
            
            # --- LÓGICA DO PAGAMENTO MISTO (UNIVERSAL) ---
            val_parte_1 = 0.0
            tipo_1 = ""
            tipo_2 = ""
            
            if forma_pag == "MISTO / COMBINADO":
                st.write("🔀 **Configurar Divisão:**")
                c_mix1, c_mix2 = st.columns(2)
                
                with c_mix1:
                    tipo_1 = st.selectbox("1ª Parte (Entrada)", ["Dinheiro", "Pix", "Cartão", "Fiado"], key="t1")
                    val_parte_1 = st.number_input(f"Valor em {tipo_1}", min_value=0.0, max_value=float(total_est), step=1.0)
                
                with c_mix2:
                    # Calcula o resto sozinho
                    resto = total_est - val_parte_1
                    tipo_2 = st.selectbox("2ª Parte (Restante)", ["Pix", "Cartão", "Fiado", "Dinheiro"], key="t2")
                    st.write(f"Falta pagar em {tipo_2}:")
                    st.warning(f"R$ {resto:.2f}")
            
            endereco = st.text_input("Endereço")
            
            if st.form_submit_button("✅ SALVAR VENDA"):
                hora = datetime.now() - timedelta(hours=3)
                custo = PRODUTOS_PADRAO[produto]["custo"] * qtd
                lucro = total_est - custo
                
                # Define o texto que vai salvar na tabela
                texto_pagamento = forma_pag
                
                if forma_pag == "MISTO / COMBINADO":
                    val_parte_2 = total_est - val_parte_1
                    # Ex: "Din: 20 + Cartão: 85"
                    texto_pagamento =       
                    
                
      

   
            
                    
  


           
                
                    


    
 
         
        



        
            

       
                
