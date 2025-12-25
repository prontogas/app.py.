import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 🔧 CONFIGURAÇÕES ---
# Senha para apagar registros (Mude aqui se quiser)
SENHA_ADMIN = "0603"

# Tabela de Preços Sugeridos e Custos
PRODUTOS_PADRAO = {
    "Gás P13":   {"sugerido": 105.00, "custo": 82.00},
    "Água 20L":  {"sugerido": 12.00,  "custo": 5.00},
    "Outros":    {"sugerido": 0.00,   "custo": 0.00}
}

# Clientes VIP (Preços Automáticos)
CLIENTES_VIP = {
    "Dona Maria": 100.00,
    "Sr. João": 95.00,
    "Comércio": 90.00
}
# ------------------------

st.set_page_config(page_title="Gestor Seguro", layout="wide")
st.title("🚀 Gestor Pronto Gás (Com Exclusão)")

# Inicializar Banco de Dados
if 'vendas' not in st.session_state:
    st.session_state.vendas = []
if 'despesas' not in st.session_state:
    st.session_state.despesas = []

# --- BARRA LATERAL (LANÇAMENTOS) ---
with st.sidebar:
    st.header("📝 Novo Lançamento")
    tipo = st.radio("Tipo", ["Venda", "Despesa"])

    if tipo == "Venda":
        with st.form("form_venda", clear_on_submit=True):
            st.markdown("### 👤 Cliente & Produto")
            cliente = st.text_input("Nome do Cliente")
            
            # Alerta VIP
            if cliente in CLIENTES_VIP:
                st.caption(f"⭐ VIP Detectado! Preço: R$ {CLIENTES_VIP[cliente]:.2f}")

            produto_selecionado = st.selectbox("Produto", list(PRODUTOS_PADRAO.keys()))
            
            # Lógica de Preço Inteligente
            preco_base = PRODUTOS_PADRAO[produto_selecionado]["sugerido"]
            if cliente in CLIENTES_VIP and produto_selecionado == "Gás P13":
                preco_base = CLIENTES_VIP[cliente]
            
            st.markdown("### 💲 Valores")
            col_p, col_q = st.columns(2)
            with col_p:
                preco_unitario = st.number_input("Preço Unitário", value=float(preco_base), step=1.0, format="%.2f")
            with col_q:
                qtd = st.number_input("Qtd", min_value=1, value=1, step=1)
            
            # Mostra total estimado (informativo)
            total_estimado = preco_unitario * qtd
            st.info(f"Total Calculado: R$ {total_estimado:.2f}")

            st.markdown("---")
            pagamento = st.selectbox("Pagamento", ["Dinheiro", "Pix", "Cartão", "Fiado"])
            endereco = st.text_input("Endereço")
            obs = st.text_input("Obs")
            
            # O formulário só envia quando clica no botão, mas o Enter no último campo também aciona
            submitted = st.form_submit_button("✅ SALVAR VENDA")
            
            if submitted:
                hora_brasil = datetime.now() - timedelta(hours=3)
                custo_unit = PRODUTOS_PADRAO[produto_selecionado]["custo"]
                custo_total = custo_unit * qtd
                lucro = total_estimado - custo_total
                
                st.session_state.vendas.append({
                    "Hora": hora_brasil.strftime("%H:%M"),
                    "Cliente": cliente,
                    "Produto": produto_selecionado,
                    "Qtd": qtd,
                    "Unitario": preco_unitario,
                    "Total": total_estimado,
                    "Lucro": lucro,
                    "Pagamento": pagamento,
                    "Local": endereco
                })
                st.success("Venda Salva!")

    elif tipo == "Despesa":
        with st.form("form_despesa", clear_on_submit=True):
            st.write("Lançar Gastos")
            desc = st.text_input("Descrição")
            valor = st.number_input("Valor (R$)", min_value=0.0, step=0.5)
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

# --- PAINEL GERAL ---
col1, col2, col3 = st.columns(3)
df_v = pd.DataFrame(st.session_state.vendas)
df_d = pd.DataFrame(st.session_state.despesas)

fat = df_v["Total"].sum() if not df_v.empty else 0.0
gastos = df_d["Valor"].sum() if not df_d.empty else 0.0
lucro_bruto = df_v["Lucro"].sum() if not df_v.empty else 0.0
lucro_real = lucro_bruto - gastos

with col1: st.metric("Faturamento", f"R$ {fat:.2f}")
with col2: st.metric("Gastos Extras", f"R$ {gastos:.2f}")
with col3: st.metric("Lucro no Bolso", f"R$ {lucro_real:.2f}")

st.markdown("---")

# Tabelas
c1, c2 = st.columns([2,1])
with c1:
    st.subheader("Histórico de Vendas")
    if not df_v.empty:
        # Mostra tabela com índice (número da linha) para facilitar exclusão
        st.dataframe(df_v[["Hora", "Cliente", "Produto", "Qtd", "Total", "Pagamento"]], use_container_width=True)
    else:
        st.info("Vazio")

with c2:
    st.subheader("Gastos")
    if not df_d.empty:
        st.dataframe(df_d, use_container_width=True)

st.markdown("---")

# --- 🔐 ÁREA DE SEGURANÇA (EXCLUSÃO) ---
with st.expander("🔐 Área Administrativa (Correção/Exclusão)"):
    senha_digitada = st.text_input("Digite a Senha Administrativa", type="password")
    
    if senha_digitada == SENHA_ADMIN:
        st.success("Acesso Liberado!")
        
        tab1, tab2 = st.tabs(["Excluir Vendas", "Excluir Despesas"])
        
        with tab1:
            if not df_v.empty:
                st.warning("Selecione o número da linha (Index) que deseja apagar:")
                # Mostra a tabela completa com o índice à esquerda
                st.dataframe(df_v)
                
                # Caixa para escolher o número
                id_para_apagar = st.number_input("Número da Linha para Apagar", min_value=0, max_value=len(df_v)-1, step=1)
                
                if st.button("🗑️ APAGAR VENDA SELECIONADA"):
                    # Remove o item da lista
                    st.session_state.vendas.pop(id_para_apagar)
                    st.rerun() # Atualiza a tela na hora
            else:
                st.write("Nada para apagar.")
                
        with tab2:
            if not df_d.empty:
                st.warning("Selecione o número da despesa para apagar:")
                st.dataframe(df_d)
                id_desp_apagar = st.number_input("Número da Linha", min_value=0, max_value=len(df_d)-1, step=1, key="del_desp")
                
                if st.button("🗑️ APAGAR DESPESA"):
                    st.session_state.despesas.pop(id_desp_apagar)
                    st.rerun()
            else:
                st.write("Nada para apagar.")
    
    elif senha_digitada != "":
        st.error("Senha Incorreta!")

# --- IA ---
if not df_v.empty:
    st.markdown("---")
    st.header("🧠 Análise")
    txt = f"""
    Analise meu dia. Fat: {fat}, Lucro: {lucro_real}.
    Vendas: {df_v.to_string(index=False)}
    """
    st.text_area("Copie para a IA:", value=txt)
