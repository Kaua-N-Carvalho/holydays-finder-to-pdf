import PyPDF2
import requests
import tkinter
import re
from tkinter.filedialog import askopenfilename
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from textwrap import wrap

#Fazer chamada api
def ChamadaAPI(Ano):
    url = "https://date.nager.at/api/v3/PublicHolidays/" + Ano + "/BR"
    payload = {}
    headers = {
      'accept': 'application/json'
      }
    response = requests.request("GET", url, headers=headers, data=payload)

    return response.text

#Transformar texto em pdf
def text_to_pdf(text, output_pdf="resultado.pdf"):
    page_width, page_height = A4
    margin = 50
    line_height = 14

    pdf = canvas.Canvas(output_pdf, pagesize=A4)

    max_chars = 90  
    lines = []
    for paragraph in text.split("\n"):
        wrapped = wrap(paragraph, max_chars)
        lines.extend(wrapped if wrapped else [""])

    y = page_height - margin

    for line in lines:
        if y < margin:  # Nova página
            pdf.showPage()
            y = page_height - margin

        pdf.drawString(margin, y, line)
        y -= line_height

    pdf.save()
    print("PDF gerado:", output_pdf)

#Ler Texto
def processar_texto():
    texto = text_box.get("1.0", "end").strip()
    datas = re.findall(r"\d{4}-\d{2}-\d{2}", texto)
    anos = set(d.split("-")[0] for d in datas)
    resposta = ""

    def pegar_feriados(texto_datas, datas_procuradas):
        resultado = ""
        feriado_regex = r'\{(.*?)\}'
        feriados = re.findall(feriado_regex, texto_datas, re.DOTALL)

        for f in feriados:
            data_match = re.search(r'"date"\s*:\s*"([^"]+)"', f)
            if data_match:
                data = data_match.group(1)
                if data in datas_procuradas:
                    resultado += f"{data}\n"
        return resultado

    for ano in anos:
        feriados_texto = ChamadaAPI(ano)
        resposta += pegar_feriados(feriados_texto, datas)

    texto_final = texto + "\n\nFERIADOS ENCONTRADOS\n" + resposta
    text_to_pdf(texto_final)

#Interface
def Exemplo():
    global text_box
    
    root = tkinter.Tk()
    root.title("Escreva o texto")
    root.resizable(True, True)

    text_box = tkinter.Text(root, width=80, height=20)
    text_box.pack()
    
    generate_from_text = tkinter.Button(root, text="Criar PDF")
    generate_from_text['command'] = processar_texto
    generate_from_text.pack()
    root.mainloop()

Exemplo()
