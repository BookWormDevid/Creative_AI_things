# ЛР №4, вариант 27. Котов Дэвид Арсенович.
# Сцена 5 «низкий контраст» (диск 0,55, фон 0,35–0,50, σₙ = 0,03) × операция 3 «фильтр Гаусса, σ = 3».
# Скрипт для Engee. Одна ячейка — один шаг плана методических указаний (раздел 5) или одна проверка.
# Шаг 2 (гипотеза и допуск до запуска) выполнен в журнале LR04/reports/journal.md.
# Рабочая папка в Engee между ячейками не сохраняется, поэтому все файлы пишутся по абсолютному пути W.

# %% Шаг 1. Подготовка среды: дата, версии, рабочая папка, учебные библиотеки
using Dates, SHA
W = "/user/Котов_Дэвид_Арсенович/LR04"
println("Дата и время (UTC): ", now(UTC))
println("VERSION = ", VERSION, ";  потоков Julia: ", Threads.nthreads())
println("Рабочая папка: LR04")
libsha(f) = bytes2hex(open(sha256, joinpath(W, f)))
for (f, ref) in (("lab03_lib.jl", "cd1622643e7cfe7c"), ("lab04_lib.jl", "094cecea2f55a0f5"))
    println(f, ": ", filesize(joinpath(W, f)), " байт, SHA-256 = ", libsha(f),
            ";  совпадает с указаниями (", ref, "…): ", startswith(libsha(f), ref))
end
include(joinpath(W, "lab04_lib.jl"))
println("Images ", pkgversion(Images))
make_gray4(101) |> size

# %% Шаг 3. Зашумлённая и чистая сцены по параметрам варианта
VARIANT = 27
SCENE, OP = divrem(VARIANT - 1, 6) .+ 1
P = scene4(SCENE)
clean = clean4(SCENE)
x101 = make_gray4(101; P...)
println("вариант ", VARIANT, ": сцена ", SCENE, ", операция ", OP, " (фильтр Гаусса, σ = 3)")
println("параметры сцены: ", P)
println("зашумлённая: ", size(x101), " ", eltype(x101), ", диапазон ", extrema(x101))
println("эталон:      ", size(clean), " ", eltype(clean), ", диапазон ", extrema(clean))
println("SHA-256 зашумлённой, seed 101: ", array_sha(x101))
println("SHA-256 повторного построения: ", array_sha(make_gray4(101; P...)), "  совпадение: ", array_sha(x101) == array_sha(make_gray4(101; P...)))
println("SHA-256 эталона:               ", array_sha(clean))
println("доля значений, обрезанных до 0 или 1: ", count(v -> v == 0 || v == 1, x101) / length(x101))

# %% Шаг 4. PSNR зашумлённой сцены относительно эталона и оценка −20·lg σₙ
ps_noisy = [psnr_db(make_gray4(s; P...), clean) for s in 101:105]
println("PSNR зашумлённой по seed 101…105: ", round.(ps_noisy; digits = 4))
println("среднее = ", sum(ps_noisy) / 5, " дБ;  оценка −20·lg(", P.noise, ") = ", -20 * log10(P.noise), " дБ")
println("расхождение = ", sum(ps_noisy) / 5 - (-20 * log10(P.noise)), " дБ")

# %% Шаг 5. Операция варианта, три PNG (зашумлённое, результат, эталон) и карты ошибки
res101, base101, ref101 = pair4(x101, clean, OP)
println("результат: ", size(res101), ", диапазон ", extrema(res101), ";  в [0, 1]: ", all(0 .<= res101 .<= 1))
println("PSNR seed 101: до ", psnr_db(base101, ref101), " дБ, после ", psnr_db(res101, ref101), " дБ")
save(joinpath(W, "v27_noisy.png"), Gray{N0f8}.(clamp01.(x101)))
save(joinpath(W, "v27_result.png"), Gray{N0f8}.(clamp01.(res101)))
save(joinpath(W, "v27_reference.png"), Gray{N0f8}.(clamp01.(clean)))
# Модуль ошибки относительно эталона, усиленный в 10 раз: до операции и после неё
err_before = clamp01.(10 .* abs.(x101 .- clean))
err_after = clamp01.(10 .* abs.(res101 .- clean))
save(joinpath(W, "v27_error_before_x10.png"), Gray{N0f8}.(err_before))
save(joinpath(W, "v27_error_after_x10.png"), Gray{N0f8}.(err_after))
println("сохранено: v27_noisy.png, v27_result.png, v27_reference.png, v27_error_before_x10.png, v27_error_after_x10.png")
mosaicview(Gray.(x101), Gray.(clamp01.(res101)), Gray.(clean), Gray.(err_before), Gray.(err_after); nrow = 1, npad = 4, fillvalue = 1)

# %% Шаг 6. Сводка варианта по серии seed: база, s, после, Δ, |Δ|/s
S = variant_summary4(VARIANT)
println("вариант ", S.variant, ": сцена ", S.ctx, ", операция ", S.fac, ";  IoU: ", S.iou, " (для операции 3 не применяется)")
for (m, b, s, a, dd, r, sig) in S.rows
    println(rpad(string(m), 9), "база = ", b, "  s = ", s, "  после = ", a, "  Δ = ", dd,
            "  |Δ|/s = ", round(r; digits = 2), "  |Δ|>2s = ", sig, "  отн. = ", round(100 * dd / b; digits = 2), " %")
end
ps_after = [psnr_db(gauss4(make_gray4(s; P...), 3), clean) for s in 101:105]
println("PSNR после по seed 101…105: ", round.(ps_after; digits = 4))
println("ΔPSNR по seed: ", round.(ps_after .- ps_noisy; digits = 4))

# %% Шаг 7. Энергия границ: карты модуля градиента Собеля до и после (нормированы на максимум чистой сцены)
cm = maximum(sobelmag(clean))
emap(z) = min.(sobelmag(z) ./ cm, 1.0)
println("энергия границ, seed 101: зашумлённое ", edge_energy(x101), ", результат ", edge_energy(res101), ", эталон ", edge_energy(clean))
save(joinpath(W, "v27_edges_noisy.png"), Gray{N0f8}.(emap(x101)))
save(joinpath(W, "v27_edges_result.png"), Gray{N0f8}.(emap(res101)))
save(joinpath(W, "v27_edges_reference.png"), Gray{N0f8}.(emap(clean)))
println("PSNR карты границ относительно карты эталона: до ", psnr_db(emap(x101), emap(clean)), " дБ, после ", psnr_db(emap(res101), emap(clean)), " дБ")
mosaicview(Gray.(emap(x101)), Gray.(emap(res101)), Gray.(emap(clean)); nrow = 1, npad = 4, fillvalue = 1)

# %% Шаг 8. Классификация по допуску, записанному до запуска, и чувствительность к порогу
TOL = 1.0
dpsnr = S.rows[1][5]
cls(d, t) = d >= t ? "полезна" : d <= -t ? "вредна" : "нейтральна"
println("допуск: полезна при ΔPSNR ≥ +", TOL, " дБ, вредна при ΔPSNR ≤ −", TOL, " дБ")
println("ΔPSNR = ", round(dpsnr; digits = 4), " дБ  →  операция ", cls(dpsnr, TOL))
println("статистически (|Δ| > 2s): ", join([string(m, " ", sig ? "значимо" : "не значимо") for (m, b, s, a, dd, r, sig) in S.rows], "; "))
println("\nчувствительность класса к порогу (основной допуск 1 дБ не меняется):")
for t in (0.25, 0.5, 1.0, 1.5, 2.0, 3.0)
    println("  порог ", rpad(string(t) * " дБ", 8), "→ ", cls(dpsnr, t))
end
println("граница нейтральности по |ΔPSNR| = ", round(abs(dpsnr); digits = 2), " дБ")

# %% Проверка 1. Разложение ошибки: цена размытия эталона и остаток шума
blur_cost = mse(gauss4(clean, 3), clean)
println("MSE(gauss(эталон), эталон) — цена размытия: ", blur_cost, "  (PSNR ", 10 * log10(1 / blur_cost), " дБ)")
nratio = [let x = make_gray4(s; P...); n0 = x .- clean; var(gauss4(x, 3) .- gauss4(clean, 3)) / var(n0) end for s in 101:105]
println("отношение дисперсии шума после фильтра к дисперсии до, по seed: ", round.(nratio; digits = 4))
mse_noisy = [mse(make_gray4(s; P...), clean) for s in 101:105]
mse_after = [mse(gauss4(make_gray4(s; P...), 3), clean) for s in 101:105]
println("MSE до:    ", sum(mse_noisy) / 5)
println("MSE после: ", sum(mse_after) / 5, "  = цена размытия ", blur_cost, " + остаток ", sum(mse_after) / 5 - blur_cost)

# %% Проверка 2. Где кончается польза: развёртка по уровню шума при геометрии сцены 5
using Plots
SIG = [0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.05, 0.07, 0.10]
sweep = map(SIG) do sn
    Q = merge(P, (noise = sn,))
    b = [psnr_db(make_gray4(s; Q...), clean) for s in 101:105]
    a = [psnr_db(gauss4(make_gray4(s; Q...), 3), clean) for s in 101:105]
    (sn, sum(b) / 5, sum(a) / 5, sum(a .- b) / 5, std(a .- b))
end
println(rpad("σₙ", 7), rpad("до, дБ", 10), rpad("после, дБ", 11), rpad("Δ, дБ", 9), "s(Δ)")
for (sn, b, a, d, sd) in sweep
    println(rpad(string(sn), 7), rpad(string(round(b; digits = 3)), 10), rpad(string(round(a; digits = 3)), 11),
            rpad(string(round(d; digits = 3)), 9), round(sd; digits = 4), "  ", cls(d, TOL))
end
i = findfirst(k -> sweep[k][4] < 0 && sweep[k + 1][4] >= 0, 1:length(SIG) - 1)
BREAK = i === nothing ? NaN : SIG[i] + (SIG[i + 1] - SIG[i]) * (-sweep[i][4]) / (sweep[i + 1][4] - sweep[i][4])
println("ΔPSNR = 0 при σₙ ≈ ", round(BREAK; digits = 4), " (линейная интерполяция между соседними точками)")
pl = plot(SIG, [s[2] for s in sweep]; marker = :circle, label = "noisy", xlabel = "noise sigma", ylabel = "PSNR vs reference, dB",
          title = "Gaussian sigma = 3, scene 5 geometry", size = (640, 420), legend = :topright)
plot!(pl, SIG, [s[3] for s in sweep]; marker = :square, label = "after Gaussian")
vline!(pl, [P.noise]; linestyle = :dash, label = "variant 27 (0.03)")
savefig(pl, joinpath(W, "v27_noise_sweep.png"))
println("сохранено: v27_noise_sweep.png")
pl

# %% Проверка 3. Соседние сцены с той же операцией; Гаусс σ=1 и окно 5×5 на своей сцене
for n in (27, 26, 9, 15, 3, 25)
    R = variant_summary4(n)
    d = R.rows[1][5]
    println("вариант ", rpad(string(n), 3), "сцена ", R.ctx, " (σₙ = ", scene4(R.ctx).noise, "), операция ", R.fac,
            ": PSNR ", round(R.rows[1][2]; digits = 3), " → ", round(R.rows[1][4]; digits = 3), ", Δ = ", round(d; digits = 3),
            " дБ, |Δ|/s = ", round(R.rows[1][6]; digits = 1), " → ", cls(d, TOL),
            ";  энергия границ ", round(R.rows[2][2]; digits = 5), " → ", round(R.rows[2][4]; digits = 5))
end

# %% Проверка 4. Воспроизведение демонстрационного варианта 1 и сверка с указаниями бит в бит
D = variant_summary4(1)
DEMO = (psnr = (33.982103137714965, 0.07450305641014086, 29.19575338868147, -4.786349749033494),
        edge = (0.01692548814288977, 0.00012750148456890567, 0.008424262473284544, -0.008501225669605225),
        contrast = (0.20774642267754806, 0.00017156629178605263, 0.20065402164009138, -0.007092401037456675))
DEMO_EXACT = true
for (m, b, s, a, dd, r, sig) in D.rows
    ref = DEMO[m]
    ok = (b, s, a, dd) == ref
    global DEMO_EXACT &= ok
    println(rpad(string(m), 9), "база ", b, "  s ", s, "  после ", a, "  Δ ", dd, "  совпало бит в бит: ", ok)
end
println("демо воспроизведено бит в бит: ", DEMO_EXACT)

# %% Проверка 5. Намеренная ошибка раздела 6.4: сравнение с зашумлённым изображением вместо эталона
wrong = [psnr_db(gauss4(make_gray4(s; P...), 3), make_gray4(s; P...)) for s in 101:105]
println("PSNR(результат, зашумлённое) по seed: ", round.(wrong; digits = 3), ";  среднее ", round(sum(wrong) / 5; digits = 3), " дБ")
println("PSNR(результат, эталон)     по seed: ", round.(ps_after; digits = 3), ";  среднее ", round(sum(ps_after) / 5; digits = 3), " дБ")
println("первое число измеряет, насколько фильтр изменил картинку, а не её качество")

# %% Сохранение всех значений в файл для отчёта и паспорта эксперимента
open(joinpath(W, "v27_results.txt"), "w") do io
    println(io, "date_utc = ", now(UTC)); println(io, "julia = ", VERSION); println(io, "images = ", pkgversion(Images))
    println(io, "lab03_lib_sha256 = ", libsha("lab03_lib.jl")); println(io, "lab04_lib_sha256 = ", libsha("lab04_lib.jl"))
    println(io, "variant = ", VARIANT, "; scene = ", SCENE, "; op = ", OP, "; params = ", P)
    println(io, "sha_noisy_seed101 = ", array_sha(x101), "; sha_clean = ", array_sha(clean))
    println(io, "psnr_noisy_by_seed = ", ps_noisy, "; estimate = ", -20 * log10(P.noise))
    println(io, "psnr_after_by_seed = ", ps_after)
    for (m, b, s, a, dd, r, sig) in S.rows
        println(io, m, ": base=", b, "; s=", s, "; after=", a, "; delta=", dd, "; ratio=", r, "; sig2s=", sig, "; rel=", dd / b)
    end
    println(io, "class = ", cls(dpsnr, TOL), "; tol_db = ", TOL)
    println(io, "blur_cost_mse = ", blur_cost, "; noise_ratio = ", nratio)
    println(io, "mse_noisy_mean = ", sum(mse_noisy) / 5, "; mse_after_mean = ", sum(mse_after) / 5)
    for (sn, b, a, d, sd) in sweep
        println(io, "sweep sigma=", sn, ": before=", b, "; after=", a, "; delta=", d, "; sd=", sd)
    end
    println(io, "break_even_sigma = ", BREAK)
    for n in (26, 9, 15, 3, 25)
        R = variant_summary4(n)
        println(io, "variant_", n, ": psnr_before=", R.rows[1][2], "; psnr_after=", R.rows[1][4], "; delta=", R.rows[1][5], "; ratio=", R.rows[1][6],
                "; edge_before=", R.rows[2][2], "; edge_after=", R.rows[2][4])
    end
    println(io, "demo_exact = ", DEMO_EXACT)
    println(io, "wrong_reference_psnr = ", wrong)
end
print(read(joinpath(W, "v27_results.txt"), String))
