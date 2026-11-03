import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator

st.set_page_config(page_title="Control por voz", page_icon="🎙️", layout="centered")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600&family=Nunito:wght@400;600;700&display=swap');

    :root {
        --cream: #FFF9F4;
        --lilac: #E9DEFF;
        --lilac-deep: #C9B3F5;
        --pink: #FFD3E2;
        --peach: #FFE2CF;
        --mint: #CDF2E3;
        --sky: #CFE7FF;
        --ink: #4B4266;
        --ink-soft: #8A82A3;
    }

    html, body, [class*="css"], .stApp { font-family: 'Nunito', system-ui, sans-serif; }

    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background:
            radial-gradient(circle at 12% 8%, var(--pink) 0, transparent 38%),
            radial-gradient(circle at 90% 18%, var(--sky) 0, transparent 36%),
            radial-gradient(circle at 70% 95%, var(--mint) 0, transparent 40%),
            var(--cream) !important;
        color: var(--ink) !important;
    }
    .block-container { padding-top: 2.2rem; max-width: 680px; text-align: center; }

    header[data-testid="stHeader"] { background: transparent !important; }
    header[data-testid="stHeader"] * { color: var(--ink) !important; fill: var(--ink) !important; }

    .stApp h1 {
        font-family: 'Fredoka', sans-serif;
        color: var(--ink) !important;
        font-size: 2.2rem;
        font-weight: 600;
        letter-spacing: 0.01em;
        padding: 1.1rem 1rem 0.2rem 1rem;
        margin: 0;
        background: linear-gradient(135deg, var(--lilac), var(--pink));
        border-radius: 28px 28px 0 0;
    }
    .stApp h3 {
        font-family: 'Fredoka', sans-serif;
        color: var(--ink-soft) !important;
        font-size: 1.05rem;
        font-weight: 500;
        padding: 0 1rem 1.2rem 1rem;
        margin: 0 0 1.4rem 0;
        background: linear-gradient(135deg, var(--lilac), var(--pink));
        border-radius: 0 0 28px 28px;
    }

    .stApp p, .stApp label, .stApp li { color: var(--ink) !important; }

    [data-testid="stImage"] { display: flex; justify-content: center; margin-bottom: 0.6rem; }
    [data-testid="stImage"] img {
        border-radius: 50%;
        border: 6px solid #FFFFFF;
        box-shadow: 0 8px 24px rgba(201, 179, 245, 0.55);
        aspect-ratio: 1 / 1;
        object-fit: cover;
    }

    [data-testid="stMarkdownContainer"] p {
        font-size: 1.02rem;
        font-weight: 600;
    }

    #MainMenu, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def on_publish(client, userdata, result):  # create function for callback
    print("el dato ha sido publicado \n")
    pass


def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)


broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("GIT-HUBC")
client1.on_message = on_message


st.title("INTERFACES MULTIMODALES")
st.subheader("CONTROL POR VOZ")

image = Image.open('voice_ctrl.jpg')

st.image(image, width=200)


st.write("Toca el Botón y habla ")

# El botón vive dentro de un iframe, así que su estilo se define con una
# hoja de estilos de Bokeh (disponible en Bokeh 3.x). En versiones
# anteriores se muestra el botón por defecto.
BUTTON_CSS = """
.bk-btn {
    font-family: 'Fredoka', 'Nunito', sans-serif;
    font-size: 17px;
    font-weight: 600;
    color: #4B4266;
    background: linear-gradient(135deg, #FFD3E2, #C9B3F5);
    border: 3px solid #FFFFFF;
    border-radius: 999px;
    box-shadow: 0 6px 18px rgba(201, 179, 245, 0.6);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.bk-btn:hover {
    background: linear-gradient(135deg, #CDF2E3, #CFE7FF);
    box-shadow: 0 8px 22px rgba(160, 210, 230, 0.7);
    transform: translateY(-2px);
}
.bk-btn:active { transform: translateY(0); }
.bk-btn:focus-visible { outline: 3px solid #4B4266; outline-offset: 3px; }
"""

try:
    from bokeh.models import InlineStyleSheet
    stt_button = Button(label=" Inicio ", width=200, stylesheets=[InlineStyleSheet(css=BUTTON_CSS)])
except Exception:
    stt_button = Button(label=" Inicio ", width=200)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        st.write(result.get("GET_TEXT"))
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": result.get("GET_TEXT").strip()})
        ret = client1.publish("voice_ctrl", message)

    try:
        os.mkdir("temp")
    except:
        pass
