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
    
    /* Style for chat input */
    .stChatInput>div>div>textarea {
        border-radius: 25px;
        padding: 10px 20px;
        border: 2px solid #2c5282;
        background-color: white;
    }
    
    /* Style for send button */
    .stButton>button {
        background-color: #2c5282;
        color: white;
        border-radius: 25px;
        padding: 10px 30px;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #1a365d;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Constants
WEBHOOK_URL = "https://pitt-create.app.n8n.cloud/webhook/e985d15f-b2f6-456d-be15-97e0b1544a40/chat"
BEARER_TOKEN = "Pittcreate82"

# Définition des prompts suggérés par catégorie
SUGGESTED_PROMPTS = {
    "Anatomie et Physiologie": [
        "🧠 Expliquez le fonctionnement du système nerveux chez les chiens.",
        "❤️ Comment fonctionne le système cardiovasculaire des chats ?",
        "🦴 Quelles sont les principales différences anatomiques entre chiens et chats ?"
    ],
    "Nutrition et Santé": [
        "🥩 Quels sont les nutriments essentiels pour une alimentation équilibrée des chiens ?",
        "🐱 Expliquez les besoins nutritionnels spécifiques des chats âgés.",
        "🦮 Comment l'alimentation peut-elle influencer la santé articulaire des grands chiens ?"
    ],
    "Comportement et Cognition": [
        "🧠 Quels sont les processus d'apprentissage chez les chiens ?",
        "😺 Comment les chats communiquent-ils entre eux et avec les humains ?",
        "🐕 Expliquez le concept de socialisation précoce chez les chiots."
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
    if "current_prompt" not in st.session_state:
        st.session_state.current_prompt = ""

    # Titre
    st.title("🐾 VeterinarIAn - Assistant Éducatif Vétérinaire")

    # Création de deux colonnes
    col1, col2 = st.columns([2, 1])

    with col1:
        # Zone de chat principale
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

        # Affichage du prompt sélectionné
        if st.session_state.current_prompt:
            st.info(f"Prompt sélectionné : {st.session_state.current_prompt}")

        # Zone de saisie de texte
        user_input = st.chat_input(placeholder="Modifiez ou posez votre question ici...")

        if user_input:
            # Traitement du message utilisateur
            full_input = user_input if not st.session_state.current_prompt else f"{st.session_state.current_prompt} {user_input}"
            
            # Ajouter le message utilisateur
            st.session_state.messages.append({"role": "user", "content": full_input})
            with st.chat_message("user"):
                st.write(full_input)

            # Obtenir et afficher la réponse
            with st.spinner('VeterinarIAn réfléchit...'):
                llm_response = send_message_to_llm(st.session_state.session_id, full_input)

            st.session_state.messages.append({"role": "assistant", "content": llm_response})
            with st.chat_message("assistant"):
                st.write(llm_response)

            # Réinitialiser le prompt courant
            st.session_state.current_prompt = ""
            st.rerun()

    with col2:
        # Section des prompts suggérés
        st.markdown("### 💡 Sujets d'apprentissage suggérés")
        
        for category, prompts in SUGGESTED_PROMPTS.items():
            with st.expander(f"📍 {category}", expanded=True):
                for prompt in prompts:
                    if st.button(prompt, key=f"prompt_{prompt}", help="Cliquez pour utiliser ce sujet d'apprentissage"):
                        st.session_state.current_prompt = prompt
                        st.rerun()

if __name__ == "__main__":
    main()
