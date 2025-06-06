import streamlit as st
import pandas as pd
from datetime import date
import os

CSV_FILE = "relatorios.csv"

# Inicializa o CSV se não existir
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["Data", "Horas", "Título", "Descrição"])
    df_init.to_csv(CSV_FILE, index=False)

# Carrega os dados


def carregar_dados():
    return pd.read_csv(CSV_FILE)

# Salva os dados


def salvar_dados(df):
    df.to_csv(CSV_FILE, index=False)


# Interface
st.set_page_config(page_title="Relatório de Atividades", layout="centered")
st.title("📋 Relatório de Atividades")

# Carregar dados atuais
df = carregar_dados()

# Estado para edição
if "editando" not in st.session_state:
    st.session_state.editando = None

st.subheader("➕ Adicionar / Editar Atividade")
# Pré-preencher campos se estiver editando
if st.session_state.editando is not None:
    atividade_em_edicao = df.iloc[st.session_state.editando]
    valor_data = pd.to_datetime(atividade_em_edicao["Data"]).date()
    valor_horas = atividade_em_edicao["Horas"]
    valor_titulo = atividade_em_edicao["Título"]
    valor_descricao = atividade_em_edicao["Descrição"]
else:
    valor_data = date.today()
    valor_horas = 0.0
    valor_titulo = ""
    valor_descricao = ""

# Formulário de adicionar/editar
with st.form("form_atividade"):
    col1, col2 = st.columns([1, 1])

    with col1:
        data = st.date_input("Data", value=valor_data)
    with col2:
        horas = st.number_input("Horas", min_value=0.0,
                                step=0.5, value=valor_horas)

    titulo = st.text_input("Título", value=valor_titulo)
    descricao = st.text_area("Descrição", value=valor_descricao)

    if st.session_state.editando is not None:
        submit_label = "Salvar Edição"
    else:
        submit_label = "Adicionar"

    submitted = st.form_submit_button(submit_label)

    if submitted:
        if not titulo or not descricao or horas == 0.0:
            st.warning("Preencha todos os campos corretamente.")
        else:
            nova_atividade = {
                "Data": str(data),
                "Horas": horas,
                "Título": titulo,
                "Descrição": descricao
            }

            if st.session_state.editando is not None:
                # Editar atividade
                df.iloc[st.session_state.editando] = nova_atividade
                st.success("Atividade editada com sucesso!")
                st.session_state.editando = None
            else:
                # Adicionar nova
                df = pd.concat(
                    [df, pd.DataFrame([nova_atividade])], ignore_index=True)
                st.success("Atividade adicionada com sucesso!")

            salvar_dados(df)
            st.rerun()

st.subheader("📊 Atividades Registradas")

if not df.empty:
    for idx, row in df.iterrows():
        with st.expander(f"{row['Data']} | {row['Título']}"):
            st.write(f"**Horas:** {row['Horas']}")
            st.write(f"**Descrição:** {row['Descrição']}")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🖊️ Editar", key=f"editar_{idx}"):
                    st.session_state.editando = idx
                    st.rerun()
            with col2:
                if st.button("🗑️ Remover", key=f"remover_{idx}"):
                    df = df.drop(index=idx).reset_index(drop=True)
                    salvar_dados(df)
                    st.success("Atividade removida.")
                    st.rerun()
else:
    st.info("Nenhuma atividade registrada ainda.")

st.subheader("⏱️ Total de horas por dia")

if not df.empty:
    # Converter e formatar datas corretamente
    df['Data'] = pd.to_datetime(df['Data'])

    # Agrupar por data e somar horas
    horas_por_dia = df.groupby(df['Data'].dt.strftime(
        '%d/%m/%Y'))['Horas'].sum().reset_index()
    horas_por_dia.columns = ['Data', 'Total de Horas']

    # Exibir tabela
    st.dataframe(horas_por_dia)

    # Exibir gráfico de barras
    st.bar_chart(horas_por_dia.set_index('Data'))
else:
    st.info("Nenhuma atividade registrada para calcular horas.")


# Download opcional
st.download_button("📥 Baixar CSV", data=df.to_csv(
    index=False), file_name="relatorios.csv", mime="text/csv")

st.subheader("🧾 Visualização em formato de texto")

if st.button("📄 Exibir como texto"):
    if df.empty:
        st.info("Nenhuma atividade registrada.")
    else:
        texto_formatado = "\n".join([
            f"{pd.to_datetime(row['Data']).strftime('%d/%m/%Y')} | {int(row['Horas'])} | {row['Título']} | {row['Descrição']}"
            for _, row in df.iterrows()
        ])
        st.text_area("Atividades formatadas:",
                     value=texto_formatado, height=300)
