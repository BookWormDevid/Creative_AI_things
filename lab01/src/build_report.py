"""Build the local lab report, passport and illustrations without third-party packages."""
from __future__ import annotations

import html
import json
import math
import statistics
import struct
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape

import lab01_generator as gen

LAB = Path(__file__).resolve().parents[1]
REPORTS = LAB / "reports"
RUN = LAB / "artifacts/fresh_run"
PROTOCOL_COMMIT = "e73126aca3128e50746329a8fb4db4f81ddeaba3"
NAMES = {"mean": "Средняя яркость", "contrast": "Контраст", "edge": "Граничная энергия", "entropy": "Энтропия, бит"}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def number(x, digits=6):
    return f"{x:.{digits}f}".replace(".", ",")


class Document:
    def __init__(self):
        self.blocks = []

    def p(self, text, kind="p"):
        self.blocks.append((kind, text))

    def table(self, headers, rows):
        self.blocks.append(("table", [headers, *rows]))

    def image(self, path, caption):
        self.blocks.append(("image", (path, caption)))

    def save(self, stem):
        md, web = [], []
        for kind, data in self.blocks:
            if kind == "table":
                clean = lambda v: str(v).replace("|", "∣").replace("\n", " ")
                md += ["| " + " | ".join(map(clean, data[0])) + " |", "|" + " --- |" * len(data[0])]
                md += ["| " + " | ".join(map(clean, row)) + " |" for row in data[1:]] + [""]
                web.append("<table><thead><tr>" + "".join("<th>" + html.escape(str(c)) + "</th>" for c in data[0]) + "</tr></thead><tbody>"
                           + "".join("<tr>" + "".join("<td>" + html.escape(str(c)) + "</td>" for c in row) + "</tr>" for row in data[1:]) + "</tbody></table>")
            elif kind == "image":
                path, caption = data
                rel = path.relative_to(REPORTS).as_posix()
                md += [f"![{caption}]({rel})", "", caption, ""]
                web.append(f'<figure><img src="{rel}" alt="{html.escape(caption)}"><figcaption>{html.escape(caption)}</figcaption></figure>')
            elif kind == "break":
                md += ["---", ""]
                web.append('<div class="pagebreak"></div>')
            else:
                prefix = {"h1": "# ", "h2": "## ", "title": "# "}.get(kind, "")
                md += [prefix + data, ""]
                tag = {"h1": "h1", "h2": "h2", "code": "pre", "title": "h1"}.get(kind, "p")
                web.append(f'<{tag} class="{kind}">{html.escape(data)}</{tag}>')
        stem.with_suffix(".md").write_text("\n".join(md), encoding="utf-8")
        css = """@page{size:A4;margin:20mm 15mm 20mm 25mm}body{font:12pt 'Times New Roman',serif;color:#111;line-height:1.45}
        h1{font-size:16pt;margin:20pt 0 10pt;break-after:avoid}h2{font-size:13pt;break-after:avoid}p{text-align:justify;margin:0 0 9pt}
        .title{text-align:center;font-size:18pt;margin-top:45pt}.center{text-align:center}.blank{text-align:right;margin-top:15pt}
        table{border-collapse:collapse;width:100%;font-size:9pt;line-height:1.2;margin:10pt 0 14pt;table-layout:fixed}
        th,td{border:1px solid #777;padding:5px;overflow-wrap:anywhere;vertical-align:top}th{background:#eee}thead{display:table-header-group}
        tr{break-inside:avoid}pre{font:9pt Consolas,monospace;white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f4f4;padding:8px;line-height:1.25}
        figure{margin:12pt 0;break-inside:avoid;text-align:center}img{max-width:100%;image-rendering:pixelated}figcaption{font-size:10pt}
        .pagebreak{break-before:page}*{-webkit-print-color-adjust:exact;print-color-adjust:exact}"""
        stem.with_suffix(".html").write_text('<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ЛР 1 — вариант 27</title><style>'
                                             + css + "</style></head><body>" + "\n".join(web) + "</body></html>", encoding="utf-8")
        make_docx(self.blocks, stem.with_suffix(".docx"))


def make_docx(blocks, target):
    """A small native OOXML writer: paragraphs, repeating table headers, PNG images."""
    relationships = ['<Relationship Id="styles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>']
    media = []
    body = []

    def paragraph(text, style="Normal", small=False, center=False):
        props = f'<w:pStyle w:val="{style}"/>' + ('<w:jc w:val="center"/>' if center else "")
        runs = "".join('<w:r>' + ('<w:rPr><w:sz w:val="18"/></w:rPr>' if small else "")
                       + '<w:t xml:space="preserve">' + escape(line) + '</w:t></w:r>'
                       + ('<w:r><w:br/></w:r>' if i < len(text.split("\n")) - 1 else "") for i, line in enumerate(text.split("\n")))
        return '<w:p><w:pPr>' + props + '</w:pPr>' + runs + '</w:p>'

    for kind, data in blocks:
        if kind == "break":
            body.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        elif kind == "table":
            cols = len(data[0])
            width = 9350 // cols
            tbl = '<w:tbl><w:tblPr><w:tblW w:w="9350" w:type="dxa"/><w:tblLayout w:type="fixed"/>'
            tbl += '<w:tblBorders>' + "".join(f'<w:{x} w:val="single" w:sz="4" w:color="777777"/>' for x in ("top", "left", "bottom", "right", "insideH", "insideV")) + '</w:tblBorders>'
            tbl += '<w:tblCellMar><w:top w:w="60" w:type="dxa"/><w:left w:w="70" w:type="dxa"/><w:bottom w:w="60" w:type="dxa"/><w:right w:w="70" w:type="dxa"/></w:tblCellMar></w:tblPr>'
            tbl += '<w:tblGrid>' + f'<w:gridCol w:w="{width}"/>' * cols + '</w:tblGrid>'
            for i, row in enumerate(data):
                tbl += '<w:tr><w:trPr><w:cantSplit/>' + ('<w:tblHeader/>' if i == 0 else "") + '</w:trPr>'
                for cell in row:
                    tbl += f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>' + ('<w:shd w:fill="EEEEEE"/>' if i == 0 else "") + '</w:tcPr>' + paragraph(str(cell), "TableText", small=True) + '</w:tc>'
                tbl += '</w:tr>'
            body.append(tbl + '</w:tbl>')
        elif kind == "image":
            path, caption = data
            idx = len(media) + 1
            image_data = path.read_bytes()
            w, h = struct.unpack(">II", image_data[16:24])
            cx, cy = 5600000, round(5600000 * h / w)
            rid = f"image{idx}"
            relationships.append(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image{idx}.png"/>')
            media.append((f"word/media/image{idx}.png", image_data))
            body.append(f'''<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{idx}" name="Figure {idx}"/><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="0" name="image{idx}.png"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>''')
            body.append(paragraph(caption, "Caption", center=True))
        else:
            style = {"h1": "Heading1", "h2": "Heading2", "title": "Title", "code": "Code"}.get(kind, "Normal")
            body.append(paragraph(data, style, center=kind in ("title", "center")))
    namespaces = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"'
    document = f'<?xml version="1.0" encoding="UTF-8"?><w:document {namespaces}><w:body>' + "".join(body)
    document += '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="850" w:bottom="1134" w:left="1701"/></w:sectPr></w:body></w:document>'
    styles = '''<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/><w:sz w:val="24"/><w:lang w:val="ru-RU"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="360" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>'''
    for name, size in (("Normal", 24), ("Title", 36), ("Heading1", 30), ("Heading2", 26), ("Code", 18), ("TableText", 18), ("Caption", 20)):
        ppr = '<w:spacing w:after="100" w:line="240" w:lineRule="auto"/>' if name in ("Code", "TableText", "Caption") else '<w:spacing w:before="180" w:after="120"/>'
        if name.startswith("Heading"):
            ppr += '<w:keepNext/>'
        styles += f'<w:style w:type="paragraph" w:styleId="{name}"><w:name w:val="{name}"/><w:pPr>{ppr}</w:pPr><w:rPr><w:sz w:val="{size}"/>' + ('<w:b/>' if name in ("Title", "Heading1", "Heading2") else "") + '</w:rPr></w:style>'
    styles += '</w:styles>'
    content_types = '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="doc" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        z.writestr("word/document.xml", document)
        z.writestr("word/styles.xml", styles)
        z.writestr("word/_rels/document.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + "".join(relationships) + '</Relationships>')
        for path, content in media:
            z.writestr(path, content)


def main():
    r = load(RUN / "v27_n5/results.json")
    summary = load(RUN / "summary.json")
    rows = load(RUN / "v27_n5/per_seed.json")
    env = load(REPORTS / "environment.json")
    reg = load(REPORTS / "registration.json")
    protocol = load(LAB / "configs/protocol.json")
    spatial = summary["series"]["5"]["spatial"]
    t = r["metrics_table"]
    date = datetime.strptime(r["date"], "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=3)))
    p = Document()
    p.p("МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ", "center")
    p.p("ФЕДЕРАЛЬНОЕ ГОСУДАРСТВЕННОЕ БЮДЖЕТНОЕ ОБРАЗОВАТЕЛЬНОЕ УЧРЕЖДЕНИЕ ВЫСШЕГО ОБРАЗОВАНИЯ", "center")
    p.p("«ДОНСКОЙ ГОСУДАРСТВЕННЫЙ ТЕХНИЧЕСКИЙ УНИВЕРСИТЕТ» (ДГТУ)", "center")
    p.p("ОТЧЁТ", "title")
    p.p("по лабораторной работе № 1\n«Подготовка рабочей среды и паспорт воспроизводимого AI-эксперимента»", "center")
    p.p("по дисциплине «Искусственный интеллект в креативных технологиях»", "center")
    p.p("Вариант 27\nЗернистая плёнка (постобработка) × шаг решётки ×2", "center")
    p.p("Выполнил: ______________________________\nГруппа: _________________________________\nПроверил: _______________________________", "blank")
    p.p("Локальные расчёты: " + date.strftime("%d.%m.%Y") + "\nЧасть Б: заполняется после самостоятельного выполнения", "center")
    p.p("2026", "center")
    p.p("", "break")
    p.p("1. Цель, постановка задачи, критерии успеха и гипотеза", "h1")
    p.p("1.1. Цель и постановка", "h2")
    p.p("Подготовить изолированную рабочую среду, зафиксировать условия эксперимента в паспорте и проверить воспроизводимость по контрольным суммам полных выходных данных. Объект — учебный генератор процедурных текстур v1.0, модель-заменитель генеративной системы. Качество реальной нейросетевой модели в работе не оценивается.")
    p.p("Вариант 27 соответствует контексту 5 и фактору 3: N=(5−1)·6+3. Текстура имитирует плёночное зерно: важны мелкий масштаб и равномерность по кадру. Исследуется удвоение шага решётки при прочих равных.")
    p.table(["Параметр", "База", "Фактор"], [["Размер, пикселей", "96×96", "96×96"], ["cell, пикселей", "2", "4"], ["Число октав", "2", "2"], ["persistence", "0,70", "0,70"], ["Квантование", "8 бит", "8 бит"], ["Интерполяция", "smooth", "smooth"], ["Seed / n", "101–105 / 5", "101–105 / 5"]])
    p.p("1.2. Критерии и исходная гипотеза", "h2")
    p.p("Воспроизводимость: EQ_1_2=true, EQ_1_4=true, EQ_1_3=false, EQ_2_4=true. Для четырёх метрик используется заранее заданное учебное правило |Δ|>2·s_base, где Δ=m̄_factor−m̄_base, s — выборочное стандартное отклонение (делитель n−1). Это не формальный статистический тест и не утверждение об уровне статистической значимости.")
    p.p("Гипотеза: укрупнение зерна снижает граничную энергию, ожидается превышение порога. Контраст и энтропия предположительно снижаются; превышение порога по ним заранее не утверждалось. Средняя яркость остаётся примерно прежней, ниже порога. Возможен рост межзапускового разброса средней яркости; для остальных метрик направление изменения разброса заранее не задаётся.")
    p.p("Протокол записан " + reg["registered_moscow"] + "; локальный коммит " + PROTOCOL_COMMIT[:7] + " выполнен до новых расчётов. До очистки старые материалы были доступны: это новое выполнение с предварительной фиксацией протокола для новых запусков, а не слепая первоначальная регистрация. Порог и гипотеза после расчётов не изменялись.")
    p.p("2. Данные, происхождение, лицензии и ограничения", "h1")
    p.p("Внешний набор данных отсутствует. Изображения синтетические, порождаются локальным random.Random(seed). Скрипты lab01_generator.py и lab01_experiment.py предоставлены в материалах курса и сохранены без изменения. Происхождение кода зафиксировано; отдельная лицензия на его распространение в предоставленных материалах не указана. Отсутствие внешнего датасета не означает произвольного разрешения на распространение кода.")
    p.p("Персональные и конфиденциальные входные материалы не используются. Сторонние пакеты не установлены: requirements.txt намеренно пуст. Источники для работы — методичка lab01, скрипты курса; приложенный PDF другого студента использован только как образец формы.")
    for name, digest in reg["source_sha256"].items():
        p.p(name + " SHA-256:\n" + digest, "code")
    p.p("3. Среда, версии и параметры", "h1")
    p.table(["Параметр", "Фактическое значение"], [["ОС", env["platform"]], ["Архитектура", env["machine"]], ["Интерпретатор", "CPython " + r["env"]["python"]], ["zlib: сборка / выполнение", env["zlib_compile"] + " / " + env["zlib_runtime"]], ["Генератор", "1.0"], ["Пакеты", "Только стандартная библиотека"], ["Основной запуск, Москва", date.isoformat()], ["Среда", ".venv в корне репозитория"]])
    p.p("Структура: src/ — два исходных скрипта и средства воспроизведения; configs/ — протокол; artifacts/fresh_run/ — новые результаты; reports/ — журнал, полный паспорт, иллюстрации и отчёт. Среда .venv исключена из Git; каждый эксперимент имеет отдельную папку. Подробные сведения — reports/environment.json.")
    p.p("4. Ход работы", "h1")
    p.p("4.1. Подготовка и фиксация протокола", "h2")
    p.p("Удалены прежние результаты, журналы и промежуточные файлы внутри lab01; исходные материалы сохранены. Создана новая среда Python; выполнены pip freeze и проверка импорта. Протокол и контрольные суммы записаны в registration.json, затем создан коммит до новых запусков. Ниже команды приводятся относительно корня репозитория.")
    p.p("python -m venv .venv\n.\\.venv\\Scripts\\python.exe -m pip freeze\n.\\.venv\\Scripts\\python.exe -c \"import sys; sys.path.insert(0,'lab01/src'); import lab01_generator\"", "code")
    p.p("4.2. Намеренная ошибка и её исправление", "h2")
    p.p("Генератор дважды запущен без --seed с параметрами базы варианта 27. Он сообщил об автоматическом выборе seed по системному времени; отпечатки оказались различны. Затем два запуска с --seed 101 дали одинаковые массивы. Для каждого запуска использована отдельная папка, поэтому повторные результаты не перезаписывались.")
    ed = summary["error_demo"]
    p.table(["Запуск", "Фактический seed", "SHA-256 пикселей, начало"], [[k, str(ed[k]["seed"]), ed[k]["sha256_pixels"][:16]] for k in ("noseed_1", "noseed_2", "seed_1", "seed_2")])
    p.p("Симптом — различие полных данных при одной команде. Причина — seed берётся из времени, если аргумент пропущен. Исправление — явный --seed и локальный генератор. Точные команды, предупреждения и результаты сохранены в artifacts/fresh_run/*.log и error_demo/.")
    p.p("4.3. Основной и дополнительные запуски", "h2")
    p.p(".\\.venv\\Scripts\\python.exe lab01\\src\\lab01_experiment.py --variant 27 --seed 101 --n 5 --out lab01\\artifacts\\fresh_run\\v27_n5", "code")
    p.p("Весь набор опытов воспроизводится командой ниже, при этом выходной каталог должен быть новым. Она также выполняет n=20, n=50, демонстрационный вариант и независимый пересчёт сводки по сохранённым данным каждого seed.")
    p.p(".\\.venv\\Scripts\\python.exe lab01\\src\\run_lab01.py --out lab01\\artifacts\\repeat01", "code")
    p.p("Точные аргументы, рабочий каталог и время каждой дочерней команды записаны в artifacts/fresh_run/commands.json. Скрипты преподавателя не изменялись; дополнительный анализ вынесен в run_lab01.py.")
    p.p("5. Результаты", "h1")
    p.p("5.1. Протокол воспроизводимости", "h2")
    p.table(["Запуск", "Seed", "SHA-256 пикселей, начало", "SHA-256 PNG, начало"], [[str(i+1), str(x["seed"]), x["sha256_pixels"][:16], x["sha256_png"][:16]] for i, x in enumerate(r["runs_repro"])])
    p.p("EQ_1_2 = true\nEQ_1_4 = true\nEQ_1_3 = false\nEQ_2_4 = true", "code")
    p.p("Запуски 1, 2 и 4 при seed 101 имеют одинаковые полные массивы; запуск при seed 1101 отличается. В этой среде совпали также PNG повторных запусков. Полные 64-символьные SHA-256 хранятся в results.json и паспорте; в таблице показаны начала только для удобства чтения. Основной критерий — отпечаток пикселей, поскольку байты PNG могут зависеть от zlib.")
    p.p("5.2. Метрики основной серии n=5", "h2")
    p.p("Для каждой серии сообщаются среднее и выборочное s. Контраст внутри отдельного изображения вычисляется с делителем N по пикселям; это другая величина, чем выборочное s по пяти seed с делителем n−1.")
    p.table(["Метрика", "m̄ базы", "s базы", "m̄ фактора", "s фактора"], [[NAMES[m], *[number(t[m][k]) for k in ("mean_base", "s_base", "mean_pert", "s_pert")]] for m in NAMES])
    p.table(["Метрика", "Δ", "|Δ|/s_base", "Решение при n=5"], [[NAMES[m], number(t[m]["delta"]), number(t[m]["delta_over_s"], 2), "Обнаружено" if t[m]["significant"] else "Не обнаружено"] for m in NAMES])
    p.p("Изменение средней яркости не обнаружено: отношение равно " + number(t["mean"]["delta_over_s"],2) + ". Для контраста, граничной энергии и энтропии отношение превышает 2; все три метрики снизились. Наиболее выражено снижение граничной энергии: " + number(100*(1-t["edge"]["mean_pert"]/t["edge"]["mean_base"]),1) + "% относительно базы.")
    p.p("5.3. Сопоставление с исходной гипотезой", "h2")
    p.p("Предсказанное снижение граничной энергии с превышением порога подтвердилось. Направления изменения контраста и энтропии также совпали с ожиданием; обнаружение их изменений является результатом опыта и не выдаётся за заранее обещанный исход. Средняя яркость не превысила порог, как ожидалось.")
    p.p("5.4. Сравнение изображений и равномерности зерна", "h2")
    a, b = gen.generate(protocol["base"], 101), gen.generate(protocol["perturbed"], 101)
    side, gap, scale = 96, 12, 3
    width = side*2 + gap
    packed = b"".join(a[y*side:(y+1)*side] + bytes([255])*gap + b[y*side:(y+1)*side] for y in range(side))
    enlarged = b"".join(b"".join(bytes([v])*scale for v in packed[y*width:(y+1)*width]) * scale for y in range(side))
    expanded_width = width*scale
    height = side*scale
    figure = REPORTS / "figures/base_factor_seed101.png"
    figure.parent.mkdir(parents=True, exist_ok=True)
    # Rectangular PNG with the same standard-library encoder structure as the generator.
    import zlib
    def chunk(tag, data):
        return struct.pack(">I",len(data))+tag+data+struct.pack(">I",zlib.crc32(tag+data)&0xffffffff)
    raw = b"".join(b"\x00"+enlarged[y*expanded_width:(y+1)*expanded_width] for y in range(height))
    figure.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",expanded_width,height,8,0,0,0,0))+chunk(b"IDAT",zlib.compress(raw,9))+chunk(b"IEND",b""))
    p.image(figure, "Рисунок 1 — Слева база cell=2, справа фактор cell=4; seed 101. Оба исходных изображения 96×96, увеличены в 3 раза без интерполяции.")
    p.p("Разброс средней яркости между seed вырос с " + number(t["mean"]["s_base"]) + " до " + number(t["mean"]["s_pert"]) + " (в " + number(t["mean"]["s_pert"]/t["mean"]["s_base"],2) + " раза). Однако разброс граничной энергии уменьшился; нельзя утверждать, что фактор увеличил разброс всех метрик.")
    p.p("Для проверки равномерности внутри кадра каждый кадр разбит на 4×4 участка 24×24 пикселя. Для каждого seed вычислено выборочное s средних яркостей 16 участков; затем усреднено по seed. Нормированные значения: база " + number(spatial["base"]["mean"]) + ", фактор " + number(spatial["factor"]["mean"]) + ". Это описательная дополнительная метрика без отдельного порога существенности.")
    p.p("Укрупнение зерна сопровождается более выраженными неоднородностями средней яркости по участкам и большим разбросом общей яркости между seed. Для задачи с мелким равномерным зерном база предпочтительнее по измеренным признакам. Оценка художественного качества и восприятия плёнки требует отдельной проверки; пространственная равномерность не выводится только из межзапускового s.")
    p.p("5.5. Проверка при n=20 и n=50", "h2")
    p.table(["Метрика", "|Δ|/s, n=5", "n=20", "n=50"], [[NAMES[m], *[number(summary["series"][str(n)]["metrics"][m]["delta_over_s"],2) for n in (5,20,50)]] for m in NAMES])
    p.p("Во всех трёх сериях состав обнаруженных изменений одинаков: контраст, граничная энергия и энтропия; для средней яркости порог не превышен. Серии вложены (seed 101…105, 101…120, 101…150), поэтому это проверка устойчивости при расширении выборки, а не три независимых подтверждения.")
    p.p("Дополнительная оценка неопределённости использует общие seed как пары: d_i=m_factor,i−m_base,i, SE=s(d)/√n. Она учитывает связь базы и фактора и не заменяет учебное правило.")
    p.table(["Метрика", "Δ при n=5", "Парная SE, n=5", "Парная SE, n=50"], [[NAMES[m], number(summary["series"]["5"]["paired"][m]["mean_difference"]), number(summary["series"]["5"]["paired"][m]["se_paired"]), number(summary["series"]["50"]["paired"][m]["se_paired"])] for m in NAMES])
    p.p("Для выводов с заданным уровнем значимости потребовались бы отдельный статистический план, проверка предпосылок и учёт сравнения нескольких метрик. Само значение SE формального доказательства эффекта не даёт.")
    p.p("5.6. Воспроизведение демонстрационного варианта", "h2")
    p.p("Демонстрационный вариант 1 выполнен при n=5. Начала SHA-256 пикселей совпали с методичкой: 93fae5913d797284 (seed 101) и 79aa3ff4187bbfe8 (seed 1101); четыре равенства выполнены. Все опубликованные в методичке средние базы, s базы и средние фактора совпали до четырёх знаков после запятой.")
    p.table(["Параметр", "Методичка", "Текущая среда"], [["Python", "3.13.7", r["env"]["python"]], ["zlib", "1.3.1", env["zlib_runtime"]], ["ОС", "Windows 10", env["platform"]]])
    p.p("В методичке не приведён численный отпечаток PNG демонстрации, поэтому его межмашинное совпадение не заявляется. Проверено совпадение PNG повторных запусков внутри текущей среды. Совпадение опубликованных префиксов SHA-256 не выдаётся за сравнение отсутствующих полных эталонных хешей.")
    p.p("6. Часть Б. Рабочая область Engee", "h1")
    p.p("По решению пользователя в текущем выполнении оформлена только локальная часть. Часть Б выполняется пользователем самостоятельно; результаты входа, версии Engee, выполнения Julia и очистки рабочей области не заявляются. Отдельный файл reports/engee_checklist.md содержит порядок действий и перечень доказательств для дополнения этого раздела.")
    p.table(["Что добавить после выполнения", "Фактический результат"], [["Дата, версии кабинета и среды", "____________________"], ["VERSION и versioninfo()", "____________________"], ["Переменная seed=101, очистка, перезапуск", "____________________"], ["Файл .ngscript, паспорт и снимки", "____________________"]])
    p.p("7. Анализ ошибок, угроз валидности и ограничений", "h1")
    p.table(["Угроза", "Мера и оставшееся ограничение"], [["Не задан seed", "Ошибка воспроизведена; использован явный seed и локальный random.Random."], ["Сравнение только средних", "Воспроизводимость проверена по SHA-256 полных массивов."], ["Подгонка гипотезы", "Новый протокол закоммичен до новых запусков; доступ к старым материалам честно отмечен."], ["Неверный делитель s", "По seed используется n−1; сводка проверена по значениям отдельных запусков."], ["Малая выборка", "Основной вывод при n=5; дополнительно n=20,50. Серии вложены."], ["Смена среды и кода", "Записаны Python, zlib, ОС и SHA-256 исходных скриптов."], ["Ограниченность метрик", "Они описывают яркость и структуру, не заменяют зрительскую оценку."], ["Неправомерное обобщение", "Проверены один контекст, один фактор и одна реализация генератора; правило 2s — учебное."]])
    p.p("8. Вывод по цели", "h1")
    p.p("Цель локальной части достигнута: создана изолированная среда без сторонних пакетов, условия записаны в паспорт, воспроизводимость подтверждена четырьмя сравнениями полных выходных данных. При n=5 удвоение cell с 2 до 4 существенно по учебному правилу снижает контраст, граничную энергию и энтропию; изменение средней яркости не обнаружено. Снижение граничной энергии с превышением порога соответствует исходной гипотезе.")
    p.p("Межзапусковый разброс средней яркости вырос, а неоднородность средних яркостей участков увеличилась в описательной проверке. Для мелкого равномерного зерна предпочтительнее базовый шаг. Расширенные серии сохранили решения по четырём метрикам. Выводы не доказывают отсутствие слабого эффекта по яркости, художественное превосходство изображения или переносимость результата на реальные нейросети. Часть Б остаётся для самостоятельного дополнения.")
    p.p("9. Артефакты, паспорт и ссылки", "h1")
    p.p("Репозиторий: https://github.com/BookWormDevid/Creative_AI_things, каталог lab01/. Коммит предварительного протокола: " + PROTOCOL_COMMIT + ". Новые коммиты созданы локально; публикация на GitHub в эту работу не входит.")
    p.table(["Путь относительно lab01", "Назначение"], [["reports/report.docx, report.pdf, report.md", "Редактируемый отчёт, PDF и исходник"], ["reports/passport.md", "Полный паспорт"], ["reports/journal.md, registration.json", "Порядок выполнения и регистрация"], ["configs/protocol.json", "Параметры и гипотеза"], ["artifacts/fresh_run/v27_n5/", "Основной результат и данные каждого seed"], ["artifacts/fresh_run/v27_n20/, v27_n50/", "Расширенные серии"], ["artifacts/fresh_run/demo_v01/, error_demo/", "Демонстрация и намеренная ошибка"], ["artifacts/fresh_run/commands.json, *.log", "Точные команды, время, вывод"], ["reports/engee_checklist.md", "Чек-лист самостоятельной части Б"], ["reports/validation.json, manifest.json", "Проверки и контрольные суммы файлов"], ["dist/lab01_variant27_local.zip", "Архив локальной части без окружения и Git"]])
    p.p("Приложение А. Ответы на контрольные вопросы", "h1")
    answers = [
        ("1. Почему одного запуска недостаточно?", "Один seed не показывает разброс. Нужны число и список seed, среднее и выборочное s, фиксированные параметры и критерий. Здесь используются n=5 и дополнительные n=20,50."),
        ("2. Среднее и выборочное s для 0,71; 0,74; 0,69; 0,73; 0,70", "Среднее 0,714; сумма квадратов отклонений 0,001720; s=√(0,001720/4)=0,020736; 2s=0,041473. Для среднего второй серии 0,770: Δ=0,056>2s — изменение обнаружено по учебному правилу. Нужны оговорки о n=5, неопределённости s и отсутствии формального уровня значимости."),
        ("3. Почему сравнивается полный массив?", "Среднее теряет информацию: массивы (0,255) и (127,128) имеют среднее 127,5, но разные пиксели. SHA-256 вычисляется по всем байтам массива и позволяет практически надёжно проверить их совпадение."),
        ("4. Почему могут различаться PNG?", "PNG содержит сжатые данные; разные версии zlib могут выдавать разные байты при тех же пикселях. В паспорт записываются версия zlib и отдельно SHA-256 пикселей и PNG. Главная проверка — массив."),
        ("5. Что означает s=0?", "Все значения метрики в серии совпали. Проверяют изменение seed, число запусков, отпечатки и агрегацию. Разные изображения могут иметь одну метрику, поэтому s=0 не всегда ошибка. При n=1 выборочное s не определено, а не равно нулю."),
        ("6. Как найти причину невоспроизводимости?", "Сравнить полные хеши, прочитать предупреждения, проверить фактические seed, версии и параметры. В намеренном опыте причина найдена в выборе seed по времени; явный --seed 101 восстановил совпадение."),
        ("7. Почему локальный random.Random(seed)?", "Экземпляр изолирует состояние от чужих вызовов глобального random. Если несколько потоков делят один генератор, порядок получения чисел может различаться. Локальные генераторы и явно определённый порядок работы уменьшают скрытые зависимости."),
        ("8. Какие поля обязательны в паспорте?", "Цель и критерий; происхождение и ограничения данных; модель и версия кода; параметры и seed; среда; точная процедура; результаты; ограничения и вывод. Потеря seed или версии кода особенно затрудняет повтор; для real-world модели нужны также неизменяемая ревизия весов и устройство."),
        ("9. Зачем точные версии зависимостей?", "Диапазон версий допускает обновление среды без изменения файла требований. Точные версии фиксируют установленные пакеты. Здесь файл пуст, поскольку пакеты не используются, но версию самого Python всё равно нужно записать отдельно."),
        ("10. Что добавить для модели «текст → изображение»?", "Идентификатор модели и полную ревизию весов, точные prompt и negative prompt, seed и устройство генератора, размер, число шагов, guidance scale, scheduler и его настройки, device, dtype, версии библиотек и драйверов, число потоков и настройки детерминизма, состав конвейера. Это план будущего паспорта, а не утверждение о запуске такой модели в ЛР 1.")
    ]
    for question, answer in answers:
        p.p(question, "h2")
        p.p(answer)
    p.save(REPORTS / "report")
    passport = Document()
    passport.p("Паспорт эксперимента ЛР 1 — вариант 27", "h1")
    passport.p("Исполнитель: ____________________. Дата локального запуска: " + date.isoformat())
    passport.table(["Раздел", "Сведения"], [
        ["Цель и критерий", "Воспроизводимость процедурного генератора и влияние cell:2→4. Критерий |Δ|>2s_base при n=5 задан до новых запусков."],
        ["Данные", "Синтетические изображения, внешнего датасета нет. Код — материалы курса; отдельная лицензия не указана."],
        ["Модель", "lab01_generator.py v1.0; контрольные суммы ниже."],
        ["Параметры", json.dumps(protocol["base"],ensure_ascii=False)+"; фактор: cell=4; seed 101–105, n=5; воспроизводимость 101,101,1101,101."],
        ["Среда", "CPython "+r["env"]["python"]+"; "+env["platform"]+"; "+env["machine"]+"; zlib "+env["zlib_runtime"]+"; сторонних пакетов нет."],
        ["Процедура", "Из корня: .venv/Scripts/python.exe lab01/src/lab01_experiment.py --variant 27 --seed 101 --n 5 --out lab01/artifacts/fresh_run/v27_n5"],
        ["Результаты", "EQ: true,true,false,true. Контраст, граничная энергия, энтропия снизились с превышением 2s; изменение яркости не обнаружено при n=5."],
        ["Ограничения", "Один контекст и фактор; учебный критерий, ограниченность метрик, вложенные дополнительные серии. Старые результаты были доступны до очистки. Engee не выполнена."]])
    passport.p("Исходная гипотеза", "h2")
    for value in protocol["hypothesis"].values():
        passport.p(value)
    passport.p("Протокол: коммит "+PROTOCOL_COMMIT+"; регистрация "+reg["registered_moscow"]+"; SHA-256 протокола: "+reg["protocol_sha256"])
    for name,digest in reg["source_sha256"].items():
        passport.p(name+": "+digest, "code")
    passport.p("Контрольные суммы полных массивов и PNG", "h2")
    for i,x in enumerate(r["runs_repro"],1):
        passport.p(f"Запуск {i}, seed={x['seed']}\npixels: {x['sha256_pixels']}\nPNG: {x['sha256_png']}","code")
    passport.table(["Метрика", "База ± s", "Фактор ± s", "Δ", "|Δ|/s"], [[NAMES[m], number(t[m]["mean_base"])+" ± "+number(t[m]["s_base"]), number(t[m]["mean_pert"])+" ± "+number(t[m]["s_pert"]), number(t[m]["delta"]), number(t[m]["delta_over_s"],2)] for m in NAMES])
    passport.p("Вывод: укрупнение зерна подтвердилось по снижению граничной энергии; межзапусковый разброс яркости вырос. По дополнительной описательной проверке участков неоднородность яркости увеличилась. Для мелкого равномерного зерна база предпочтительнее по исследованным признакам. Данные и команды: ../artifacts/fresh_run/; анализ и ограничения: report.md; Engee: engee_checklist.md.")
    # The complete passport is plain Markdown; no redundant DOCX/PDF copy is needed.
    lines=[]
    for kind,data in passport.blocks:
        if kind=="table":
            lines.append("| "+" | ".join(str(c).replace("|","∣") for c in data[0])+" |\n|"+" --- |"*len(data[0]))
            lines.extend("| "+" | ".join(str(c).replace("|","∣") for c in row)+" |" for row in data[1:])
        else:
            lines.append(({"h1":"# ","h2":"## "}.get(kind,""))+data)
        lines.append("")
    (REPORTS/"passport.md").write_text("\n".join(lines),encoding="utf-8")
    print("Built report.md, report.html, report.docx, passport.md and figure.")


if __name__ == "__main__":
    main()
