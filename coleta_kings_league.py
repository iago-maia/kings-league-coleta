# Estrutura inicial para o sistema de coleta de dados da Kings League

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Caminhos de diretórios
PASTA_JOGOS = "data/jogos"
os.makedirs(PASTA_JOGOS, exist_ok=True)

# Carregar jogadores
@st.cache_data
def carregar_jogadores():
    return pd.read_csv("players_meta.csv")

df_jogadores = carregar_jogadores()

# Seleção dos times da partida
st.sidebar.title("⚙️ Configuração do Jogo")
times_disponiveis = sorted(df_jogadores["team_name"].dropna().unique())
time_a = st.sidebar.selectbox("Selecione o Time A", times_disponiveis)
time_b = st.sidebar.selectbox("Selecione o Time B", [t for t in times_disponiveis if t != time_a])

jogadores_time_a = df_jogadores[df_jogadores["team_name"] == time_a]["shortName"].tolist()
jogadores_time_b = df_jogadores[df_jogadores["team_name"] == time_b]["shortName"].tolist()
jogadores_partida = jogadores_time_a + jogadores_time_b

# Definir nome do arquivo CSV do jogo
nome_jogo = f"{datetime.now().strftime('%Y%m%d')}_{time_a.replace(' ', '')}_vs_{time_b.replace(' ', '')}.csv"
st.session_state.csv_jogo = os.path.join(PASTA_JOGOS, nome_jogo)

# Estado da sessão
if "relogio_iniciado" not in st.session_state:
    st.session_state.relogio_iniciado = False
    st.session_state.tempo_inicio = None
    st.session_state.tempo_manual = timedelta(minutes=0)

if "eventos" not in st.session_state:
    st.session_state.eventos = []

# Funções auxiliares
def tempo_jogo():
    if st.session_state.relogio_iniciado:
        delta = datetime.now() - st.session_state.tempo_inicio + st.session_state.tempo_manual
    else:
        delta = st.session_state.tempo_manual
    return str(delta)[:7]

def salvar_evento(acao, detalhe, jogador, time, comentario):
    evento = {
        "id": f"e{len(st.session_state.eventos)+1:03}",
        "minuto": tempo_jogo(),
        "tempo_real": datetime.now().strftime("%H:%M:%S"),
        "acao": acao,
        "jogador": jogador,
        "time": time,
        "detalhe": detalhe,
        "comentario": comentario
    }
    st.session_state.eventos.append(evento)
    salvar_em_csv(evento)

def salvar_em_csv(evento):
    if "csv_jogo" in st.session_state:
        df = pd.DataFrame([evento])
        df.to_csv(st.session_state.csv_jogo, mode='a', index=False, header=not os.path.exists(st.session_state.csv_jogo))

def start_clock():
    if not st.session_state.relogio_iniciado:
        st.session_state.relogio_iniciado = True
        st.session_state.tempo_inicio = datetime.now()

def pause_clock():
    if st.session_state.relogio_iniciado:
        st.session_state.relogio_iniciado = False
        st.session_state.tempo_manual += datetime.now() - st.session_state.tempo_inicio

# UI
st.title("🎮 Sistema de Coleta - Kings League")

col1, col2 = st.columns([2, 1])

with col1:
    with st.form("form_evento"):
        st.subheader("Inserir Evento")
        acao = st.selectbox("Ação", ["Gol", "Chute no Gol", "Chute Bloqueado", "Falta", "Cartão Amarelo", "Cartão Vermelho", "Escanteio", "Impedimento", "Lateral", "Tiro de Meta", "Penalti Presidente", "Shootout", "Carta Secreta", "Gol Duplo", "Golden Goal", "Dado Min 18"])
        detalhe = st.text_input("Detalhe (opcional)")
        jogador = st.selectbox("Jogador (opcional)", [""] + jogadores_partida)
        time = st.selectbox("Time (opcional)", ["", time_a, time_b])
        comentario = st.text_input("Comentário (opcional)")
        submit = st.form_submit_button("Registrar Evento")
        if submit:
            salvar_evento(acao, detalhe, jogador, time, comentario)

    st.markdown("---")
    st.subheader("Relógio do Jogo")
    col_relogio1, col_relogio2 = st.columns(2)
    col_relogio1.button("Iniciar", on_click=start_clock)
    col_relogio2.button("Pausar", on_click=pause_clock)
    st.write(f"⏱ Tempo de Jogo: {tempo_jogo()}")

with col2:
    st.subheader("📋 Eventos Registrados")
    df_eventos = pd.DataFrame(st.session_state.eventos)
    st.dataframe(df_eventos)

    if st.button("Finalizar e Exportar CSV"):
        df_eventos.to_csv(st.session_state.csv_jogo, index=False)
        st.success(f"Jogo exportado para {st.session_state.csv_jogo}")
