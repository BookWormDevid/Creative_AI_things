# Паспорт эксперимента — ЛР №6, вариант 27

| Поле | Значение |
| --- | --- |
| Работа | Исследование параметров text-to-image генерации |
| Дата | 02.11.2026; results.json сохранён 16:57:44.893352 UTC / 19:57:44 МСК |
| Вариант | 27 = (бриф 5 − 1) · 6 + фактор 3 |
| Бриф | cover art for an electronic music release, brushed metal surface with iridescent reflections, macro photography style, strong contrast, no text, no logo, no people |
| Модель генерации | stabilityai/sd-turbo; ревизия b261bac6fd2cf515557d5d0707481eafa0485ec2 |
| Модель метрики | openai/clip-vit-base-patch32; ревизия 3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268 |
| Фактор A → B | size 512×512 → 768×768; остальные поля конфигурации совпадают |
| Серия | 101, 102, 103, 104, 105; n=5 |
| Генерация | 1 шаг, guidance_scale=0,0, свежий CPU-генератор, GPU cuda:0, torch.float16; веса fp16, safetensors |
| Среда | Google Colab, Tesla T4, 14,6 ГиБ |
| Платформа / Python | Linux-6.6.159+-x86_64-with-glibc2.39 / 3.13.16 |
| torch / CUDA / cuDNN / драйвер | 2.11.0+cu130 / 13.0 / 92700 / 580.82.07 |
| Пакеты | diffusers 0.40.0; transformers 5.16.1; Pillow 11.3.0; numpy 2.1.3; scipy 1.16.3; accelerate 1.15.0; safetensors 0.8.0 |
| CLIP | косинусное сходство ×100 с исходным английским брифом, не CLIPScore; модель метрики на cuda:0 |
| Энергия границ | средний модуль градиента яркости Собеля, нормировка 1/8 |
| Контраст | std яркости RGB→0,299R+0,587G+0,114B на шкале 0–1 |
| Время | вызов генерации после прогрева обоих режимов, без загрузки моделей |
| Статистика | Δ=B−A, s — выборочное стандартное отклонение базы A, ddof=1; учебное правило \|Δ\|>2s |
| Допуски | CLIP ±1,0; границы и контраст ±10 % от A; время ±20 %; запись до запуска 02.11.2026 16:39:34 UTC |
| Классификация | CLIP выше/время ниже — улучшение за допуском; отклонение границ/контраста — ухудшение близости к базе; равенство порогу нейтрально |
| Результат CLIP | 27,634311 → 28,058827; Δ=+0,424516; в допуске, 2s не превышен |
| Результат границ | 0,035323 → 0,030544; −13,527811 %; вне допуска, 2s не превышен |
| Результат контраста | 0,134517 → 0,107662; −19,963718 %; вне допуска, 2s не превышен |
| Результат времени | 0,307027 → 0,659328 с; +114,745700 %; вне допуска, 2s превышен |
| Контроль масштаба | границы −1,085 % на 512 и +3,789 % на 768; контраст ниже на 20–21 % |
| Повтор | seed 101 в A и B совпал с серией по SHA; новый сеанс не проверен |
| Guidance | 0 и 1: SHA равны, CFG выключен; 3: CFG включён, PSNR 10,61 дБ на брифе 5 |
| Демонстрационный вариант | выводы по 2s и допускам совпали по четырём метрикам; средние трёх метрик без времени близки к методике, не все статистики идентичны |
| Визуально | радужная штриховая фактура главная во всех кадрах; металл неоднозначен; новые разрывы исключительно у 768 не выявлены |
| Время работы | загрузка SD Turbo 16,6 с, CLIP 12,8 с; серия около 13,4 с; блокнот около 2,6 мин |
| Ограничения | одна модель, бриф, GPU и сеанс; n=5, фиксированный порядок A/B; метрики не оценивают эстетику |
| Артефакты | LR06/artifacts/: results.json, два листа, 10 исходных PNG и манифесты, SHA256SUMS |

Лицензии и источники: SD Turbo — [закреплённый LICENSE.md](https://huggingface.co/stabilityai/sd-turbo/blob/b261bac6fd2cf515557d5d0707481eafa0485ec2/LICENSE.md), учебное некоммерческое использование и AUP. У [официальной реализации CLIP](https://github.com/openai/CLIP/blob/main/LICENSE) — MIT; отдельная лицензия весов в [карточке снимка](https://huggingface.co/openai/clip-vit-base-patch32/blob/3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268/README.md) явно не задана. Веса в репозитории работы не размещены. Powered by Stability AI.

Все 23 записи SHA256SUMS проверены. Контраст и границы независимо пересчитаны по исходным PNG с точностью до 10⁻¹²; CLIP и GPU-время повторно локально не измерялись. Выводы кодовых ячеек сохранены; визуальная оценка и итог добавлены после просмотра файлов.

**Контрольные суммы сохранённых материалов:**

| Файл | SHA-256 |
| --- | --- |
| LR06/Котов_Дэвид_Арсенович_Вариант_27_ЛР_6.ipynb | `e6667af86a60a05c500c44771e44f87c3a1048a07dfa0e931b4957528f9095e4` |
| LR06/src/lab05_lib.py | `4eb176506585ffcda1702605a767309fb451808229c3622f80ce882b7fa2ce1a` |
| LR06/src/lab06_lib.py | `c6d8473cf5a3000f4c27fbdef57916c2fbce347db272928d5c4729472f748bd8` |
| LR06/src/lab06_demo.py | `6bd455ea028a475f6d21593b6f969446b676a3627ab496fd7f125394361edf4a` |
| LR06/artifacts/comparison.png | `93b4a1ff1c1dc1420edc7bedab21b82ed31229bced6aeac247f7d37558da077e` |
| LR06/artifacts/results.json | `e5a418cdd317951b599478fdb40cc96b08d0ff56d3621e05d1147b59a2ae92d0` |
| LR06/artifacts/series/A_seed101/manifest.json | `6c74ee359ce57827d84ff0b1ba0a2aa246b04c9566df786307a2df9314cbd219` |
| LR06/artifacts/series/A_seed101/result.png | `d41f2c83f6c305e8714b7ae13f0047274218a407ff375c2916092a5059c0f614` |
| LR06/artifacts/series/A_seed102/manifest.json | `1d5d2f4298abad824b90f6bd9bbc758a3e66144e41ba71e964b5872aa062d33e` |
| LR06/artifacts/series/A_seed102/result.png | `0dd89d0891241593b29f789cca374840534eeecf633791d3bdc1b94831f906a0` |
| LR06/artifacts/series/A_seed103/manifest.json | `d1ad508e58676d51d2e8928de9cb413cfd756eb38debab0a2fdca3ea73079f97` |
| LR06/artifacts/series/A_seed103/result.png | `7a3e3832fee45d0f5c4426c740a8a3b0a48a9c2b856c0c4fcb84c6f2600496d6` |
| LR06/artifacts/series/A_seed104/manifest.json | `d7d0474720370c9c4ae1f61c9aab9ba371644f14c76ceb3f544364c1227c4897` |
| LR06/artifacts/series/A_seed104/result.png | `2953a430c9704890291713c7950360591434eac3ca4647a77535c3e3afa54de4` |
| LR06/artifacts/series/A_seed105/manifest.json | `77257ef247f996ce6db10b57ca1c66c14870762a0018add5c0a8ca6943a63be9` |
| LR06/artifacts/series/A_seed105/result.png | `391cd5b78473ffa5a52f36cb3949bbb4cbe221d8c5e2d11bceb28c60a4ffbd63` |
| LR06/artifacts/series/B_seed101/manifest.json | `0dd9340354c0ca80e6ac3b6051e277569603d62942405dfa9df02afd5404ccdb` |
| LR06/artifacts/series/B_seed101/result.png | `dd073dfc424b5d8b069fe1cb2b73541c7bcda6d87fbc6d8f77956a6154d1ffee` |
| LR06/artifacts/series/B_seed102/manifest.json | `58b7c38f13ac17e547dcbb3f8f6c6368015c519b7389022cb0074548dfa086f3` |
| LR06/artifacts/series/B_seed102/result.png | `a29ed70be528ba09b4ad8d8a7b26bce673199ce14376a9e2e7b95ad8bb31ec5d` |
| LR06/artifacts/series/B_seed103/manifest.json | `23d29b2bd31a1863229505f3304b0be59ae69a71154472b616910fbe5f39fd01` |
| LR06/artifacts/series/B_seed103/result.png | `f7aca1f0e1fae781f7d4baa2f69889dea48797a65c693a11e9e9238aa2dd233a` |
| LR06/artifacts/series/B_seed104/manifest.json | `d9bf764f913481eb7fe1976ef2fd0bc85b2fb638c1503afb7d1fad6920fcaa30` |
| LR06/artifacts/series/B_seed104/result.png | `1611ef79f4602ecdb95064d2ffabd9389f4d7d72b4e5d6d2e1fcf0a88f6293a6` |
| LR06/artifacts/series/B_seed105/manifest.json | `96482403bdcec16c994f58b7b5b7baa530b8c0779515cd52b8bdb2b46249357b` |
| LR06/artifacts/series/B_seed105/result.png | `2214fdcb71b5411a94b805f1ded5451727bc177c32bbea4d48a7c7e42828897d` |
| LR06/artifacts/series_seeds.png | `e0f62b90147ff1dc23faf93feb4a18d03091208e57b4444e71a0370e31e0420d` |
| LR06/artifacts/SHA256SUMS | `47b61a317aefb76a16727889ddfcdde64cfbd51180f718addbb311d295c0f722` |
