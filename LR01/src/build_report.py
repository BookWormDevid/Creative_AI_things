"""Build the local lab report, passport and illustrations without third-party packages."""
from __future__ import annotations

import json
import struct
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape

LAB = Path(__file__).resolve().parents[1]
REPORTS = LAB / "reports"
RUN = LAB / "artifacts/fresh_run"
PROTOCOL_COMMIT = "e73126aca3128e50746329a8fb4db4f81ddeaba3"
NAMES = {"mean": "Средняя яркость", "contrast": "Контраст", "edge": "Граничная энергия", "entropy": "Энтропия, бит"}
REPORT_NAME = "Котов_Дэвид_Арсенович_Вариант_27_ЛР_1"


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
                    cell_text = paragraph(str(cell), "TableText", small=True)
                    if i < len(data) - 1:
                        cell_text = cell_text.replace('<w:pPr>', '<w:pPr><w:keepNext/>', 1)
                    tbl += f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>' + ('<w:shd w:fill="EEEEEE"/>' if i == 0 else "") + '</w:tcPr>' + cell_text + '</w:tc>'
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
            body.append(f'''<w:p><w:pPr><w:keepNext/><w:jc w:val="center"/></w:pPr><w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{idx}" name="Figure {idx}"/><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="0" name="image{idx}.png"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>''')
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
    env = load(REPORTS / "environment.json")
    reg = load(REPORTS / "registration.json")
    engee = load(REPORTS / "engee/evidence.json")
    t = r["metrics_table"]
    date = datetime.strptime(r["date"], "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=3)))
    p = Document()
    p.p("МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ", "center")
    p.p("ФЕДЕРАЛЬНОЕ ГОСУДАРСТВЕННОЕ БЮДЖЕТНОЕ ОБРАЗОВАТЕЛЬНОЕ УЧРЕЖДЕНИЕ ВЫСШЕГО ОБРАЗОВАНИЯ", "center")
    p.p("«ДОНСКОЙ ГОСУДАРСТВЕННЫЙ ТЕХНИЧЕСКИЙ УНИВЕРСИТЕТ» (ДГТУ)", "center")
    p.p("ОТЧЁТ", "title")
    p.p("по лабораторной работе № 1\n«Подготовка рабочей среды и паспорт воспроизводимого AI-эксперимента»", "center")
    p.p("по дисциплине «Искусственный интеллект в креативных технологиях»", "center")
    p.p("Вариант 27\nЗернистая плёнка: шаг решётки 2 → 4 пикселя", "center")
    p.p("Выполнил: Котов Дэвид Арсенович\nГруппа: _________________________________\nПроверил: _______________________________", "blank")
    p.p("Дата расчётов: " + date.strftime("%d.%m.%Y") + "\n2026", "center")
    p.p("", "break")
    p.p("1. Цель, задача и гипотеза", "h1")
    p.p("Цель — подготовить среду Python, составить паспорт эксперимента и проверить, повторяется ли результат при одном seed. В варианте 27 нужно выяснить, как удвоение шага решётки меняет плёночное зерно.")
    p.table(["Параметр", "База", "Фактор"], [["Размер", "96×96", "96×96"], ["cell", "2", "4"], ["Октавы / persistence", "2 / 0,70", "2 / 0,70"], ["Квантование / интерполяция", "8 бит / smooth", "8 бит / smooth"], ["Seed / число запусков", "101–105 / 5", "101–105 / 5"]])
    p.p("До новых запусков записана гипотеза: зерно станет крупнее, а граничная энергия снизится с превышением порога. Контраст и энтропия, предположительно, тоже снизятся; средняя яркость заметно не изменится. Возможно увеличение разброса яркости между seed.")
    p.p("Критерий для каждой метрики: |Δ| > 2s_base, где Δ — разность средних фактора и базы, s_base — выборочное стандартное отклонение с делителем n−1. Это учебное правило. Протокол зафиксирован коммитом e73126a до новых расчётов. Работа выполнялась повторно; прежние результаты были доступны до очистки.")
    p.p("2. Данные и происхождение кода", "h1")
    p.p("Внешних данных нет: изображения создаёт процедурный генератор v1.0. Два исходных скрипта получены с заданием и не изменялись. Их SHA-256 приведены в паспорте. Отдельная лицензия на код в материалах не указана.")
    p.p("3. Среда и параметры", "h1")
    p.table(["Компонент", "Версия или значение"], [["ОС / архитектура", env["platform"] + " / " + env["machine"]], ["Python / zlib", r["env"]["python"] + " / " + env["zlib_runtime"]], ["Сторонние пакеты", "Нет; requirements.txt пуст"], ["Время основного запуска, Москва", date.strftime("%d.%m.%Y %H:%M:%S")], ["Среда", ".venv в корне репозитория"]])
    p.p("4. Ход работы", "h1")
    p.p("Создана виртуальная среда, проверен импорт генератора. Два запуска без seed дали разные изображения и предупреждение. Причина — автоматический выбор seed по времени. После явного --seed 101 отпечатки совпали.")
    ed = summary["error_demo"]
    p.table(["Запуск", "Seed", "SHA-256 пикселей, начало"], [[k, str(ed[k]["seed"]), ed[k]["sha256_pixels"][:16]] for k in ("noseed_1", "noseed_2", "seed_1", "seed_2")])
    p.p("Основной опыт выполнен из корня репозитория:")
    p.p(".\\.venv\\Scripts\\python.exe LR01\\src\\lab01_experiment.py --variant 27 --seed 101 --n 5 --out LR01\\artifacts\\fresh_run\\v27_n5", "code")
    p.p("Затем выполнены серии n=20 и n=50, демонстрационный вариант 1 и проверка равномерности по участкам. Команды и вывод сохранены в artifacts/fresh_run/commands.json и логах.")
    p.p("5. Результаты", "h1")
    p.p("5.1. Воспроизводимость", "h2")
    p.table(["Запуск", "Seed", "SHA-256 пикселей, начало", "SHA-256 PNG, начало"], [[str(i+1), str(x["seed"]), x["sha256_pixels"][:16], x["sha256_png"][:16]] for i,x in enumerate(r["runs_repro"])])
    p.p("EQ_1_2 = true; EQ_1_4 = true; EQ_1_3 = false; EQ_2_4 = true. Протокол выполнен. Сравнивались полные отпечатки массивов; таблица показывает первые 16 символов. PNG повторных запусков в этой среде также совпали.")
    p.p("5.2. Метрики при n=5", "h2")
    p.table(["Метрика", "Среднее базы", "s базы", "Среднее фактора", "s фактора"], [[NAMES[m], *[number(t[m][k]) for k in ("mean_base", "s_base", "mean_pert", "s_pert")]] for m in NAMES])
    p.table(["Метрика", "Δ", "|Δ|/s_base", "Эффект при n=5"], [[NAMES[m], number(t[m]["delta"]), number(t[m]["delta_over_s"],2), "Обнаружен" if t[m]["significant"] else "Не обнаружен"] for m in NAMES])
    p.p("Контраст, граничная энергия и энтропия снизились с превышением порога. Изменение средней яркости не обнаружено. Граничная энергия уменьшилась на " + number(100*(1-t["edge"]["mean_pert"]/t["edge"]["mean_base"]),1) + "%. Это подтверждает основное предсказание об укрупнении зерна.")
    p.p("5.3. Изображения и равномерность зерна", "h2")
    p.image(REPORTS / "figures/base_factor_seed101.png", "Рисунок 1 — База cell=2 слева, фактор cell=4 справа. Seed 101, размер 96×96; увеличение без интерполяции.")
    spatial = summary["series"]["5"]["spatial"]
    p.p("Разброс средней яркости между seed вырос: " + number(t["mean"]["s_base"]) + " → " + number(t["mean"]["s_pert"]) + ". У граничной энергии разброс, напротив, уменьшился.")
    p.p("Каждый кадр разбит на 16 участков 24×24. Среднее по seed стандартное отклонение яркости участков выросло: " + number(spatial["base"]["mean"]) + " → " + number(spatial["factor"]["mean"]) + ". Неоднородность внутри кадра стала выраженнее. Это дополнительное описательное измерение без отдельного порога.")
    p.p("5.4. Дополнительные проверки", "h2")
    p.table(["Метрика", "|Δ|/s, n=5", "n=20", "n=50"], [[NAMES[m], *[number(summary["series"][str(n)]["metrics"][m]["delta_over_s"],2) for n in (5,20,50)]] for m in NAMES])
    p.p("При расширении серии вывод по каждой метрике сохранился. Серии вложены: они начинаются с seed 101 и не являются независимыми опытами.")
    p.p("Для оценки неопределённости рассчитана парная ошибка SE=s(d)/√n, где d — разность метрик при общем seed. Она дополняет основной критерий:")
    p.table(["Метрика", "SE, n=5", "SE, n=50"], [[NAMES[m], number(summary["series"]["5"]["paired"][m]["se_paired"]), number(summary["series"]["50"]["paired"][m]["se_paired"])] for m in NAMES])
    p.p("Вариант 1 воспроизвёл опубликованные начала отпечатков и значения метрик до четырёх знаков. В методичке Python 3.13.7 и zlib 1.3.1; здесь — " + r["env"]["python"] + " и " + env["zlib_runtime"] + ". Полный эталонный отпечаток PNG не опубликован, поэтому межмашинное совпадение файла не проверялось.")
    p.p("6. Часть Б. Engee", "h1")
    p.p("6.1. Среда и файлы", "h2")
    p.p("Часть Б выполнена 20.10.2026 в 20:19 (Москва). В папке курса создан каталог LR01, сохранён скрипт LR01_environment.ngscript и вывод versioninfo.txt. В LR01 загружен паспорт локального эксперимента в PDF.")
    p.table(["Компонент", "Фактическое значение"], [["Личный кабинет", engee["account_version"]], ["Рабочая среда", engee["workspace_version"]], ["Julia — вывод VERSION", engee["runtime_version"]], ["Платформа", "Linux, x86_64-linux-gnu, 64 бит"], ["Процессор", "112 × Intel Xeon Platinum 8180, 2.50 GHz"], ["Потоки", "5 default, 3 interactive, 5 GC; JULIA_NUM_THREADS=7,1"]])
    p.p("Версии отличаются от методички: там кабинет 26.9.1 и среда 26.8.2-H3. Интерфейс англоязычный: File Browser, Script Editor, Variables → Workspace. В метаданных .ngscript указана Julia 1.9.3, но фактически команда VERSION вернула 1.12.4; в отчёт внесён результат выполнения.")
    p.p('println("VERSION = ", VERSION)\nversioninfo()\n\nseed = 101', "code")
    p.p("Полный вывод первой ячейки сохранён без изменений в reports/engee/versioninfo.txt. Локальная часть выполнялась на Python в Windows, часть Б — на Julia в Linux; сведения об этих средах записаны отдельно.")
    p.image(REPORTS / "engee/Engee_screenshots_pt1.png", "Рисунок 2 — Вывод VERSION и versioninfo(), файлы рабочего каталога LR01.")
    p.p("6.2. Состояние рабочей области", "h2")
    p.table(["Действие", "Переменные", "Сохранённый вывод ячейки"], [["Выполнено seed = 101", "seed = 101, Int64", "101"], ["Очистка переменных", "Таблица пуста", "101 остаётся"], ["Перезапуск ядра", "Таблица пуста", "101 остаётся"]])
    p.p("После очистки и перезапуска переменная исчезла из рабочей области, хотя вывод 101 сохранился под ячейкой. Сохранённый вывод отражает прошлый запуск, а не текущее состояние ядра. Поэтому для повторения работы нужно фиксировать порядок выполнения ячеек и исходное состояние среды.")
    p.image(REPORTS / "engee/Engeept2.png", "Рисунок 3 — После seed = 101 в таблице есть переменная seed типа Int64.")
    p.image(REPORTS / "engee/Engeept3.png", "Рисунок 4 — После очистки таблица переменных пуста, вывод ячейки сохранён.")
    p.image(REPORTS / "engee/Engeept4.png", "Рисунок 5 — После перезапуска таблица остаётся пустой, вывод 101 виден в редакторе.")
    p.p("7. Ошибки и ограничения", "h1")
    p.p("Ошибка без seed устранена явным значением 101. Воспроизводимость проверена по полным массивам, а не по средним. Выборочное s рассчитано с делителем n−1; порог после запуска не менялся.")
    p.p("Основной вывод ограничен n=5, одной текстурой и одним фактором. Правило 2s не является статистическим тестом. Метрики описывают яркость и структуру зерна, но не художественное качество. Отсутствие обнаруженного изменения яркости не доказывает отсутствия слабого эффекта.")
    p.p("8. Вывод", "h1")
    p.p("Работа выполнена: среда подготовлена, паспорт составлен, воспроизводимость подтверждена. Удвоение cell укрупнило зерно, снизило контраст, граничную энергию и энтропию. Средняя яркость не превысила порог, но её разброс между seed вырос. Для мелкого равномерного зерна базовый шаг подходит лучше по измеренным признакам. В Engee проверены версии и состояние рабочей области: после очистки и перезапуска сохранённый вывод не подтверждает наличие переменной.")
    p.p("9. Файлы работы", "h1")
    p.p("Репозиторий: https://github.com/BookWormDevid/Creative_AI_things, каталог LR01/.")
    p.table(["Путь относительно LR01", "Содержимое"], [[REPORT_NAME + ".docx", "Отчёт с частями А и Б; PDF экспортируется отдельно"], ["reports/passport.pdf", "Паспорт локального эксперимента"], ["reports/engee/", "Скрипт, полный вывод Julia, снимки и сведения о среде"], ["reports/journal.md, registration.json", "Журнал и регистрация протокола"], ["artifacts/fresh_run/", "Результаты, изображения, команды и логи"], ["reports/validation.json", "Результаты самопроверки"], ["dist/LR01_Вариант_27.zip", "Архив работы с частями А и Б"]])
    p.p("Приложение А. Контрольные вопросы", "h1")
    answers = [
        ("1. Зачем несколько запусков?", "Один seed не показывает разброс. Нужны список seed, среднее, выборочное s и заранее заданный критерий."),
        ("2. Расчёт по пяти значениям", "Для 0,71; 0,74; 0,69; 0,73; 0,70: среднее 0,714; s=0,020736; 2s=0,041473. Разность со средним 0,770 равна 0,056 и превышает порог. Вывод действует в рамках учебного правила при n=5."),
        ("3. Почему полный массив?", "Массивы (0,255) и (127,128) имеют одно среднее 127,5, но разные пиксели. Отпечаток учитывает все байты."),
        ("4. Почему могут различаться PNG?", "Разная версия сжатия может изменить байты файла при тех же пикселях. Поэтому отдельно записываются zlib, отпечаток массива и отпечаток PNG."),
        ("5. Что означает s=0?", "Метрика совпала во всех запусках. Нужно проверить seed, отпечатки и агрегацию. Это не обязательно ошибка; при n=1 выборочное s не определено."),
        ("6. Как найти невоспроизводимость?", "Проверить предупреждения, фактические seed, параметры, версии и отпечатки. В опыте причиной стал выбор seed по времени."),
        ("7. Зачем random.Random(seed)?", "Локальный экземпляр защищает последовательность от посторонних вызовов глобального генератора. Общий генератор в потоках зависит от порядка обращений."),
        ("8. Что хранится в паспорте?", "Цель и критерий, данные, код и версия, параметры и seed, среда, точная команда, результаты и ограничения. Без этих сведений повторить опыт трудно."),
        ("9. Зачем точные версии?", "Диапазон допускает обновление зависимостей без изменения файла. Здесь сторонних пакетов нет, но версия Python записана отдельно."),
        ("10. Что добавить для «текст → изображение»?", "Ревизию весов, точный запрос, seed, размер, шаги, guidance scale, scheduler, устройство, dtype, версии библиотек и настройки детерминизма.")]
    for question, answer in answers:
        p.p(question + " " + answer)
    p.p("Приложение Б. Самопроверка", "h1")
    p.table(["Требование", "Проверка"], [["Вариант и единственный фактор", "27; меняется только cell: 2→4"], ["Гипотеза и порог до новых запусков", "Протокол и исходная запись сверены с e73126a"], ["Полный протокол seed", "101,101,1101,101; четыре сравнения выполнены"], ["Четыре метрики и выборочное s", "Пересчитаны по данным каждого seed"], ["Вывод по каждой метрике", "Совпадает с правилом |Δ|>2s_base"], ["Изображения и равномерность", "Один seed, один масштаб; проверка 16 участков"], ["Среда, код, команды, паспорт", "Версии, SHA-256 и файлы приложены"], ["Дополнительные серии и демо", "n=20,50 и вариант 1 проверены"], ["Часть Б", "Скрипт, вывод Julia и четыре снимка приложены"], ["Оформление", "Отчёт DOCX, паспорт PDF; осталось указать группу и проверяющего"]])
    p.save(LAB / REPORT_NAME)
    print("Built the named DOCX report; no PDF exported.")


if __name__ == "__main__":
    main()
