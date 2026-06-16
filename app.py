import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import uuid
import requests

# Configuração da página do Streamlit (Deve ser a primeira linha)
st.set_page_config(page_title="Enxoval da Elis 👶", page_icon="👶", layout="wide")

# --- CONEXÃO AUTOMÁTICA COM GOOGLE SHEETS ---
# O Streamlit lê o bloco [connections.gsheets] do seu segredo sozinho aqui
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # ttl=0 garante que ele busque os dados atualizados sem pegar lixo do cache
    df_completo = conn.read(ttl=0)
except Exception as e:
    st.error(f"Erro ao conectar com o Google Sheets: {e}")
    df_completo = pd.DataFrame()

# --- BUSCA DE SENHAS E CHAVES DO TOML ---
IMGBB_KEY = st.secrets.get("api_keys", {}).get("imgbb")
SENHA_PAIS = st.secrets.get("credenciais", {}).get("senha_pais")

# --- INJEÇÃO DE CSS PREMIUM (Foco em Acessibilidade para Idosos) ---
st.markdown("""
    <style>
        html, body, [data-testid="stMarkdownContainer"] p {
            font-family: 'Open Sans', sans-serif !important;
            font-size: 1.25rem !important;
            color: #1A202C !important;
        }
        h1 { font-size: 3rem !important; font-weight: 800 !important; color: #0284C7 !important; text-align: center; }
        h2 { font-size: 2rem !important; font-weight: 700 !important; color: #0369A1 !important; }
        
        .box-ajuda {
            background-color: #E0F2FE !important;
            border-left: 6px solid #0284C7 !important;
            padding: 20px !important;
            border-radius: 12px !important;
            margin-bottom: 30px !important;
        }
        
        .card-presente {
            background-color: #FFFFFF;
            border: 2px solid #E5E7EB;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
            margin-bottom: 20px;
            text-align: center;
        }
        .img-produto {
            height: 160px !important;
            object-fit: contain !important;
            margin-bottom: 15px;
        }
        .titulo-produto {
            font-size: 1.4rem !important;
            font-weight: 700 !important;
            color: #111827 !important;
            margin-bottom: 8px;
        }
        .tag-tamanho {
            background-color: #F3F4F6;
            padding: 2px 10px;
            border-radius: 6px;
            font-weight: 700;
        }
        
        div.stButton > button {
            width: 100% !important;
            background-color: #0284C7 !important;
            color: white !important;
            font-size: 1.3rem !important;
            font-weight: bold !important;
            padding: 12px 20px !important;
            border-radius: 14px !important;
            border: none !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        }
        div.stButton > button:hover {
            background-color: #0369A1 !important;
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# Abas de navegação
aba_convidados, aba_sugerir, aba_pais = st.tabs([
    "🍼 Lista de Presentes", 
    "💝 Dar Outro Presente", 
    "🔒 Área dos Pais"
])

# =========================================================================
# ABA 1: LISTA DE PRESENTES (CONVIDADOS)
# =========================================================================
with aba_convidados:
    st.markdown("<h1>Lista de Presentes da Elis</h1>", unsafe_allow_html=True)
    st.markdown("""
        <div class="box-ajuda">
            <h3 style='margin-top:0; color:#0369A1;'>💡 Como escolher o seu presente?</h3>
            <ol style='margin-bottom:0;'>
                <li>Olhe as opções de presentes disponíveis abaixo.</li>
                <li>Quando gostar de um, clique no grande botão azul <b>"Quero dar este presente"</b>.</li>
                <li>Um formulário vai abrir logo abaixo do card: digite seu nome e confirme. Pronto!</li>
            </ol>
        </div>
    """, unsafe_allow_html=True)

    if not df_completo.empty:
        # Força os nomes de colunas a ignorarem espaços extras
        df_completo.columns = [c.strip() for c in df_completo.columns]
        
        # Filtra para mostrar apenas o que está livre
        df_disponiveis = df_completo[df_completo['Status'] == '🛒 Faltando']
        
        if df_disponiveis.empty:
            st.success("Uau! Todos os presentes da lista já foram reservados! Muito obrigado! ❤️")
        else:
            cols = st.columns(3)
            for idx, (_, item) in enumerate(df_disponiveis.iterrows()):
                col_atual = cols[idx % 3]
                
                with col_atual:
                    url_foto = item['URL da Foto'] if str(item['URL da Foto']).strip() not in ["", "nan", "0"] else "https://images.unsplash.com/photo-1555252333-9f8e92e65df9?q=80&w=200"
                    
                    st.markdown(f"""
                        <div class="card-presente">
                            <img src="{url_foto}" class="img-produto">
                            <div class="titulo-produto">{item['Nome do Item']}</div>
                            <p style='margin-bottom:4px;'>🏷️ <b>Categoria:</b> {item['Tipo']}</p>
                            <p style='margin-bottom:4px;'>📐 <b>Tamanho:</b> <span class="tag-tamanho">{item['Tamanho']}</span></p>
                            <p style='margin-bottom:15px;'>🔢 <b>Precisamos de:</b> {item['Quantidade']} un</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("Quero dar este presente 🙋‍♂️", key=f"btn_{item['Código']}"):
                        st.session_state[f"res_{item['Código']}"] = True
                        
                    if st.session_state.get(f"res_{item['Código']}", False):
                        with st.form(key=f"form_{item['Código']}"):
                            st.markdown(f"### Confirmar: {item['Nome do Item']}")
                            nome_doador = st.text_input("Seu Nome e Sobrenome:", placeholder="Ex: Tia Maria Silva")
                            tel_doador = st.text_input("Seu Telefone / WhatsApp (Opcional):")
                            
                            f_c1, f_c2 = st.columns(2)
                            with f_c1:
                                enviado = st.form_submit_button("Confirmar Escolha ❤️")
                            with f_c2:
                                if st.form_submit_button("Cancelar ❌"):
                                    st.session_state[f"res_{item['Código']}"] = False
                                    st.rerun()
                                    
                            if enviado:
                                if nome_doador.strip():
                                    # Encontra o índice da linha na planilha original
                                    idx_linha = df_completo[df_completo['Código'] == item['Código']].index[0]
                                    df_completo.at[idx_linha, 'Status'] = "⏳ Reservado (Falta receber)"
                                    df_completo.at[idx_linha, 'Doador'] = nome_doador
                                    df_completo.at[idx_linha, 'Telefone'] = tel_doador
                                    
                                    conn.update(data=df_completo)
                                    st.success("Presente reservado com sucesso! Muito obrigado! ❤️")
                                    st.session_state[f"res_{item['Código']}"] = False
                                    st.rerun()
                                else:
                                    st.warning("Escreva seu nome para confirmar.")
    else:
        st.info("Aguardando cadastro de itens na planilha do Google Sheets.")

# =========================================================================
# ABA 2: SUGERIR OUTRO PRESENTE
# =========================================================================
with aba_sugerir:
    st.markdown("<h2 style='text-align:center;'>Dar um presente de fora da lista</h2>", unsafe_allow_html=True)
    
    with st.form(key="form_sugestao", clear_on_submit=True):
        nome_sug = st.text_input("Seu Nome e Sobrenome:", placeholder="Ex: Vovó Maria Silva")
        tel_sug = st.text_input("Seu Celular (Opcional):")
        presente_sug = st.text_input("Qual presente você comprou?", placeholder="Ex: Banheira de Bebê")
        foto_sug = st.file_uploader("Foto do presente (Opcional):", type=["png", "jpg", "jpeg"])
        
        enviar_sug = st.form_submit_button("Confirmar e Registrar Meu Presente ❤️")
        
        if enviar_sug:
            if nome_sug and presente_sug:
                url_foto_final = "https://images.unsplash.com/photo-1555252333-9f8e92e65df9?q=80&w=200"
                
                if foto_sug and IMGBB_KEY:
                    try:
                        response = requests.post(
                            "https://api.imgbb.com/1/upload",
                            data={"key": IMGBB_KEY},
                            files={"image": foto_sug.getvalue()}
                        )
                        if response.status_code == 200:
                            url_foto_final = response.json()["data"]["url"]
                    except Exception:
                        pass
                
                nova_linha = pd.DataFrame([{
                    "Código": f"SUG-{str(uuid.uuid4().hex[:6]).upper()}",
                    "Nome do Item": presente_sug,
                    "Tipo": "Sugerido por Convidado",
                    "Tamanho": "N/A",
                    "Quantidade": 1,
                    "URL da Foto": url_foto_final,
                    "Status": "⏳ Reservado (Falta receber)",
                    "Doador": nome_sug,
                    "Telefone": tel_sug
                }])
                
                df_atualizado = pd.concat([df_completo, nova_linha], ignore_index=True)
                conn.update(data=df_atualizado)
                st.success("Presente registrado com sucesso! Obrigado! ❤️")
                st.rerun()

# =========================================================================
# ABA 3: ÁREA DOS PAIS (GERENCIADOR INTERATIVO)
# =========================================================================
with aba_pais:
    st.markdown("<h2>🛠️ Painel de Controle dos Pais</h2>", unsafe_allow_html=True)
    
    if "admin_ok" not in st.session_state:
        st.session_state["admin_ok"] = False
        
    if not st.session_state["admin_ok"]:
        senha = st.text_input("Insira a senha de acesso:", type="password")
        if st.button("Liberar Painel 🔓"):
            if senha == SENHA_PAIS:
                st.session_state["admin_ok"] = True
                st.rerun()
            else:
                st.error("Senha incorreta! 🔑")
    else:
        st.write("Planilha de controle. Altere dados ou adicione linhas e clique em salvar:")
        
        df_editado = st.data_editor(
            df_completo, 
            num_rows="dynamic", 
            use_container_width=True,
            column_config={
                "Status": st.column_config.SelectboxColumn("Status", options=["🛒 Faltando", "⏳ Reservado (Falta receber)", "✅ Recebido (Em mãos)"]),
                "Tipo": st.column_config.SelectboxColumn("Categoria", options=["Roupa", "Fralda", "Higiene", "Quarto / Decoração", "Sugerido por Convidado", "Outros"])
            }
        )
        
        if st.button("💾 Salvar Todas as Alterações no Google Sheets"):
            with st.spinner("Sincronizando..."):
                # Garante código para novas linhas criadas pelo painel
                for idx, row in df_editado.iterrows():
                    if pd.isna(row.get("Código")) or str(row.get("Código")).strip() == "":
                        df_editado.at[idx, "Código"] = f"ELIS-{str(uuid.uuid4().hex[:6]).upper()}"
                
                df_editado["Doador"] = df_editado["Doador"].fillna("").astype(str)
                df_editado["Telefone"] = df_editado["Telefone"].fillna("").astype(str)
                
                conn.update(data=df_editado)
                st.success("Tudo sincronizado no Google Sheets! 🚀")
                st.rerun()