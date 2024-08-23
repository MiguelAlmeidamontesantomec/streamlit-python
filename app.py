import cv2
import numpy as np
import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
import pandas as pd
import re  # Para validação de padrão

def detect_barcode(frame):
    """Detecta códigos de barras na imagem fornecida e retorna uma lista com as informações dos códigos de barras."""
    decoded_objects = decode(frame)
    valid_barcodes = []
    for obj in decoded_objects:
        barcode_data = obj.data.decode('utf-8')
        
        # Validar se o código segue o padrão alfanumérico de 13 caracteres
        if re.fullmatch(r'[A-Za-z0-9]{13}', barcode_data):
            valid_barcodes.append(barcode_data)
            points = obj.polygon
            if len(points) == 4:
                pts = np.array(points, dtype=np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
                cv2.putText(frame, barcode_data, (pts[0][0][0], pts[0][0][1] - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return frame, valid_barcodes

def main():
    st.title("Leitor de Códigos de Barras")

    # Captura de vídeo da webcam
    video_capture = cv2.VideoCapture(0)

    detected_barcodes = set()  # Armazena códigos de barras detectados

    # Containers para layout em colunas
    col1, col2 = st.columns([3, 2])  # Ajuste os pesos conforme necessário

    with col1:
        st.subheader("Vídeo da Câmera")
        stframe = st.empty()  # Placeholder para o vídeo da câmera

    with col2:
        st.subheader("Último Código Lido")
        last_code_display = st.empty()  # Placeholder para o último código lido
        count_display = st.empty()  # Placeholder para a contagem de códigos

    # Cria o expander para a tabela
    with st.expander("Exibir tabela de códigos lidos", expanded=False):
        codes_table = st.empty()  # Placeholder para a tabela de códigos lidos

    while True:
        ret, frame = video_capture.read()
        if not ret:
            st.error("Não foi possível capturar o vídeo.")
            break

        # Detecção de códigos de barras
        frame, valid_barcodes = detect_barcode(frame)

        # Convertendo o frame para um formato exibível no Streamlit
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb_frame)

        # Exibindo o frame na interface do Streamlit
        stframe.image(image, use_column_width=True)

        # Atualiza o último código lido
        new_codes = []
        if valid_barcodes:
            for barcode_data in valid_barcodes:
                if barcode_data not in detected_barcodes:
                    detected_barcodes.add(barcode_data)
                    new_codes.append(barcode_data)

        # Atualiza o último código lido
        if new_codes:
            last_code = new_codes[-1]
            last_code_display.write(f"**Último Código Lido:** {last_code}")

        # Atualiza a contagem de códigos lidos
        count_display.write(f"**Contagem Atual:** {len(detected_barcodes)}")

        # Atualiza a tabela de códigos lidos no expander
        if detected_barcodes:
            codes_table.table(pd.DataFrame(list(detected_barcodes), columns=["Códigos Lidos"]))

    # Libere o recurso de vídeo
    video_capture.release()

if __name__ == "__main__":
    main()
