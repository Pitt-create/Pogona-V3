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

# Styles CSS personnalisés
st.markdown("""
<style>
    /* Styles existants */
    .main {
        background-color: #f0f7f4;
        padding: 2rem;
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
        margin: 5px;
    }
    
    .prompt-chip:hover {
        background-color: #2c5282;
        color: white;
        transform: translateY(-2px);
    }
    
    .prompt-section {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
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
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = generate_session_id()

    # Titre
    st.title("🐾 VeterinarIAn")

    # Création de deux colonnes
    col1, col2 = st.columns([2, 1])

    with col1:
        # Zone de chat principale
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

    with col2:
        # Section des prompts suggérés
        st.markdown("### 💡 Questions suggérées")
        
        for category, prompts in SUGGESTED_PROMPTS.items():
            with st.expander(f"📍 {category}", expanded=True):
                for prompt in prompts:
                    if st.button(prompt, key=f"prompt_{prompt}", help="Cliquez pour utiliser cette question"):
                        # Ajouter directement le message à l'historique
                        st.session_state.messages.append({"role": "user", "content": prompt})
                        with st.chat_message("user"):
                            st.write(prompt)
                        
                        # Obtenir et afficher la réponse
                        with st.spinner('VeterinarIAn réfléchit...'):
                            llm_response = send_message_to_llm(st.session_state.session_id, prompt)
                        
                        st.session_state.messages.append({"role": "assistant", "content": llm_response})
                        with st.chat_message("assistant"):
                            st.write(llm_response)
                        
                        # Forcer le rafraîchissement de la page
                        st.rerun()

    # Zone de saisie de texte
    user_input = st.chat_input(placeholder="Posez votre question ici...")

    if user_input:
        # Ajouter le message utilisateur
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Obtenir et afficher la réponse
        with st.spinner('VeterinarIAn réfléchit...'):
            llm_response = send_message_to_llm(st.session_state.session_id, user_input)

        st.session_state.messages.append({"role": "assistant", "content": llm_response})
        with st.chat_message("assistant"):
            st.write(llm_response)

if __name__ == "__main__":
    main()
