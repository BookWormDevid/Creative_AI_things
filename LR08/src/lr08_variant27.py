# ЛР №8. Генерация и интерполяция в латентном пространстве.
# Котов Дэвид Арсенович, вариант 27: два диска × d=8→2.
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Engee: расчёт на процессоре.
import functools, hashlib, json, math, platform, sys, time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import torch
import PIL
from PIL import Image
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent if HERE.name == "src" else HERE
ART = ROOT / "artifacts" / "engee"
ART.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(HERE))
print = functools.partial(print, flush=True)
if (ART / "results_v27.json").exists():
    print("Готовая серия уже сохранена: LR08/artifacts/engee/results_v27.json. Повторное обучение не запускалось.")
    raise SystemExit(0)
T_START = time.perf_counter()
LIBS = {}
for filename, expected in (
    ("lab07_lib.py", "d84b83a878f55e95289d76a788dc9fa84d3249d0d33aa719d9db8d6792fd2698"),
    ("lab08_lib.py", "f414c49bd0df4eb3aae1f822b29ef2eb112979afc078b26bc65645fd3f43fe9f"),
    ("lab08_demo.py", "8ab781bf6a0e71fb9c007e2a0d88f25f96686aa7fb1237190be9846672865c53")):
    data = (HERE / filename).read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    print(filename, len(data), actual)
    if actual != expected:
        raise RuntimeError("SHA-256 не совпал: " + filename)
    LIBS[filename] = dict(bytes=len(data), sha256=actual)
LIBS["lr08_variant27.py"] = dict(bytes=Path(__file__).stat().st_size, sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
import lab07_lib as L
import lab08_lib as V
assert L.DEVICE == "cpu"
ENV = dict(date_utc=datetime.now(timezone.utc).isoformat(), engee=os.getenv("LR08_ENGEE_VERSION"),
           julia=os.getenv("LR08_JULIA_VERSION"), python=platform.python_version(), platform=platform.platform(),
           torch=torch.__version__, numpy=np.__version__, Pillow=PIL.__version__, device=L.DEVICE, dtype="float32",
           threads=torch.get_num_threads(), cuda_available=torch.cuda.is_available(),
           cudnn_deterministic=torch.backends.cudnn.deterministic,
           cudnn_benchmark=torch.backends.cudnn.benchmark,
           deterministic_algorithms=torch.are_deterministic_algorithms_enabled())
print("СРЕДА:", ENV)
VARIANT = 27
c, k = divmod(VARIANT - 1, 6)
KIND, FACTOR = L.KINDS[c], V.FACTORS[k]
a_cfg, b_cfg = V.settings(FACTOR)
SEEDS = list(L.SEEDS)
DIFF = {q: (a_cfg[q], b_cfg[q]) for q in a_cfg if a_cfg[q] != b_cfg[q]}
assert KIND == "two_discs" and FACTOR == "latent_8_to_2"
assert DIFF == {"d": (8, 2)}
TOL = dict(recon=1.0, interp=1.0, sample=1.0, r2=0.05)
print("Вариант:", VARIANT, "набор:", KIND, "фактор:", FACTOR, "A:", a_cfg, "B:", b_cfg)
print("Допуски до запуска:", TOL, "; гипотеза: все четыре метрики снизятся больше допуска.")
Xtr, Xte, Ftr, Fte = L.dataset(KIND)
MEAN_PSNR = L.psnr_images(Xtr.mean(0, keepdim=True).expand_as(Xte), Xte)
DATA_SHA = {name: hashlib.sha256(t.cpu().contiguous().numpy().tobytes()).hexdigest()
            for name, t in (("train", Xtr), ("test", Xte), ("train_factors", Ftr), ("test_factors", Fte))}
print("Данные:", tuple(Xtr.shape), tuple(Xte.shape), "; средняя картинка:", MEAN_PSNR)
# Обучение с тем же кэшем get_model, что в учебной библиотеке.
TRAIN_SEC = {"A": {}, "B": {}}
for seed in SEEDS:
    for mode, cfg in (("A", a_cfg), ("B", b_cfg)):
        print("START обучение", mode, "seed", seed, "d", cfg["d"])
        t0 = time.perf_counter()
        V.get_model(KIND, cfg, seed)
        TRAIN_SEC[mode][str(seed)] = time.perf_counter() - t0
        print("DONE обучение", mode, "seed", seed, "секунд", round(TRAIN_SEC[mode][str(seed)], 2))
# variant_summary остаётся учебной; обёртка только записывает её измерения.
PER_SEED = {"A": {}, "B": {}}
_run = V.run

def run_logged(kind, cfg, seed):
    value = _run(kind, cfg, seed)
    mode = "A" if cfg == a_cfg else "B"
    PER_SEED[mode][str(seed)] = value
    print("METRICS", mode, "seed", seed, value)
    return value

V.run = run_logged
try:
    result = V.variant_summary(VARIANT)
finally:
    V.run = _run
ROWS = {name: dict(A=a, s=sd, B=b, delta=delta, ratio=ratio if math.isfinite(ratio) else None, sig2s=sig)
        for name, a, sd, b, delta, ratio, sig in result["rows"]}

def classify(delta, tolerance):
    return "улучшение" if delta > tolerance else "ухудшение" if delta < -tolerance else "нейтрально"

CLASSES = {}
print("ИТОГ ОСНОВНОЙ СЕРИИ")
for name, row in ROWS.items():
    av = [v[name] for v in PER_SEED["A"].values()]
    bv = [v[name] for v in PER_SEED["B"].values()]
    assert np.isclose(row["A"], np.mean(av)) and np.isclose(row["B"], np.mean(bv))
    assert np.isclose(row["s"], np.std(av, ddof=1))
    CLASSES[name] = classify(row["delta"], TOL[name])
    print(name, row, CLASSES[name])
SENS = {str(mult): {name: classify(row["delta"], TOL[name]*mult) for name,row in ROWS.items()}
        for mult in (0.25, 0.5, 1, 1.5, 2, 4)}
PAIRED = {}
for name in ROWS:
    differences = [PER_SEED["B"][str(s)][name]-PER_SEED["A"][str(s)][name] for s in SEEDS]
    se = float(np.std(differences, ddof=1) / np.sqrt(len(SEEDS)))
    delta = ROWS[name]["delta"]
    PAIRED[name] = dict(differences=differences, se=se, descriptive_interval=[delta-2*se, delta+2*se])
print("Чувствительность:", SENS)
print("Описательные диапазоны, не 95%-е ДИ:", PAIRED)

@torch.no_grad()
def diagnose(model, variational=True):
    mu, lv = model.encode_dist(Xte)
    train_mu = model.encode(Xtr)
    design = torch.cat([train_mu, torch.ones(train_mu.shape[0], 1, device=L.DEVICE)], 1).double()
    weights = torch.linalg.solve(design.T@design + 1e-6*torch.eye(design.shape[1], device=L.DEVICE, dtype=design.dtype), design.T@Ftr.double()).float()
    prediction = torch.cat([mu, torch.ones(mu.shape[0], 1, device=L.DEVICE)], 1)@weights
    r2 = 1-((prediction-Fte)**2).sum(0)/((Fte-Fte.mean(0))**2).sum(0)
    row = dict(mu_std=mu.std(0).cpu().tolist(), mu_mean=mu.mean(0).cpu().tolist(),
               mu_mean_norm=float(mu.norm(dim=1).mean()), r2_each_factor=r2.cpu().tolist(), r2_mean=float(r2.mean()))
    if variational:
        kl = (-0.5*(1+lv-mu**2-lv.exp())).mean(0)
        row.update(kl_axis=kl.cpu().tolist(), active=int((kl>0.05).sum()),
                   active_threshold_nat=0.05, sigma_mean=float(torch.exp(0.5*lv).mean()))
    return row

DIAG, MODEL_SHA = {"A": {}, "B": {}}, {"A": {}, "B": {}}
for mode,cfg in (("A",a_cfg),("B",b_cfg)):
    for seed in SEEDS:
        model=V.get_model(KIND,cfg,seed)
        q=diagnose(model)
        assert np.isclose(q["r2_mean"], PER_SEED[mode][str(seed)]["r2"], atol=1e-6)
        DIAG[mode][str(seed)]=q
        MODEL_SHA[mode][str(seed)]=hashlib.sha256(b"".join(t.detach().cpu().contiguous().numpy().tobytes() for t in model.state_dict().values())).hexdigest()
        print("DIAG",mode,"seed",seed,q)
# Диагностика обычного AE отделена от изменения d у VAE.
print("START дополнительный AE beta=0, d=8, seed 101")
ae_cfg=dict(V.BASE,beta=0.0)
ae=V.get_model(KIND,ae_cfg,101)
ae_diag=diagnose(ae, variational=False)
ae_weight_sha=hashlib.sha256(b"".join(t.detach().cpu().contiguous().numpy().tobytes() for t in ae.state_dict().values())).hexdigest()
ae_diag["active"]=None  # KL не обучался при beta=0; признак активности не интерпретируется.

@torch.no_grad()
def nearest_psnr(model,z):
    xs=model.decode(z).flatten(1)
    mse=torch.cdist(xs,Xte.flatten(1)).pow(2)/xs.shape[1]
    return float((10*torch.log10(1/mse.min(1).values.clamp_min(1e-10))).mean())

with torch.no_grad():
    mu_train=ae.encode(Xtr).cpu().double()
    fitted_mean=mu_train.mean(0)
    fitted_cov=torch.cov(mu_train.T)+1e-6*torch.eye(mu_train.shape[1],dtype=mu_train.dtype)
    chol=torch.linalg.cholesky(fitted_cov)
    eps=torch.randn((V.N_SAMPLES,8),generator=torch.Generator(device="cpu").manual_seed(1101))
    fitted_z=(fitted_mean+eps.double()@chol.T).float()
    AE_SAMPLES=dict(seed=101, model=ae_cfg, diagnostic=ae_diag,
                    weight_tensor_sha256=ae_weight_sha, N01_psnr=nearest_psnr(ae,eps.to(L.DEVICE)), fitted_psnr=nearest_psnr(ae,fitted_z.to(L.DEVICE)),
                    fitted_train_mean=fitted_mean.tolist(), fitted_train_cov=fitted_cov.tolist(), covariance_jitter=1e-6)
print("AE N(0,I) / N(mu_train,Sigma_train):",AE_SAMPLES)
# Маски обоих цветов; не подменяют визуальную проверку.
_yy,_xx=torch.meshgrid(torch.arange(L.N,dtype=torch.float32,device=L.DEVICE),torch.arange(L.N,dtype=torch.float32,device=L.DEVICE),indexing="ij")

@torch.no_grad()
def geometry(images,color):
    red,green,blue=images[:,0],images[:,1],images[:,2]
    mask=(red>0.65)&((green-blue>0.10) if color=="amber" else (blue-green>0.05))
    m=mask.float();area=m.sum((1,2));count=area.clamp_min(1)
    return dict(mask=mask,area=area,cx=(m*_xx).sum((1,2))/count,cy=(m*_yy).sum((1,2))/count)

@torch.no_grad()
def compare_geometry(images,targets):
    out={}
    for color in ("amber","pink"):
        a,b=geometry(images,color),geometry(targets,color)
        union=(a["mask"]|b["mask"]).sum((1,2)).clamp_min(1)
        valid=(a["area"]>0)&(b["area"]>0)
        value=dict(empty_masks=int((a["area"]==0).sum()),target_empty_masks=int((b["area"]==0).sum()),
                   area_mae=float((a["area"]-b["area"]).abs().mean()),
                   mean_iou=float(((a["mask"]&b["mask"]).sum((1,2))/union).mean()), valid_centroids=int(valid.sum()))
        for key in ("cx","cy"):
            value[key+"_mae_nonempty"]=float((a[key][valid]-b[key][valid]).abs().mean()) if bool(valid.any()) else None
        out[color]=value
    return out

ia,ib,tg=V.interp_targets(KIND)
INTERP_SHAPE={"A":{},"B":{}}
with torch.no_grad():
    targets=torch.cat([tg[t] for t in (0.25,0.5,0.75)])
    for mode,cfg in (("A",a_cfg),("B",b_cfg)):
        for seed in SEEDS:
            model=V.get_model(KIND,cfg,seed);mu=model.encode(Xte)
            path=torch.cat([model.decode((1-t)*mu[ia]+t*mu[ib]) for t in (0.25,0.5,0.75)])
            INTERP_SHAPE[mode][str(seed)]=compare_geometry(path,targets)
            print("Маски 200 пар × 3 точки",mode,seed,INTERP_SHAPE[mode][str(seed)])
# Лист: четыре ряда сэмплов, истинный путь, A, B, смешение пикселей.
N_VIS=9
PAIR=(0,2)
t_values=torch.linspace(0,1,N_VIS,device=L.DEVICE).unsqueeze(1)
model_a,model_b=V.get_model(KIND,a_cfg,101),V.get_model(KIND,b_cfg,101)
visual_eps=torch.randn((N_VIS,8),generator=torch.Generator(device="cpu").manual_seed(5))
with torch.no_grad():
    f0,f2=Fte[PAIR[0]].cpu().numpy(),Fte[PAIR[1]].cpu().numpy()
    true_path=torch.tensor(np.stack([L.render(KIND,(1-t)*f0+t*f2) for t in t_values[:,0].cpu().numpy()]),device=L.DEVICE)
    rows=[ae.decode(visual_eps.to(L.DEVICE)),ae.decode((fitted_mean+visual_eps.double()@chol.T).float().to(L.DEVICE)),
          model_a.decode(visual_eps.to(L.DEVICE)),model_b.decode(visual_eps[:,:2].to(L.DEVICE)),true_path]
    VIS_SHAPE={}
    for mode,model in (("A",model_a),("B",model_b)):
        za,zb=model.encode(Xte[PAIR[0]:PAIR[0]+1]),model.encode(Xte[PAIR[1]:PAIR[1]+1])
        path=model.decode((1-t_values)*za+t_values*zb);rows.append(path)
        VIS_SHAPE[mode]=[compare_geometry(path[i:i+1],true_path[i:i+1]) for i in range(N_VIS)]
    rows.append((1-t_values[:,:,None,None])*Xte[PAIR[0]:PAIR[0]+1]+t_values[:,:,None,None]*Xte[PAIR[1]:PAIR[1]+1])
    grid=np.concatenate([np.concatenate(list(x.permute(0,2,3,1).cpu().numpy()),axis=1) for x in rows],axis=0)
sheet=Image.fromarray((np.clip(grid,0,1)*255).round().astype("uint8")).resize((N_VIS*L.N*4,len(rows)*L.N*4),Image.NEAREST)
sheet.save(ART/"comparison.png")
ROW_NAMES=["AE N(0,I)","AE fitted train Gaussian","VAE A d=8 N(0,I)","VAE B d=2 N(0,I)","true factor path","VAE A path","VAE B path","pixel blend"]
print("comparison.png: строки",ROW_NAMES,"; t",t_values[:,0].tolist(),"; test pair",PAIR)
NEAR_MEAN={mode:[seed for seed in SEEDS if PER_SEED[mode][str(seed)]["recon"]<=MEAN_PSNR+1] for mode in "AB"}
print("Реконструкция в пределах 1 дБ от средней картинки (диагностика, не доказательство схлопывания):",NEAR_MEAN)
TOTAL=time.perf_counter()-T_START
results=dict(lab="Генерация и интерполяция в латентном пространстве",student="Котов Дэвид Арсенович",variant=VARIANT,
             kind=KIND,factor=FACTOR,A=a_cfg,B=b_cfg,diff=DIFF,seeds=SEEDS,data_seed=7,data_sha256=DATA_SHA,
             environment=ENV,libraries=LIBS,train_seconds=TRAIN_SEC,per_seed=PER_SEED,summary=ROWS,tolerance=TOL,
             classes=CLASSES,sensitivity=SENS,paired_difference_diagnostics=PAIRED,diagnostics=DIAG,
             factor_names=["amber_x","amber_y","pink_x","pink_y"],mean_image_psnr=MEAN_PSNR,
             ae_sampling=AE_SAMPLES,interpolation_geometry=INTERP_SHAPE,model_tensor_sha256=MODEL_SHA,
             comparison=dict(training_seed=101,sample_seed=5,pair=PAIR,t=t_values[:,0].tolist(),row_names=ROW_NAMES,
                             geometry_each_step=VIS_SHAPE,sampling_note="For display B uses first two coordinates of A noise; metrics use original V.metrics sampling."),
             near_mean_psnr_seeds=NEAR_MEAN,total_seconds=TOTAL,new_session_checked=False,
             tensor_hash_definition="SHA-256 concatenated contiguous CPU tensor bytes in state_dict order")
(ART/"results_v27.json").write_text(json.dumps(results,ensure_ascii=False,indent=2,allow_nan=False),encoding="utf-8")
manifest=dict(variant=VARIANT,model_revision=LIBS,model_tensor_sha256=MODEL_SHA,configs={"A":a_cfg,"B":b_cfg},
              data_seed=7,data_sha256=DATA_SHA,training_seeds=SEEDS,environment=ENV,
              files={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                     for p in sorted(ART.iterdir()) if p.name in ("comparison.png","results_v27.json")})
(ART/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2,allow_nan=False),encoding="utf-8")
print("ГОТОВО: LR08/artifacts/engee/results_v27.json; comparison.png; manifest.json")
print("Полная длительность, мин:",round(TOTAL/60,2))
for filename in ("results_v27.json","comparison.png","manifest.json"):
    print(filename,hashlib.sha256((ART/filename).read_bytes()).hexdigest())
