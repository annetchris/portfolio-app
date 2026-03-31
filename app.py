import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import io
from PIL import Image

# 1. Pagina Configuratie
st.set_page_config(page_title="Portfolio Assistent Safe-Mode", page_icon="🎓", layout="wide")

# --- AI INSTELLEN (Alleen voor tekst) ---
API_KEY = "AIzaSyC7AYzC8Fmi971V_C8yZ6hVuUwCPv9AJZI" 
genai.configure(api_key=API_KEY)
# We gebruiken 'gemini-pro', dit is het meest stabiele tekstmodel ter wereld
model = genai.GenerativeModel('gemini-pro')

# --- HOOFDSCHERM ---
st.title("🎓 :blue[Mijn Praktijk Portfolio] :orange[Assistent]")
st.write("Versie 1.2: Stabiliteitsmodus (AI op basis van tekst)")

col1, col2 = st.columns(2)

with col1:
    st.header("1. De Opdracht")
    werk_situatie = st.text_area("Wat is je werksituatie?", placeholder="Bijv: Ik werk in de gehandicaptenzorg...")
    opdracht_beschrijving = st.text_area("Wat is de opdracht van school?", placeholder="Typ hier kort wat er op je blaadje staat...")
    uploaded_files = st.file_uploader("Upload foto's voor in je PDF", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

with col2:
    st.header("2. Jouw Reflectie")
    st_actie = st.text_area("Wat heb je precies gedaan?", placeholder="Ik heb...")
    st_resultaat = st.text_area("Wat was het resultaat?", placeholder="De cliënt...")

# 3. Genereren (Zonder dat de AI de foto's hoeft te 'zien')
if st.button("✨ Genereer STARR-Verslag", use_container_width=True):
    if werk_situatie and opdracht_beschrijving:
        with st.spinner('🚀 AI schrijft je verslag...'):
            try:
                prompt = f"""
                Schrijf een professioneel STARR-verslag op basis van:
                Situatie: {werk_situatie}
                Opdracht: {opdracht_beschrijving}
                Mijn Actie: {st_actie}
                Resultaat: {st_resultaat}
                Zorg voor een leerzame en professionele toon voor een zorg-portfolio.
                """
                response = model.generate_content(prompt)
                st.session_state['ai_output'] = response.text
                st.balloons()
            except Exception as e:
                st.error(f"AI Fout: {e}. Probeer de tekst iets korter te maken.")
    else:
        st.warning("Vul a.u.b. de situatie en opdrachtbeschrijving in!")

# 4. Resultaat & PDF
if 'ai_output' in st.session_state:
    st.divider()
    st.markdown(st.session_state['ai_output'])

    if st.button("📄 Downloaden als PDF (inclusief foto's)"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Mijn STARR Portfolio Verslag", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", '', 11)
        clean_text = st.session_state['ai_output'].replace("**", "").replace("#", "")
        pdf.multi_cell(0, 7, txt=clean_text.encode('latin-1', 'ignore').decode('latin-1'))
        
        # Foto's toevoegen aan de PDF
        if uploaded_files:
            pdf.add_page()
            pdf.cell(0, 10, "Bijlagen (Bewijslast):", ln=True)
            for f in uploaded_files:
                img = Image.open(f)
                # Tijdelijk opslaan om in PDF te zetten
                img_path = f"temp_{f.name}"
                img.save(img_path)
                pdf.image(img_path, x=10, w=100) # Voeg foto toe (10cm breed)
                pdf.ln(5)

        pdf_output = pdf.output(dest='S').encode('latin-1', 'ignore')
        st.download_button("Klik hier om PDF op te slaan", data=pdf_output, file_name="Portfolio_Verslag.pdf")
