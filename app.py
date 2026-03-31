import streamlit as st
import PIL.Image
import google.generativeai as genai
from fpdf import FPDF
import io

# 1. Pagina Configuratie
st.set_page_config(
    page_title="Portfolio Assistent Pro", 
    page_icon="🎓", 
    layout="wide"
)

# --- AI INSTELLEN ---
# Zorg dat je hier jouw eigen API Key tussen de aanhalingstekens hebt staan!
API_KEY = "AIzaSyC7AYzC8Fmi971V_C8yZ6hVuUwCPv9AJZI" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash')

# --- SIDEBAR (Zijbalk) ---
with st.sidebar:
    st.header("🛠️ Hoe werkt het?")
    st.info("""
    1. **Situatie:** Vertel waar je werkt.
    2. **Scan:** Upload één of meerdere foto's van je opdracht.
    3. **Reflectie:** Vul in wat je hebt gedaan.
    4. **Download:** Sla je STARR-verslag op als PDF!
    """)
    st.divider()
    st.write("V1.1 - Nu met ondersteuning voor meerdere foto's")

# --- HOOFDSCHERM ---
st.title("🎓 :blue[Mijn Praktijk Portfolio] :orange[Assistent]")
st.write("Verander je praktijkopdrachten (ook meerdere pagina's) direct in een professioneel reflectieverslag.")

# 2. Input Sectie
col1, col2 = st.columns(2)

with col1:
    st.header("1. De Opdracht")
    werk_situatie = st.text_area(
        "Wat is je huidige werksituatie?", 
        placeholder="Bijv: Ik loop stage in de gehandicaptenzorg...",
        help="Beschrijf je doelgroep en je rol."
    )

    input_methode = st.radio("Hoe voeg je de opdracht toe?", ("Foto maken 📸", "Bestanden uploaden 📁"))

    uploaded_files = []
    if input_methode == "Foto maken 📸":
        camera_photo = st.camera_input("Maak een foto van de opdracht")
        if camera_photo:
            uploaded_files.append(camera_photo)
    else:
        # Hier is 'accept_multiple_files=True' toegevoegd
        uploaded_files = st.file_uploader("Upload afbeelding(en)", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

with col2:
    st.header("2. Jouw Reflectie")
    st.write("Vul dit in nadat je de opdracht hebt uitgevoerd.")
    st_actie = st.text_area("Wat heb je precies gedaan? (Actie)", placeholder="Ik heb de cliënt begeleid bij...")
    st_resultaat = st.text_area("Wat was het resultaat?", placeholder="De cliënt voelde zich veilig en...")

# 3. Logica voor Genereren
if st.button("✨ Genereer Advies & STARR-Verslag", use_container_width=True):
    if werk_situatie and uploaded_files:
        with st.spinner('🚀 AI analyseert alle foto\'s en schrijft je verslag...'):
            try:
                # De Geoptimaliseerde STARR Prompt
                prompt = f"""
                Kijk naar de afbeeldingen van de schoolopdracht en gebruik deze context:
                - Werksituatie: {werk_situatie}
                - Gebruikers actie: {st_actie}
                - Resultaat: {st_resultaat}

                Instructies:
                1. Geef 3 concrete praktijkvoorbeelden passend bij de opdracht op de foto's.
                2. Schrijf een officieel STARR-verslag (Situatie, Taak, Actie, Resultaat, Reflectie).
                3. Gebruik een professionele, leergerichte toon voor een stageportfolio.
                4. Gebruik duidelijke kopjes.
                """
                
                # We maken de lijst voor de AI: eerst de tekst, dan alle foto's
                inhoud_voor_ai = [prompt]
                for f in uploaded_files:
                    if f is not None:
                        img = PIL.Image.open(f)
                        inhoud_voor_ai.append(img)
                
                # Stuur alles in één keer naar het model
                response = model.generate_content(inhoud_voor_ai)
                st.session_state['ai_output'] = response.text
                
                st.balloons()
                st.success(f"✅ Analyse van {len(uploaded_files)} foto('s) voltooid!")
                
            except Exception as e:
                st.error(f"Er is een fout opgetreden: {e}")
    else:
        st.warning("⚠️ Zorg dat je zowel de werksituatie invult als minimaal één foto toevoegt!")

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
            pdf.multi_cell(0, 7, txt=werk_situatie.encode('latin-1', 'ignore').decode('latin-1'))
            pdf.ln(5)
            
            # Sectie: AI Analyse
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Analyse en STARR-Reflectie:", ln=True)
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
