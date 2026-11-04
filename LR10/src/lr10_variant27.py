# ЛР 10, вариант 27. Котов Дэвид Арсенович.
# Запуск в Engee из папки, где лежит lab10_lib.py:  python lr10_variant27.py
# Сводку считает variant_summary(27, save_dir="v27") из библиотеки без изменений, листы слепого сравнения — blind_sheets(27, "v27").
# Вызов measure() обёрнут регистратором: он записывает значения по seed и сохраняет изображения ещё и в PNG (без потерь).
# Ключ слепого сравнения (v27/blind_key.json) скрипт не читает и не печатает.
import hashlib, json, math, os, platform, resource, sys, time
from pathlib import Path
import numpy as np
import torch, diffusers, transformers, scipy, PIL, huggingface_hub
HERE = Path(__file__).resolve().parent
os.chdir(HERE)
sys.path.insert(0,str(HERE))
raw = (HERE/"lab10_lib.py").read_bytes()
LIB_SHA = hashlib.sha256(raw).hexdigest()
if LIB_SHA != "b53293ebd2422295cfa2fd01e4dcc5f8eaef440c0802a80803d3771c19ce2f6c":
    raise RuntimeError("SHA-256 учебной библиотеки не совпал")
LIBRARIES = {"lab10_lib.py":dict(bytes=len(raw),sha256=LIB_SHA), Path(__file__).name:dict(bytes=Path(__file__).stat().st_size,sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())}
import lab10_lib as L

N = 27
C, K = (N - 1) // 6, (N - 1) % 6
OUT = "v27"
os.makedirs(OUT, exist_ok=True)


def sha(img):
    return hashlib.sha256(np.asarray(img).tobytes()).hexdigest()


def cpu_model():
    try:
        return next(l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name"))
    except Exception:
        return platform.processor()


rec = []
_measure = L.measure


def measure_logged(pipe, clip, key, ctx, seed, cfg=None):
    r, img = _measure(pipe, clip, key, ctx, seed, cfg)
    img.save(os.path.join(OUT, f"{key}_s{seed}.png"))
    rec.append(dict(model=key, seed=seed, **r, pixels_sha256=sha(img)))
    print(f"  {key} seed {seed}: clip_brief {r['clip_brief']:.2f}  clip_text {r['clip_text']:.2f}  "
          f"edge {r['edge']:.4f}  contrast {r['contrast']:.4f}  {r['seconds']:.1f} с", flush=True)
    return r, img




_load = L.load_model
load_seconds = {}
schedulers = {}


def load_logged(key):
    t0 = time.perf_counter(); p = _load(key); load_seconds[key] = time.perf_counter() - t0
    schedulers[key] = type(p.scheduler).__name__
    print(f"загрузка {key}: {load_seconds[key]:.1f} с; планировщик {type(p.scheduler).__name__}", flush=True)
    return p




a_key, b_key = L.PAIRS[K]
assert (C,K,a_key,b_key) == (4,2,"turbo","amused")
assert L.MODELS[a_key]["size"] == 512 and L.MODELS[b_key]["size"] == 256
env = dict(engee=os.getenv("LR10_ENGEE_VERSION") or None,julia=os.getenv("LR10_JULIA_VERSION") or None,device="cpu",dtype="float32",
           date_utc=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), python=sys.version.split()[0],
           torch=torch.__version__, diffusers=diffusers.__version__, transformers=transformers.__version__,
           numpy=np.__version__, scipy=scipy.__version__, pillow=PIL.__version__, huggingface_hub=huggingface_hub.__version__,
           cuda=torch.cuda.is_available(), torch_threads=torch.get_num_threads(), cpu=cpu_model(), cpu_count=os.cpu_count(),
           clip=L.CLIP_ID, clip_revision=L.CLIP_REVISION, seeds=list(L.SEEDS),
           models={k: L.MODELS[k] for k in (a_key, b_key)})
print("Среда:", json.dumps(env, ensure_ascii=False), flush=True)
print(f"Вариант {N}: бриф {C + 1}, пара {K + 1}: A = {a_key}, B = {b_key}")
print("бриф:", repr(L.BRIEFS[C]), flush=True)

t0 = time.perf_counter()
L.measure = measure_logged
L.load_model = load_logged
try:
    M = L.variant_summary(N, save_dir=OUT)
finally:
    L.measure = _measure
    L.load_model = _load
t_all = time.perf_counter() - t0
print(f"variant_summary: {t_all:.1f} с (CLIP, две загрузки, два прогрева, 10 изображений)", flush=True)
L.blind_sheets(N, OUT)   # ключ не печатается
print("листы слепого сравнения:", sorted(f for f in os.listdir(OUT) if f.startswith("blind_") and f.endswith(".png")))

print("\nСводка variant_summary (как в указаниях):")
print(f"{'метрика':<12}{'A':>10}{'s':>9}{'B':>10}{'Δ':>10}{'|Δ|/s':>8}  |Δ|>2s")
for m, a, s, b, d, q, f in M["rows"]:
    nd = 4 if m in ("edge", "contrast") else 2
    print(f"{m:<12}{a:>10.{nd}f}{s:>9.{nd}f}{b:>10.{nd}f}{d:>+10.{nd}f}{q:>8.1f}  {'да' if f else 'нет'}")

A = [r for r in rec if r["model"] == a_key]; B = [r for r in rec if r["model"] == b_key]
rows_check = L.compare(A, B)
same = all(x == y or abs(x - y) < 1e-12 for r1, r2 in zip(M["rows"], rows_check) for x, y in zip(r1[1:6], r2[1:6]))
print("\nПересчёт сводки по записанным значениям совпал с variant_summary:", same)
ratio = float(np.mean([r["seconds"] for r in B]) / np.mean([r["seconds"] for r in A]))
print(f"отношение времён B/A: {ratio:.2f}")

print("\nПо seed (clip_brief):")
ba = [r["clip_brief"] for r in A]; bb = [r["clip_brief"] for r in B]
print("seed  " + "  ".join(f"{r['seed']:>7}" for r in A))
print("A     " + "  ".join(f"{x:>7.2f}" for x in ba))
print("B     " + "  ".join(f"{x:>7.2f}" for x in bb))
dd = [b - a for a, b in zip(ba, bb)]
print("B − A " + "  ".join(f"{x:>+7.2f}" for x in dd))

# Бриф 5 не совпадает с демонстрационным брифом 1: прямое совпадение их средних не проверяется.

peak_gb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20
print(f"\nпик памяти процесса: {peak_gb:.1f} ГБ")
TOL = dict(clip_brief=1.0,clip_text=1.0,edge=0.10,contrast=0.10,seconds_factor=1.5)

def practical(metric,a,b,mult=1.0):
    if metric=="seconds":
        factor=mult
        if a<=0 or b<=0: raise ValueError("Время должно быть положительным")
        ratio=b/a
        return ((ratio>factor and not math.isclose(ratio,factor,rel_tol=1e-12)) or
                (ratio<1/factor and not math.isclose(ratio,1/factor,rel_tol=1e-12)))
    threshold=TOL[metric] if metric.startswith("clip_") else abs(a)*TOL[metric]
    delta=abs(b-a);boundary=threshold*mult
    return delta>boundary and not math.isclose(delta,boundary,rel_tol=1e-12,abs_tol=1e-15)

CLASSES={};SENS={}
for name,a,sd,b,delta,q,sig in M["rows"]:
    outside=practical(name,a,b,TOL["seconds_factor"] if name=="seconds" else 1.0)
    label="значимо и важно" if sig and outside else "только 2s" if sig else "только допуск" if outside else "ни то ни другое"
    CLASSES[name]=dict(sig2s=sig,practical=outside,label=label)
    SENS[name]={str(v):practical(name,a,b,v) for v in ((1.25,1.5,2.0) if name=="seconds" else (0.5,1.0,2.0))}
    print(name,CLASSES[name],flush=True)
M["rows"]=[(*row[:5],row[5] if math.isfinite(row[5]) else None,row[6]) for row in M["rows"]]
json.dump(dict(libraries=LIBRARIES,schedulers=schedulers,tolerance=TOL,classification=CLASSES,sensitivity=SENS,new_session_checked=False,
               variant=N, ctx=C + 1, pair=[a_key, b_key], brief=L.BRIEFS[C], env=env, load_seconds=load_seconds,
               variant_summary_seconds=t_all, peak_rss_gb=peak_gb, rows=M["rows"], rows_recomputed_match=same,
               time_ratio=ratio, per_seed=rec),
          open("results_v27.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, allow_nan=False)
print("записано: results_v27.json, изображения и листы слепого сравнения в", OUT)

# Манифест не открывает и не раскрывает blind_key.json.
common=dict(variant=N,brief=L.BRIEFS[C],models={key:L.MODELS[key] for key in (a_key,b_key)},
            clip=dict(id=L.CLIP_ID,revision=L.CLIP_REVISION),environment=env,libraries=LIBRARIES,
            schedulers=schedulers,generator_device="cpu",dtype="float32",seeds=list(L.SEEDS))
image_manifest=dict(common,files={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    for p in sorted(Path(OUT).iterdir()) if p.is_file() and p.name!="blind_key.json" and p.name!="manifest.json"})
(Path(OUT)/"manifest.json").write_text(json.dumps(image_manifest,ensure_ascii=False,indent=2,allow_nan=False),encoding="utf-8")
paths=[Path("results_v27.json"),Path(OUT)/"manifest.json"]
manifest=dict(common,files={p.as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths})
Path("manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2,allow_nan=False),encoding="utf-8")
print("Готово: results_v27.json, manifest.json, v27/; ключ слепого сравнения не показан.",flush=True)
