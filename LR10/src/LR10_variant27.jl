# ЛР №10, вариант 27. Котов Дэвид Арсенович.

# %% Шаг 3 плана. Среда: дата, версии, файлы работы и их SHA-256; пакеты указаний
using Dates, SHA
W = "/user/Котов_Дэвид_Арсенович/LR10"
PY = "/user/.user_venvs/py3.11/bin/python3"
ENGEE_VERSION = ""  # Вписать текущую версию из заголовка Engee.
println("Дата и время (UTC): ", now(UTC))
println("Julia VERSION = ", VERSION, ";  ядер: ", Sys.CPU_THREADS, ";  ОЗУ: ", round(Sys.total_memory() / 2^30; digits = 1), " ГБ")
# Учебная библиотека приложения А; проверка целостности файлов.
for (f, ref) in (("lab10_lib.py", "b53293eb"), ("lr10_variant27.py", ""))
    isfile(joinpath(W,f)) || error("В папке LR10 отсутствует " * f * "; загрузите все файлы из архива.")
    h = bytes2hex(open(sha256, joinpath(W, f)))
    println(rpad(f, 18), filesize(joinpath(W, f)), " байт, SHA-256 ", h, isempty(ref) ? "" : "; SHA-256 проверен: $(startswith(h, ref))")
end
# Раздел 4 указаний: diffusers 0.32.2 и transformers < 5, PyTorch не трогать (ставится только если его нет).
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

# %% Шаг 4 плана. variant_summary(27, save_dir="v27") и blind_sheets(27, "v27"). Запуск блокирующий
# (фоновый запуск из ячейки подвешивает ячейку). Если results_v27.json уже есть, повторно не запускается.
cmd = addenv(Cmd(`$PY -u $(joinpath(W, "lr10_variant27.py"))`; dir = W), "LR10_ENGEE_VERSION"=>ENGEE_VERSION, "LR10_JULIA_VERSION"=>string(VERSION))
if isfile(joinpath(W, "results_v27.json"))
    println("результат уже есть: results_v27.json от ", Dates.unix2datetime(mtime(joinpath(W, "results_v27.json"))), " UTC — повторно не запускаю")
else
    t0 = time(); run(pipeline(cmd; stdin = devnull, stdout = joinpath(W, "out_v27.txt"), stderr = joinpath(W, "err_v27.txt")))
    println("вариант 27 выполнен за ", round((time() - t0) / 60; digits = 1), " мин; stderr: ", filesize(joinpath(W, "err_v27.txt")), " байт")
end

# %% Вывод скрипта варианта целиком (ключ слепого сравнения в нём не печатается)
print(read(joinpath(W, "out_v27.txt"), String))

# %% Шаг 5 плана. Пять листов слепого сравнения (seed 101…105 сверху вниз), без подписей моделей
using Images
vcat((load(joinpath(W, "v27", "blind_$s.png")) for s in 101:105)...)
