# ЛР 9, вариант 27, часть 1. Котов Дэвид Арсенович.
# Запуск в Engee из папки, где лежит lab09_lib.py:  python lr09_variant27.py
# Сводку считает variant_summary() из библиотеки без изменений. Вызов measure() обёрнут регистратором: он записывает
# значения по seed (сходство со всеми целями контекста, edge, contrast, время) и сохраняет изображения в PNG.
# Результаты: v27/A_s<seed>.png, v27/B_s<seed>.png, results_v27.json, печать в stdout.
import hashlib, io, json, math, os, platform, resource, sys, time
from pathlib import Path
import numpy as np
import torch, diffusers, transformers, scipy, PIL, huggingface_hub
HERE = Path(__file__).resolve().parent
os.chdir(HERE)
sys.path.insert(0, str(HERE))
LIBRARIES = {}
for filename, expected in (("lab09_lib.py", "cc4d233de574e47a73d2126234ee0b8e9f5d80aa0ed6d4a2fac9748ac0f7b062"), ("lab09_llm.py", "5eabb31fd8ba76f103020177acfb04cdb2127352cbddf22e67f2c0b4835abcb5")):
    data = (HERE/filename).read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected: raise RuntimeError("SHA-256 не совпал: "+filename)
    LIBRARIES[filename] = dict(bytes=len(data),sha256=actual)
LIBRARIES[Path(__file__).name] = dict(bytes=Path(__file__).stat().st_size,sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
import lab09_lib as L

N = 27
C, K = (N - 1) // 6, (N - 1) % 6
OUT = "v27"
assert (C, K, L.FACTORS[K]) == (4, 2, "palette")
os.makedirs(OUT, exist_ok=True)


def png_bytes(img):
    b = io.BytesIO(); img.save(b, format="PNG"); return b.getvalue()


def sha(img):
    return hashlib.sha256(np.asarray(img).tobytes()).hexdigest()


def cpu_model():
    try:
        return next(l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name"))
    except Exception:
        return platform.processor()


rec = []
_measure = L.measure


def measure_logged(pipe, clip, c, prompt, seed):
    r, img = _measure(pipe, clip, c, prompt, seed)
    mode = "A" if prompt == L.prompt_a(C) else "B"
    img.save(os.path.join(OUT, f"{mode}_s{seed}.png"))
    rec.append(dict(mode=mode, seed=seed, prompt=prompt, sims=r["sims"], edge=r["edge"], contrast=r["contrast"],
                    seconds=r["seconds"], pixels_sha256=sha(img)))
    print(f"  {mode} seed {seed}: clip_target {r['sims'][1 + K]:.2f}  clip_subject {r['sims'][0]:.2f}  "
          f"edge {r['edge']:.4f}  contrast {r['contrast']:.4f}  {r['seconds']:.1f} с", flush=True)
    return r, img



env = dict(engee=os.getenv("LR09_ENGEE_VERSION") or None, julia=os.getenv("LR09_JULIA_VERSION") or None, device="cpu", dtype="float32",
           date_utc=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), python=sys.version.split()[0],
           torch=torch.__version__, diffusers=diffusers.__version__, transformers=transformers.__version__,
           numpy=np.__version__, scipy=scipy.__version__, pillow=PIL.__version__, huggingface_hub=huggingface_hub.__version__,
           cuda=torch.cuda.is_available(), torch_threads=torch.get_num_threads(), cpu=cpu_model(), cpu_count=os.cpu_count(),
           model=L.MODEL_ID, revision=L.REVISION, clip=L.CLIP_ID, clip_revision=L.CLIP_REVISION,
           steps=L.STEPS, guidance=L.GUIDANCE, size=L.SIZE, seeds=list(L.SEEDS))
print("Среда:", json.dumps(env, ensure_ascii=False), flush=True)
print(f"Вариант {N}: контекст {C + 1}, элемент {K + 1} ({L.FACTORS[K]})")
print("A:", repr(L.prompt_a(C)))
print("B:", repr(L.prompt_b(C, K)))
print("текст-цель CLIP:", repr(L.ELEMENTS[C][K][1]), flush=True)

t0 = time.perf_counter(); pipe = L.load_pipe(); t_pipe = time.perf_counter() - t0
t0 = time.perf_counter(); clip = L.load_clip(); t_clip = time.perf_counter() - t0
print(f"загрузка: SD Turbo {t_pipe:.1f} с, CLIP {t_clip:.1f} с", flush=True)

t0 = time.perf_counter()
L.measure = measure_logged
try:
    M = L.variant_summary(pipe, clip, N)
finally:
    L.measure = _measure
t_series = time.perf_counter() - t0
print(f"серия (прогрев + 10 изображений + CLIP): {t_series:.1f} с", flush=True)

print("\nСводка variant_summary (как в указаниях):")
print(f"{'метрика':<13}{'A':>10}{'s':>9}{'B':>10}{'Δ':>10}{'|Δ|/s':>8}  |Δ|>2s")
for m, a, s, b, d, q, f in M["rows"]:
    nd = 4 if m in ("edge", "contrast") else 2
    print(f"{m:<13}{a:>10.{nd}f}{s:>9.{nd}f}{b:>10.{nd}f}{d:>+10.{nd}f}{q:>8.1f}  {'да' if f else 'нет'}")

A = [r for r in rec if r["mode"] == "A"]; B = [r for r in rec if r["mode"] == "B"]
rows_check = L.compare([dict(sims=r["sims"], edge=r["edge"], contrast=r["contrast"]) for r in A],
                       [dict(sims=r["sims"], edge=r["edge"], contrast=r["contrast"]) for r in B], K)
same = all(x == y or abs(x - y) < 1e-12 for r1, r2 in zip(M["rows"], rows_check) for x, y in zip(r1[1:6], r2[1:6]))
print("\nПересчёт сводки по записанным значениям совпал с variant_summary:", same)

print("\nПо seed (clip_target):")
ta = [r["sims"][1 + K] for r in A]; tb = [r["sims"][1 + K] for r in B]
print("seed  " + "  ".join(f"{r['seed']:>7}" for r in A))
print("A     " + "  ".join(f"{x:>7.2f}" for x in ta))
print("B     " + "  ".join(f"{x:>7.2f}" for x in tb))
dd = [b - a for a, b in zip(ta, tb)]
print("B − A " + "  ".join(f"{x:>+7.2f}" for x in dd))
md, sd = float(np.mean(dd)), float(np.std(dd, ddof=1))
print(f"парные разности: положительных {sum(x > 0 for x in dd)} из 5; среднее {md:+.2f}, s разностей {sd:.2f}, среднее/s {md / sd if sd else float('nan'):.2f}")

# Демонстрационный контекст 1 не равен нашему контексту 5: его значения не сравниваются как повтор режима A.
print("\nОпределённость: повторная генерация seed 101", flush=True)
rep = {}
for mode, prompt in (("A", L.prompt_a(C)), ("B", L.prompt_b(C, K))):
    img = L.generate(pipe, prompt, 101)
    first = next(r for r in rec if r["mode"] == mode and r["seed"] == 101)
    rep[mode] = sha(img) == first["pixels_sha256"]
    print(f"  {mode}: пиксели совпали с серией бит в бит — {rep[mode]}")

peak_gb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20
print(f"\nпик памяти процесса: {peak_gb:.1f} ГБ; среднее время изображения A {np.mean([r['seconds'] for r in A]):.1f} с, "
      f"B {np.mean([r['seconds'] for r in B]):.1f} с")

for row in M["rows"]:
    if not math.isfinite(row[5]):
        row_index = M["rows"].index(row)
        M["rows"][row_index] = (*row[:5], None, row[6])

TOL = dict(clip_target=1.0, clip_subject=1.0, edge=0.10, contrast=0.10)
CLASSIFICATION = {}
SENSITIVITY = {}
for m,a,sd_base,b,delta,ratio,sig in M["rows"]:
    boundary = TOL[m] if m.startswith("clip_") else abs(a)*TOL[m]
    practical = abs(delta)>boundary
    label = "значимо и важно" if sig and practical else "только 2s" if sig else "только допуск" if practical else "ни то ни другое"
    CLASSIFICATION[m] = dict(sig2s=sig, practical=practical, threshold_absolute=boundary, label=label)
    SENSITIVITY[m] = {str(mult): abs(delta)>boundary*mult for mult in (0.5,1,2)}
    print(m,CLASSIFICATION[m],flush=True)

json.dump(dict(libraries=LIBRARIES, classification=CLASSIFICATION, tolerance=TOL, sensitivity=SENSITIVITY,
               scheduler=type(pipe.scheduler).__name__, new_session_checked=False, variant=N, ctx=C + 1, factor=L.FACTORS[K], prompt_a=L.prompt_a(C), prompt_b=L.prompt_b(C, K),
               target=L.ELEMENTS[C][K][1], texts=L.texts_for(C), env=env, load_seconds=dict(pipe=t_pipe, clip=t_clip),
               series_seconds=t_series, peak_rss_gb=peak_gb, rows=M["rows"], rows_recomputed_match=same,
               per_seed=rec, paired=dict(diffs=dd, mean=md, sd=sd), repeat_seed101_bit_identical=rep),
          open("results_v27.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, allow_nan=False)
print("записано: results_v27.json, изображения в", OUT)

# Манифест рядом с исходными PNG; JSON сводки хранится отдельно от изображений.
common = dict(variant=N,model=dict(id=L.MODEL_ID,revision=L.REVISION),
              metric_model=dict(id=L.CLIP_ID,revision=L.CLIP_REVISION),environment=env,libraries=LIBRARIES,
              steps=L.STEPS,guidance_scale=L.GUIDANCE,size=L.SIZE,generator_device="cpu",dtype="float32")
image_manifest=dict(common,files={f"{r['mode']}_s{r['seed']}.png": dict(mode=r["mode"],seed=r["seed"],prompt=r["prompt"],
    pixels_sha256=r["pixels_sha256"],sha256=hashlib.sha256((Path(OUT)/f"{r['mode']}_s{r['seed']}.png").read_bytes()).hexdigest()) for r in rec})
(Path(OUT)/"manifest.json").write_text(json.dumps(image_manifest,ensure_ascii=False,indent=2,allow_nan=False),encoding="utf-8")
from PIL import Image
images=[Image.open(Path(OUT)/f"{mode}_s101.png").convert("RGB") for mode in ("A","B")]
sheet=Image.new("RGB",(2*L.SIZE,L.SIZE));sheet.paste(images[0],(0,0));sheet.paste(images[1],(L.SIZE,0));sheet.save("comparison.png")
files=[Path("results_v27.json"),Path("comparison.png"),*sorted(Path(OUT).glob("*.png")),Path(OUT)/"manifest.json"]
manifest=dict(common,files={p.as_posix(): dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files})
Path("manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2,allow_nan=False),encoding="utf-8")
print("Готово: results_v27.json, comparison.png, manifest.json и v27/",flush=True)
