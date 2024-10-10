import streamlit as st
import requests
import uuid

# Configuration de la page
st.set_page_config(
    page_title="VeterinarIAn",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styles CSS personnalisés avec ajout des styles pour les prompts suggérés
st.markdown("""
<style>
    /* Styles existants */
    .main {
        background-color: #f0f7f4;
        padding: 2rem;
    }
    
    .title-container {
        background-color: #2c5282;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .main-title {
        color: white;
        font-size: 3rem;
        font-weight: bold;
        margin: 0;
    }
    
    /* Styles pour les prompts suggérés */
    .suggested-prompts {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 20px 0;
        padding: 20px;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .prompt-chip {
        background-color: #f0f7ff;
        border: 1px solid #2c5282;
        color: #2c5282;
        padding: 8px 16px;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.9rem;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }
    
    .prompt-chip:hover {
        background-color: #2c5282;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .prompt-section {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .prompt-section h3 {
        color: #2c5282;
        margin-bottom: 15px;
    }
    
    /* Autres styles existants */
    .stChatMessage {...}
    .user-message {...}
    .assistant-message {...}
    .stTextInput>div>div>input {...}
    .stButton>button {...}
</style>
""", unsafe_allow_html=True)

# Constants
WEBHOOK_URL = "https://pitt-create.app.n8n.cloud/webhook/e985d15f-b2f6-456d-be15-97e0b1544a40/chat"
BEARER_TOKEN = "Pittcreate82"

# Définition des prompts suggérés par catégorie
SUGGESTED_PROMPTS = {
    "Premiers secours": [
        "🚨 Que faire si mon animal s'est coupé ?",
        "🤒 Mon chien a de la fièvre, que dois-je faire ?",
        "💊 Quels sont les signes d'urgence chez un chat ?"
    ],
    "Nutrition": [
        "🥩 Quels aliments sont toxiques pour les chiens ?",
        "🐱 Comment calculer la ration alimentaire de mon chat ?",
        "🦮 Mon chien est en surpoids, que faire ?"
    ],
    "Comportement": [
        "😿 Mon chat griffe les meubles, comment l'en empêcher ?",
        "🐕 Comment gérer l'anxiété de séparation ?",
        "🐈 Pourquoi mon chat miaule la nuit ?"
    ]
}

def generate_session_id():
    return str(uuid.uuid4())

def send_message_to_llm(session_id, message):
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "sessionId": session_id,
        "chatInput": message
    }
    response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["output"]
    else:
        return f"Error: {response.status_code} - {response.text}"

def main():
    # Titre stylisé
    st.markdown('<div class="title-container"><h1 class="main-title">🐾 VeterinarIAn</h1></div>', unsafe_allow_html=True)

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = generate_session_id()
    if "current_prompt" not in st.session_state:
        st.session_state.current_prompt = ""

    # Création de deux colonnes
    col1, col2 = st.columns([2, 1])

    with col1:
        # Zone de chat principale
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(f'<div class="{message["role"]}-message">{message["content"]}</div>', 
                              unsafe_allow_html=True)

    with col2:
        # Sidebar avec prompts suggérés
        st.markdown("### 💡 Questions suggérées")
        
        for category, prompts in SUGGESTED_PROMPTS.items():
            st.markdown(f"#### {category}")
            for prompt in prompts:
                if st.button(prompt, key=f"prompt_{prompt}"):
                    st.session_state.current_prompt = prompt

    # Zone de saisie avec le prompt sélectionné
    user_input = st.chat_input(placeholder="Que voulez-vous apprendre aujourd'hui ?", 
                              key="chat_input",
                              value=st.session_state.current_prompt)

    if user_input:
        # Réinitialiser le prompt sélectionné
        st.session_state.current_prompt = ""
        
        # Ajouter le message utilisateur
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(f'<div class="user-message">{user_input}</div>', 
                       unsafe_allow_html=True)

        # Obtenir et afficher la réponse
        with st.spinner('VeterinarIAn réfléchit...'):
            llm_response = send_message_to_llm(st.session_state.session_id, user_input)

        st.session_state.messages.append({"role": "assistant", "content": llm_response})
        with st.chat_message("assistant"):
            st.markdown(f'<div class="assistant-message">{llm_response}</div>', 
                       unsafe_allow_html=True)

if __name__ == "__main__":
    main()
