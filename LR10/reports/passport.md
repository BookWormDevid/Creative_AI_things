# Паспорт эксперимента — ЛР №10, вариант 27

| Поле | Значение |
| --- | --- |
| Работа | Сравнительное исследование моделей text-to-image |
| Вариант | 27, бриф 5, пара 3 |
| Дата | 04.11.2026; гипотезы 13:50:10 UTC, среда 14:02:00 UTC |
| Бриф | cover art for an electronic music release, brushed metal surface with iridescent reflections, macro photography style, strong contrast, no text, no logo, no people |
| A | stabilityai/sd-turbo @ b261bac6fd2cf515557d5d0707481eafa0485ec2 |
| Режим A | 512×512, 1 шаг, guidance=0, EulerDiscreteScheduler |
| B | amused/amused-256 @ 09b6259bf96dbe6d70a852b70812420fe02df55e |
| Режим B | 256×256, 12 шагов, guidance=10, AmusedScheduler; маскированные токены, не диффузия |
| CLIP | openai/clip-vit-large-patch14 @ 32bd64288804d66eefd0ccbe215aa642df71cc41; safetensors |
| Seed / вычисления | 101–105; свежий CPU-генератор; CPU float32; модели загружены по очереди |
| Площадка | Engee 26.10.2-H2; Julia 1.12.6; Python 3.11.11 |
| Пакеты | torch 2.4.1+cpu; diffusers 0.32.2; transformers 4.57.6; numpy 2.1.3; scipy 1.15.2; Pillow 11.1.0; huggingface_hub 0.36.2 |
| Ресурсы | Intel Xeon Platinum 8180; 4 потока torch, видны 112 ядер; CUDA=False; ОЗУ 16 ГБ в интерфейсе; пик RSS 7,82 ГиБ |
| Время | Загрузка A/B: 16,95/58,79 с; variant_summary 441,53 с; генерация A/B: 18,484/37,223 с |
| Определения | CLIP — косинус ×100 по исходному размеру, не CLIPScore; edge/contrast — RGB→256×256 (Pillow BICUBIC), яркость 0,299R+0,587G+0,114B, средний Собель /8 и std |
| Статистика | n=5, s(A) с ddof=1; Δ=B−A; учебный признак \|Δ\|>2s, не формальный тест |
| Допуски | CLIP ±1 пункт; edge/contrast ±10 % от A; время B/A внутри [2/3; 1,5], границы нейтральны |
| Результат | CLIP брифа +2,381; пробы текста +0,945; edge −20,87 %; contrast +147,81 %; время ×2,014 |
| Классификация | clip_brief/edge — только допуск; clip_text — ни один порог; contrast/seconds — оба порога |
| Слепые листы | JPEG quality=90, обе стороны 384×384, промежуток 12 px; порядок из blind_key.json |
| Оценка / ключ | 14:45 / 14:49 UTC; пять выборов aMUSEd-256; p(5:0)=0,0625>0,05 |
| Ограничение оценки | Модели узнавались по виду; один оценщик; время и порядок подтверждены автором, отдельного снимка первичной записи нет |
| Повтор | Повтор генерации и новый сеанс не проверялись; повтор служебных ячеек использовал готовый JSON |
| Артефакты | LR10/artifacts/engee/; исходные PNG, JPEG, слепые листы, ключ, JSON, манифесты, выводы и выполненный ngscript |

Проверены 25 записей манифеста изображений и 2 записи общего манифеста; ключ, добавленный после оценки, отдельно включён в SHA256SUMS. Размеры и RGB-хеши десяти PNG совпали. Контраст и Собель независимо пересчитаны по пикселям: максимальное расхождение 2,78·10⁻¹⁷. Средние, s, Δ и классификации совпали с исходным JSON. Все четыре ячейки содержат вывод, исключений основного расчёта нет. CLIP и время заново не измерялись; первичные JSON, stdout/stderr и ngscript не редактировались.

Для этого брифа aMUSEd-256 предпочтительнее по передаче отражающего металла: она выбрана в пяти парах из пяти. Средний clip_brief выше на 2,381, но ниже порога 2s. Цена — вдвое более долгая генерация на CPU, меньший исходный размер, предметный уход и риск буквоподобных знаков. Для конвейера с приоритетом этого материала B — кандидат после проверки и удаления таких дефектов; A быстрее, но здесь даёт преимущественно абстрактные волны. Ни метрика, ни пять визуальных выборов не доказывают общего превосходства. Повтор в новом сеансе не проверен.

SD Turbo используется по Stability AI Community License закреплённой ревизии; в карточке aMUSEd-256 указана OpenRAIL++. У кода CLIP лицензия MIT; отдельное поле лицензии весов в закреплённой карточке не указано. Условия кода и весов не смешиваются. Веса не включены в репозиторий, учебные файлы не входят в MIT собственного кода. Изображения — учебные концепты. Powered by Stability AI.

Источники условий: [SD Turbo](https://huggingface.co/stabilityai/sd-turbo/blob/b261bac6fd2cf515557d5d0707481eafa0485ec2/LICENSE.md), [aMUSEd-256](https://huggingface.co/amused/amused-256/blob/09b6259bf96dbe6d70a852b70812420fe02df55e/README.md), [код CLIP](https://github.com/openai/CLIP/blob/main/LICENSE).

## Контрольные суммы

Все файлы результатов перечислены в LR10/artifacts/engee/SHA256SUMS. Основные материалы:

| Файл | SHA-256 |
| --- | --- |
| LR10/assignment/src/lab10_lib.py | `b53293ebd2422295cfa2fd01e4dcc5f8eaef440c0802a80803d3771c19ce2f6c` |
| LR10/src/lr10_variant27.py | `2e198947a1b7d73043f85185bfac6f6147c170e03820e3eb12db981c87979619` |
| LR10/src/LR10_variant27.jl | `d5a20352ed8675b3a57e0dac30c22c9287c77ff61e4bd0de71226c7ab8ef9c70` |
| LR10/artifacts/engee/results_v27.json | `da624c3dded67b3c270e3b30e4fa2859c6b2714c09753792a6ab3bf428ab3338` |
| LR10/artifacts/engee/manifest.json | `e52593e26fa68b9684806a481fb2fcdcbf82c883a3a8bafd82b89e1344b35f74` |
| LR10/artifacts/engee/v27/manifest.json | `8c779d165cc07cb06ae1416c5880578bf81165b3087172d784f1b8ea79a2c2ba` |
| LR10/artifacts/engee/v27/blind_key.json | `e8fed723932831a83eeacf9e37c5c13e2b1c2c9c8aa06c7728e90bf6b62c8445` |
| LR10/artifacts/engee/SHA256SUMS | `2aa356c0a3aee0dabce64d55c414fee9cc1d5a037115980d67323ba0584e62ed` |
| LR10/reports/blind_eval.md | `6a5bb898fb26d92e86a72892019cf9f54133eb280d5de255bd830897f70fd683` |
| LR10/reports/journal.md | `b8981c2ab0ea7629bc9081eb132aec188040d15efc776a18587f16787e91e942` |
| LR10/reports/figures/Engee_screenshot_1.png | `3c8a1ec51ad28b59b7da257fccd75d61176e968bba67818c244295639f7aecd1` |
| LR10/Котов_Дэвид_Арсенович_Вариант_27_ЛР_10.docx | `3993506602a5f3c3bd65b2060dd193bd75e87e0d08f04677f238a8e5e285adca` |
