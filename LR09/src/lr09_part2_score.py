# ЛР №9, вариант 27, часть 2. Проверка девяти ответов контекста 5.
# Функции учебной lab09_llm.py используются без изменения.
import argparse, hashlib, json, math, sys
from datetime import datetime, timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument("--root",type=Path,default=HERE.parent if HERE.name=="src" else HERE)
args=parser.parse_args();ROOT=args.root.resolve()
for path in [HERE,ROOT,ROOT/"assignment"/"src"]:
    sys.path.insert(0,str(path))
import lab09_llm as L
CTX=5
APPROACHES=("zero","few","step")
paths={a:[ROOT/"answers"/f"ctx{CTX}_{a}_r{i}.txt" for i in (1,2,3)] for a in APPROACHES}
missing=[p.relative_to(ROOT).as_posix() for group in paths.values() for p in group if not p.is_file()]
if missing:
    print("Нужны все девять ответов. Отсутствуют:",*missing,sep="\n",file=sys.stderr)
    raise SystemExit(2)
results={};complete=True
for a,files in paths.items():
    scored=[L.score_file(str(p),CTX) for p in files]
    parsed=[L.extract_array(p.read_text(encoding="utf-8"))[0] for p in files]
    eligible=[i for i,arr in enumerate(parsed) if isinstance(arr,list) and len(arr)==5 and all(isinstance(o,dict) for o in arr)]
    valid_paths=[str(files[i]) for i in eligible]
    k4=L.stability(valid_paths) if len(valid_paths)>=2 else None
    row=dict(k1=sum(v["k1"] for v in scored)/3,k2=sum(v["k2"] for v in scored)/3,k3=sum(v["k3"] for v in scored)/3,
             k4=k4,k4_valid_repeats=len(eligible),k4_complete=len(eligible)==3,
             each=[dict(file=(Path("LR09")/p.relative_to(ROOT)).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),**v)
                   for p,v in zip(files,scored)])
    row["choices"]={field:[[o.get(field) for o in parsed[i]] for i in eligible] for field in ("style","composition")}
    for field in ("style","composition"):
        same=total=0
        for p,i in enumerate(eligible):
            for j in eligible[p+1:]:
                for k in range(5):
                    same+=parsed[i][k].get(field)==parsed[j][k].get(field);total+=1
        row["k4_"+field]=same/total if total else None
    complete=complete and row["k4_complete"]
    results[a]=row
results["_meta"]=dict(variant=27,context=CTX,scored_utc=datetime.now(timezone.utc).isoformat(),
                       expected_repeats_per_approach=3,files=9,k4_all_repeats_usable=complete,
                       checker_sha256=hashlib.sha256(Path(L.__file__).read_bytes()).hexdigest(),
                       note="K1-K3: original teacher functions; K4 below three valid repeats is explicitly partial. Chat sessions are documented separately.")
print(f"{'приём':<10} {'K1':>6} {'K2':>7} {'K3':>6} {'K4':>7} {'повторы K4':>11}")
for a in APPROACHES:
    q=results[a];v=f"{q['k4']:.3f}" if q['k4'] is not None else "н/д"
    print(f"{a:<10} {q['k1']:>6.3f} {q['k2']:>7.3f} {q['k3']:>6.3f} {v:>7} {q['k4_valid_repeats']:>11}")
    for e in q["each"]:print(Path(e["file"]).name,"K1",e["k1"],"K2",e["k2"],"K3",e["k3"],"ошибки:",e["errors"] or "нет")
if not complete:print("K4 не у всех приёмов охватывает три повтора; исходные ответы сохранены без правок.")
output=ROOT/"reports"/"k1k4.json";output.parent.mkdir(exist_ok=True)
output.write_text(json.dumps(results,ensure_ascii=False,indent=2,allow_nan=False),encoding="utf-8")
print("Сохранено: LR09/reports/k1k4.json")
