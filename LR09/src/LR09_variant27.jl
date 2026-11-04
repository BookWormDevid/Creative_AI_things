# ЛР №9, вариант 27. Котов Дэвид Арсенович.

# %% Шаг 3 плана. Среда: дата, версии, файлы работы и их SHA-256; пакеты указаний
using Dates, SHA
W = "/user/Котов_Дэвид_Арсенович/LR09"
PY = "/user/.user_venvs/py3.11/bin/python3"
ENGEE_VERSION = ""  # Вписать текущую версию из заголовка Engee.
println("Дата и время (UTC): ", now(UTC))
println("Julia VERSION = ", VERSION, ";  ядер: ", Sys.CPU_THREADS, ";  ОЗУ: ", round(Sys.total_memory() / 2^30; digits = 1), " ГБ")
for (f, ref) in (("lab09_lib.py", "cc4d233d"), ("lab09_llm.py", "5eabb31f"), ("run_lr09.py", "a962a37b"), ("lr09_variant27.py", ""))
    isfile(joinpath(W,f)) || error("В папке LR09 отсутствует " * f * "; загрузите все файлы из архива.")
    h = bytes2hex(open(sha256, joinpath(W, f)))
    println(rpad(f, 18), filesize(joinpath(W, f)), " байт, SHA-256 ", h, isempty(ref) ? "" : "; совпадает с архивом работы: $(startswith(h, ref))")
end
# Раздел 4 указаний: diffusers 0.32.2 и transformers < 5, PyTorch не обновлять. Если torch в окружении нет
# (так было в ЛР 8), ставится версия указаний — 2.4.1 для процессора. Вывод pip — в pip_install.log.
has(m) = success(ignorestatus(`$PY -c "import $m"`))
PIPLOG = joinpath(W, "pip_install.log")
pipi(args...) = run(pipeline(`$PY -m pip install --progress-bar off $args`; stdin = devnull, stdout = PIPLOG, stderr = PIPLOG, append = true))
has("torch") || (println("ставлю torch 2.4.1 (CPU)"); pipi("torch==2.4.1", "--index-url", "https://download.pytorch.org/whl/cpu"))
has("scipy") || (println("ставлю scipy"); pipi("scipy"))
ver = read(ignorestatus(`$PY -c "import diffusers, transformers; print(diffusers.__version__, transformers.__version__)"`), String)
# Команда указаний ("transformers<5") не обновляет уже стоящую версию 4.x (в окружении была 4.48.3), поэтому
# ставится проверенная указаниями 4.57.6.
startswith(ver, "0.32.2 4.57.") || (println("ставлю diffusers==0.32.2, transformers==4.57.6"); pipi("diffusers==0.32.2", "transformers==4.57.6"))
run(`$PY -c "import sys, torch, diffusers, transformers, scipy, numpy; print('python', sys.version.split()[0], '| torch', torch.__version__, '| diffusers', diffusers.__version__, '| transformers', transformers.__version__, '| scipy', scipy.__version__, '| numpy', numpy.__version__, '| cuda', torch.cuda.is_available())"`)

# %% Шаги 4–6 плана. Вариант 27: серия A и B на seed 101…105, сводка, проверки. Запуск блокирующий
# (фоновый запуск из ячейки подвешивает ячейку). Если results_v27.json уже есть, повторно не запускается.
cmd = addenv(Cmd(`$PY -u $(joinpath(W, "lr09_variant27.py"))`; dir = W), "LR09_ENGEE_VERSION"=>ENGEE_VERSION, "LR09_JULIA_VERSION"=>string(VERSION))
if isfile(joinpath(W, "results_v27.json"))
    println("результат уже есть: results_v27.json от ", Dates.unix2datetime(mtime(joinpath(W, "results_v27.json"))), " UTC — повторно не запускаю")
else
    t0 = time(); run(pipeline(cmd; stdin = devnull, stdout = joinpath(W, "out_v27.txt"), stderr = joinpath(W, "err_v27.txt")))
    println("вариант 27 выполнен за ", round((time() - t0) / 60; digits = 1), " мин; stderr: ", filesize(joinpath(W, "err_v27.txt")), " байт")
end

# %% Вывод скрипта варианта целиком
print(read(joinpath(W, "out_v27.txt"), String))

# %% Шаг 5 плана. Лист сравнения seed 101: слева A, справа B
using Images
hcat(load(joinpath(W, "v27", "A_s101.png")), load(joinpath(W, "v27", "B_s101.png")))

# %% Шаг 7 плана. Запросы части 2 для новых чатов языковой модели (контекст 5)
for a in ("zero", "few", "step")
    println("=== ", a, " ===")
    run(Cmd(`$PY $(joinpath(W, "lab09_llm.py")) prompt $a 5`; dir = W))
end
