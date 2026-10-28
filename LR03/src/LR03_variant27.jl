# ЛР №3, вариант 27. Котов Дэвид Арсенович.
# Сцена 5 «шахматная структура» (lo 0,15, hi 0,85, шум 0,02, checker 8) × воздействие 3 «уменьшение в 4 раза и возврат».
# Скрипт для Engee. Одна ячейка — один шаг плана методических указаний (раздел 5).
# Шаг 2 (гипотеза и допуск до запуска) выполнен в журнале LR03/reports/journal.md.

# %% Шаг 1. Подготовка среды: дата, версия Julia, рабочая папка, учебная библиотека
using Dates, SHA
println("Дата и время (UTC): ", now(UTC))
println("VERSION = ", VERSION)
cd("/user/Котов_Дэвид_Арсенович/LR03")
println("Рабочая папка: LR03")
lib = "lab03_lib.jl"
println("lab03_lib.jl: ", filesize(lib), " байт, SHA-256 = ", bytes2hex(open(sha256, lib)))
println("совпадает с методичкой (cd1622643e7cfe7c…): ", startswith(bytes2hex(open(sha256, lib)), "cd1622643e7cfe7c"))
include(lib)
make_scene(101) |> describe_image

# %% Шаг 3. Сцена варианта и её свойства: размер, тип, диапазон, объём в байтах
cd("/user/Котов_Дэвид_Арсенович/LR03")
VARIANT = 27
SCENE, FACTOR = divrem(VARIANT - 1, 6) .+ 1
P = scene_preset(SCENE)
img = make_scene(101; P...)
d = describe_image(img)
println("вариант ", VARIANT, ": сцена ", SCENE, ", воздействие ", FACTOR)
println("параметры сцены: ", P)
println("size = ", d.size, ", eltype = ", d.eltype)
println("min = ", d.min, ", max = ", d.max)
println("bytes = ", d.bytes, "  (ожидалось 128·128·3·8 = ", 128 * 128 * 3 * 8, ")")

# %% Шаг 4. Яркость двумя способами и максимум модуля разности
cd("/user/Котов_Дэвид_Арсенович/LR03")
y_manual = luma_manual(img)
y_gray = luma_images(img)
println("максимум модуля разности = ", maximum(abs.(y_manual .- y_gray)))
println("сравнение с допуском isapprox: ", isapprox(y_manual, y_gray))
println("SHA вручную: ", array_sha(y_manual)[1:16])
println("SHA Gray:    ", array_sha(y_gray)[1:16])
println("контрольные суммы равны: ", array_sha(y_manual) == array_sha(y_gray))

# %% Шаг 5. Контрольная сумма яркости при seed 101 — дважды
cd("/user/Котов_Дэвид_Арсенович/LR03")
sha_1 = array_sha(luma_images(make_scene(101; P...)))
sha_2 = array_sha(luma_images(make_scene(101; P...)))
sha_ctrl = array_sha(luma_images(make_scene(102; P...)))
println("seed 101, построение 1: ", sha_1)
println("seed 101, построение 2: ", sha_2)
println("совпадение: ", sha_1 == sha_2)
println("контроль, seed 102:     ", sha_ctrl[1:16], "  (отличается: ", sha_ctrl != sha_1, ")")

# %% Шаг 6. Гистограмма яркости до воздействия (32 интервала) и сохранение графика
cd("/user/Котов_Дэвид_Арсенович/LR03")
using Plots
g = luma_images(img)
cb = hist_counts(g, 32)
xc = ((1:32) .- 0.5) ./ 32
hb = bar(xc, cb; bar_width = 1 / 32, legend = false, size = (560, 380),
         title = "Before: scene 5, seed 101", xlabel = "luminance", ylabel = "count")
savefig(hb, "v27_hist_before.png")
println("сохранено: v27_hist_before.png;  занятых интервалов: ", count(>(0), cb), " из 32")
hb

# %% Шаг 7. Воздействие варианта, гистограмма после, сохранение изображений в PNG
cd("/user/Котов_Дэвид_Арсенович/LR03")
h = apply_factor(g, FACTOR)
println("диапазон до:    ", extrema(g))
println("диапазон после: ", extrema(h))
println("значения после в [0, 1]: ", all(0 .<= h .<= 1))
save("v27_before.png", Gray{N0f8}.(g))
save("v27_after.png", Gray{N0f8}.(clamp01.(h)))
ca = hist_counts(h, 32)
ymax = 1.05 * max(maximum(cb), maximum(ca))
ha = bar(xc, ca; bar_width = 1 / 32, legend = false, size = (560, 380), ylims = (0, ymax),
         title = "After: downscale x4 and back", xlabel = "luminance", ylabel = "count")
savefig(ha, "v27_hist_after.png")
hp = plot(bar(xc, cb; bar_width = 1 / 32, legend = false, ylims = (0, ymax), title = "Before", xlabel = "luminance", ylabel = "count"),
          bar(xc, ca; bar_width = 1 / 32, legend = false, ylims = (0, ymax), title = "After", xlabel = "luminance");
          layout = (1, 2), size = (1000, 380))
savefig(hp, "v27_hist_compare.png")
println("сохранено: v27_before.png, v27_after.png, v27_hist_after.png, v27_hist_compare.png")
println("занятых интервалов: до ", count(>(0), cb), ", после ", count(>(0), ca))
mosaicview(Gray.(g), Gray.(clamp01.(h)); nrow = 1, npad = 4, fillvalue = 1)

# %% Шаг 8. Сводка варианта по серии seed 101…105: таблица метрик и PSNR
cd("/user/Котов_Дэвид_Арсенович/LR03")
S = variant_summary(VARIANT)
ps_seed = [psnr_db(luma_images(make_scene(s; P...)), apply_factor(luma_images(make_scene(s; P...)), FACTOR)) for s in 101:105]
println("вариант ", S.variant, ": сцена ", S.ctx, ", воздействие ", S.fac)
println("PSNR по seed 101…105: ", round.(ps_seed; digits = 4))
println("средний PSNR = ", S.psnr, " дБ")
for (m, b, s, a, dd, r, sig) in S.rows
    println(rpad(string(m), 9), "база = ", b, "  s = ", s, "  после = ", a,
            "  Δ = ", dd, "  |Δ|/s = ", round(r; digits = 3), "  |Δ|>2s = ", sig,
            "  отн. = ", round(100 * dd / b; digits = 3), " %")
end

# Для варианта 27: та же сцена, но уменьшение в 2 раза (вариант 26).
S2 = variant_summary(26)
ps_seed2 = [psnr_db(luma_images(make_scene(s; P...)), apply_factor(luma_images(make_scene(s; P...)), 2)) for s in 101:105]
println("Сравнение с уменьшением в 2 раза на той же сцене:")
println("PSNR x2 по seed 101…105: ", round.(ps_seed2; digits = 4))
println("средний PSNR x2 = ", S2.psnr, " дБ; x4 = ", S.psnr, " дБ")
for (m, b, s, a, dd, r, sig) in S2.rows
    println("x2 ", rpad(string(m), 9), "база = ", b, "  s = ", s, "  после = ", a,
            "  Δ = ", dd, "  |Δ|/s = ", round(r; digits = 3), "  |Δ|>2s = ", sig,
            "  отн. = ", round(100 * dd / b; digits = 3), " %")
end

# %% Шаг 9. Значимость: статистическая (|Δ| > 2s) и практическая (допуск, записанный до запуска)
cd("/user/Котов_Дэвид_Арсенович/LR03")
TOL_REL, TOL_PSNR = 0.05, 30.0
println("допуск: относительное изменение > ", 100 * TOL_REL, " %  или  PSNR < ", TOL_PSNR, " дБ")
for (m, b, s, a, dd, r, sig) in S.rows
    rel = abs(dd) / abs(b)
    println(rpad(string(m), 9), "статистически: ", sig ? "значимо" : "не значимо",
            " | практически: ", rel > TOL_REL ? "важно" : "не важно",
            " (", round(100 * rel; digits = 3), " %)")
end
println("PSNR ", round(S.psnr; digits = 3), " дБ: ", S.psnr < TOL_PSNR ? "ниже 30 дБ — практически важно" : "выше 30 дБ — в допуске")
println("\nчувствительность вывода к порогу (основной допуск 5 % не меняется):")
for t in (0.005, 0.01, 0.02, 0.05, 0.10)
    imp = [string(m) for (m, b, s, a, dd, r, sig) in S.rows if abs(dd) / abs(b) > t]
    println("  порог ", rpad(string(100 * t) * " %", 7), "→ практически важны: ", isempty(imp) ? "нет" : join(imp, ", "))
end

# %% Продвинутый уровень рубрики: воспроизведение демонстрационного варианта 1 и сверка с методичкой
cd("/user/Котов_Дэвид_Арсенович/LR03")
D = variant_summary(1)
sha_demo = array_sha(luma_images(make_scene(101)))[1:16]
println("демо PSNR = ", D.psnr, "   в методичке 34.594244830067446   совпало: ", D.psnr == 34.594244830067446)
println("демо SHA  = ", sha_demo, "   в методичке 50567c6b9e5e4ac1   совпало: ", sha_demo == "50567c6b9e5e4ac1")
for (m, b, s, a, dd, r, sig) in D.rows
    println("  ", rpad(string(m), 9), "база = ", b, "  после = ", a, "  |Δ|/s = ", round(r; digits = 3))
end

# %% Сохранение всех значений в файл для отчёта и паспорта эксперимента
cd("/user/Котов_Дэвид_Арсенович/LR03")
open("v27_results.txt", "w") do io
    println(io, "date_utc = ", now(UTC)); println(io, "julia = ", VERSION)
    println(io, "lib_sha256 = ", bytes2hex(open(sha256, lib)))
    println(io, "variant = ", VARIANT, "; scene = ", SCENE, "; factor = ", FACTOR, "; params = ", P)
    println(io, "describe = ", d)
    println(io, "luma_maxdiff = ", maximum(abs.(y_manual .- y_gray)), "; isapprox = ", isapprox(y_manual, y_gray), "; sha_equal = ", array_sha(y_manual) == array_sha(y_gray))
    println(io, "sha_seed101 = ", sha_1, "; repeat_equal = ", sha_1 == sha_2, "; sha_seed102 = ", sha_ctrl)
    println(io, "range_before = ", extrema(g), "; range_after = ", extrema(h))
    println(io, "bins_used_before = ", count(>(0), cb), "; bins_used_after = ", count(>(0), ca))
    println(io, "psnr_mean = ", S.psnr, "; psnr_by_seed = ", ps_seed)
    for (m, b, s, a, dd, r, sig) in S.rows
        println(io, m, ": base=", b, "; s=", s, "; after=", a, "; delta=", dd, "; ratio=", r, "; sig2s=", sig, "; rel=", dd / b)
    end
    println(io, "psnr_x2_mean = ", S2.psnr, "; psnr_x2_by_seed = ", ps_seed2)
    for (m, b, s, a, dd, r, sig) in S2.rows
        println(io, "x2_", m, ": base=", b, "; s=", s, "; after=", a, "; delta=", dd, "; ratio=", r, "; sig2s=", sig, "; rel=", dd / b)
    end
    println(io, "demo_psnr = ", D.psnr, "; demo_sha = ", sha_demo)
    for (m, b, s, a, dd, r, sig) in D.rows
        println(io, "demo_", m, ": base=", b, "; after=", a, "; ratio=", r)
    end
end
print(read("v27_results.txt", String))
