import streamlit as st
import PIL.Image
import google.generativeai as genai
from fpdf import FPDF
import io

# 1. Pagina Configuratie
st.set_page_config(
    page_title="Portfolio Assistent", 
    page_icon="🎓", 
    layout="wide"
)

# --- AI INSTELLEN ---
# Vervang 'JOUW_API_KEY' door de sleutel van Google AI Studio
# Voor veiligheid op Streamlit Cloud gebruik je: st.secrets["GOOGLE_API_KEY"]
API_KEY = "JOUW_API_KEY_HIER" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- SIDEBAR (Zijbalk) ---
with st.sidebar:
    st.header("🛠️ Hoe werkt het?")
    st.info("""
    1. **Situatie:** Vertel waar je werkt.
    2. **Scan:** Maak een foto van je opdracht.
    3. **Reflectie:** Vul je acties in.
    4. **Download:** Sla je STARR-verslag op!
    """)
    st.divider()
    st.write("V1.0 - Gemaakt voor Studenten")

# --- HOOFDSCHERM ---
st.title("🎓 :blue[Mijn Praktijk Portfolio] :orange[Assistent]")
st.write("Verander je praktijkopdrachten direct in een professioneel reflectieverslag.")

# 2. Input Sectie
col1, col2 = st.columns(2)

with col1:
    st.header("1. De Opdracht")
    werk_situatie = st.text_area(
        "Wat is je huidige werksituatie?", 
        placeholder="Bijv: Ik loop stage bij een fysiotherapiepraktijk...",
        help="Beschrijf je doelgroep en je rol."
    )

    input_methode = st.radio("Hoe voeg je de opdracht toe?", ("Foto maken 📸", "Bestand uploaden 📁"))

    if input_methode == "Foto maken 📸":
        uploaded_file = st.camera_input("Maak een foto van de opdracht")
    else:
        uploaded_file = st.file_uploader("Upload afbeelding", type=['jpg', 'jpeg', 'png'])

with col2:
    st.header("2. Jouw Reflectie")
    st.write("Vul dit in nadat je de opdracht hebt uitgevoerd.")
    st_actie = st.text_area("Wat heb je precies gedaan? (Actie)", placeholder="Ik heb de patiënt geholpen met...")
    st_resultaat = st.text_area("Wat was het resultaat?", placeholder="De patiënt kon weer zelfstandig...")

# 3. Logica voor Genereren
if st.button("✨ Genereer Advies & STARR-Verslag", use_container_width=True):
    if werk_situatie and uploaded_file:
        with st.spinner('🚀 AI analyseert je foto en schrijft je verslag...'):
            try:
                image = PIL.Image.open(uploaded_file)
                
                # De Geoptimaliseerde STARR Prompt
                prompt = f"""
                Kijk naar de afbeelding van de schoolopdracht en gebruik deze context:
                - Werksituatie: {werk_situatie}
                - Gebruikers actie: {st_actie}
                - Resultaat: {st_resultaat}

                Geef eerst 3 concrete praktijkvoorbeelden passend bij de opdracht op de foto.
                Schrijf daarna een officieel STARR-verslag (Situatie, Taak, Actie, Resultaat, Reflectie).
                Zorg voor een professionele, leergerichte toon voor een stageportfolio.
                Gebruik duidelijke kopjes.
                """
                
                response = model.generate_content([prompt, image])
                st.session_state['ai_output'] = response.text
                
                st.balloons()
                st.success("✅ Je verslag is gegenereerd!")
                
            except Exception as e:
                st.error(f"Er is een fout opgetreden: {e}")
    else:
        st.warning("⚠️ Zorg dat je zowel de werksituatie invult als een foto toevoegt!")

# 4. Resultaat & Export
if 'ai_output' in st.session_state:
    st.divider()
    with st.container(border=True):
        st.subheader("📋 Jouw Resultaat")
        st.markdown(st.session_state['ai_output'])

    # PDF Export Knop
    if st.button("📄 Downloaden als PDF"):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Praktijkverslag & STARR", ln=True, align='C')
            pdf.ln(10)
            
            # Sectie: Situatie
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Mijn Werksituatie:", ln=True)
            pdf.set_font("Arial", '', 11)
            pdf.multi_cell(0, 7, txt=werk_situatie)
            pdf.ln(5)
            
            # Sectie: AI Analyse
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "AI Analyse & Reflectie:", ln=True)
            pdf.set_font("Arial", '', 11)
            
            # Opschonen van Markdown tekens voor PDF
            clean_text = st.session_state['ai_output'].replace("**", "").replace("#", "")
            pdf.multi_cell(0, 7, txt=clean_text.encode('latin-1', 'ignore').decode('latin-1'))
            
            pdf_output = pdf.output(dest='S').encode('latin-1', 'ignore')
            st.download_button(
                label="Klik hier om PDF op te slaan",
                data=pdf_output,
                file_name="Mijn_Portfolio_Verslag.pdf",
                mime="application/pdf"
            )
            st.toast("PDF gereed!", icon="✅")
        except Exception as e:
            st.error(f"PDF fout: {e}")
