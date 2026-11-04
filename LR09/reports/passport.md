# Паспорт эксперимента — ЛР №9, вариант 27

| Поле | Значение |
| --- | --- |
| Работа / вариант | Промпт-инжиниринг / 27, контекст 5, элемент 3 — palette |
| Дата части 1 | 04.11.2026; среда записана 13:05:01 UTC / 16:05:01 МСК |
| Запрос A | electronic music cover art |
| Запрос B | electronic music cover art, iridescent purple and cyan colors |
| Текст-цель | iridescent purple and cyan colors |
| SD Turbo | stabilityai/sd-turbo @ b261bac6fd2cf515557d5d0707481eafa0485ec2 |
| CLIP | openai/clip-vit-large-patch14 @ 32bd64288804d66eefd0ccbe215aa642df71cc41 |
| Генерация | 512×512, 1 шаг, guidance=0, EulerDiscreteScheduler, CPU-генератор, float32, seed 101–105 |
| Среда | Engee 26.10.2-H2, Julia 1.12.6, Python 3.11.11, torch 2.4.1+cpu |
| Пакеты | diffusers 0.32.2; transformers 4.57.6; numpy 2.1.3; scipy 1.15.2; Pillow 11.1.0; huggingface_hub 0.36.2 |
| Ресурсы | Intel Xeon Platinum 8180; 4 потока torch, видны 112 ядер; CUDA=False; пик RSS 7,81 ГиБ |
| Длительность | Загрузка SD Turbo 64,33 с, CLIP 23,13 с; серия 223,88 с; изображение около 18,3 с |
| Метрики | CLIP: косинус ×100, не CLIPScore; границы: средний модуль Собеля яркости /8; контраст: std яркости 0,299R+0,587G+0,114B |
| Статистика | n=5, s базы ddof=1, Δ=B−A, учебное правило \|Δ\|>2s |
| Допуски | CLIP ±1 пункт; границы и контраст ±10 %; запись 03.11.2026 11:20:27 UTC |
| Часть 1 | CLIP цели +11,085209; предмета +2,613838; границы −23,354229 %; контраст +13,106051 % |
| Повтор | Seed 101 совпал по RGB в A и B; новый сеанс не проверялся |
| Часть 2 | DeepSeek (веб), автовыбор; DeepThink=False, поиск=False; точная версия модели не установлена |
| Чат-сеансы | 04.11.2026, приблизительно 13:22–13:32 UTC; 3 приёма ×3 новых чата; точных времён по ответам нет |
| Оценка | K1–K3 по всем 45 объектам; K4 — 30 попарных сравнений style/composition для каждого приёма; все 3 повтора каждого приёма разобраны |
| K1–K4 zero | 0,8667 / 1 / 0,8667 / 0,8667 |
| K1–K4 few | 0,9333 / 1 / 0,9333 / 0,7333 |
| K1–K4 step | 1 / 1 / 1 / 0,7667 |
| Ошибки | avoid=[yellow] в ctx5_zero_r1, zero_r2 и few_r1; исходные ответы не менялись |
| Материалы | LR09/artifacts/engee/, prompts/, answers/, reports/ |

Проверены 13 записей общего манифеста и 10 записей манифеста изображений. RGB-хеши всех десяти PNG совпали; контраст и Собель независимо пересчитаны с точностью до 10⁻¹². Средние, s и Δ пересчитаны по исходным значениям. K1–K4 и SHA девяти ответов повторно проверены учебными функциями. Все пять ячеек Engee имеют сохранённый вывод; основной расчёт завершён без исключений. Предупреждения accelerate и API не прервали работу. Исходные JSON, ответы и выводы не редактировались.

Один контекст, пять seed и один сеанс генерации; CLIP измеряет соответствие тексту, а не эстетику или достоверность металла. K2 — эвристика подстрок, K3 — точность формального avoid, K4 — только style и composition. Сервис DeepSeek выбирает модель автоматически, точная версия не зафиксирована. Девять новых чатов не делают 30 попарных совпадений независимой выборкой. Результаты относятся к указанным дате, режиму и запросам.

Входы — синтетические описания и запросы без персональных данных и закрытых материалов. Учебные файлы не включены в MIT собственного кода. SD Turbo используется по закреплённой Stability AI Community License; веса не размещены в репозитории. У кода CLIP MIT, отдельное поле лицензии весов в закреплённой карточке не указано. Условия DeepSeek относятся к использованному сервису, а не к лицензии локального кода. Powered by Stability AI.

Источники условий: [SD Turbo](https://huggingface.co/stabilityai/sd-turbo/blob/b261bac6fd2cf515557d5d0707481eafa0485ec2/LICENSE.md), [CLIP](https://github.com/openai/CLIP/blob/main/LICENSE), [DeepSeek Terms](https://cdn.deepseek.com/policies/en-US/deepseek-terms-of-use.html), [DeepSeek Privacy](https://cdn.deepseek.com/policies/en-US/deepseek-privacy-policy.html).

## Контрольные суммы

| Файл | SHA-256 |
| --- | --- |
| LR09/artifacts/engee/comparison.png | `99384f87105ada67df88dc7268ad116bd5ed2f8f2a437a666ae8cff084b34f37` |
| LR09/artifacts/engee/err_v27.txt | `86d66096fa5fa171fe9d7d44392b4a7dda7ae511ef4549573257d648491f540b` |
| LR09/artifacts/engee/LR09_27.ngscript | `1b23109498e2dc404fc1ab473cdd8729144ad14bdfbc7d94565ac6c66f7f41b8` |
| LR09/artifacts/engee/manifest.json | `d2a7e8396dd91fa0827b7fcb73f840e653fa7afffaaacfa4341ed62bad9439a3` |
| LR09/artifacts/engee/out_v27.txt | `b58c22ec1b70634b6088768ffbe3597bcd95f3de36cc91eb0b5a1678d05e5ec1` |
| LR09/artifacts/engee/pip_install.log | `97e550d096a4c6a7bf066c750652a581a0742ea418a1fa75388b1d5eff33bc6a` |
| LR09/artifacts/engee/results_v27.json | `ebc94657e92f4e3d0022462d946f7cbd5fa6caa41dd5c0e0c67e73383d5ece84` |
| LR09/artifacts/engee/SHA256SUMS | `c12634e82d547aeec57f26d6b7cf70c4ca0e853a68a920f57d975a18a8d9e754` |
| LR09/artifacts/engee/v27/A_s101.png | `300c9efa5e80bcd6540bebb80ab484277d8dc1abdbc4371270ba0dbbf28e8039` |
| LR09/artifacts/engee/v27/A_s102.png | `409bf5bfdee4306f6d673393386ff35797c8fd878771d85843508cc736c53158` |
| LR09/artifacts/engee/v27/A_s103.png | `e46200f9e4ee5139a59453fd24f3dfa4279ce416e8106df2d7333dcf3d8b38c4` |
| LR09/artifacts/engee/v27/A_s104.png | `7cf12c5692e52e58061f3be50b7a22ed3ad8d5c836156824ae951882f626179f` |
| LR09/artifacts/engee/v27/A_s105.png | `d94eaaf35dbee7eac81d4da008ad9ef0d1a1066b33d3cc4169bf46219a8e910b` |
| LR09/artifacts/engee/v27/B_s101.png | `a5fe720496511d6f600cc17025c2acd0a339a74cf5661cc24dab5ae7a43bd9fe` |
| LR09/artifacts/engee/v27/B_s102.png | `b9125f5cc8fb26f1ddc6ff068205bd4191aadf8811f19d7e6be9ce876895d137` |
| LR09/artifacts/engee/v27/B_s103.png | `10473eb9a05af3a5c3f0d4e0675dd0ef0bcdc3e5c8e230f2ba590f1fa4fa39dc` |
| LR09/artifacts/engee/v27/B_s104.png | `c03ca3d98a7a4326c054b15a5726b91e83b78d72023e81e146b9e9f8046d5cb6` |
| LR09/artifacts/engee/v27/B_s105.png | `62ab21d4d19685cdbadac93f13e8aa1a285373a79591d0025a718e7ceed9fbba` |
| LR09/artifacts/engee/v27/manifest.json | `ffb71da6a9547cae39769a7a6f788db5aeda914e45f34fa18f53a95aacc40f37` |
| LR09/answers/ctx5_few_r1.txt | `69f1b6dd02b34a37d12108bc6c11cc2e669fc36ca664315dd1f2d1be16d93483` |
| LR09/answers/ctx5_few_r2.txt | `07185fcb54d4a6e444dc425954c97dc5f2c70e7d8069f880c2ff71994197425a` |
| LR09/answers/ctx5_few_r3.txt | `6c3fb8b7508de6a2d05a02d605e6e51143a39074ff836c1c4f8ccad0ac2affb0` |
| LR09/answers/ctx5_step_r1.txt | `9db57c6af32cd0b5b7fc3d95229a28090876f310e61f57bd7695c757b10cfe42` |
| LR09/answers/ctx5_step_r2.txt | `74b429ec76f548d0214483e29ff4bebebfb47f35dab55c6b069fb586201c0c8c` |
| LR09/answers/ctx5_step_r3.txt | `ad0b45ca8cd85492bc346058e60376ee9f7cf8eda27228a49e50f990f03898af` |
| LR09/answers/ctx5_zero_r1.txt | `da78a01fb215e7d9e9364b95e15533222c7e151d099bdc2102d4e1e672030ff8` |
| LR09/answers/ctx5_zero_r2.txt | `876d7b9b703cd8314043308780dc55b8664376b2fde1a5e0005045a516c3d1cb` |
| LR09/answers/ctx5_zero_r3.txt | `6bc74348f682fb9e7fb545b8cbcfa4bda01fe6fb93dab016e6193f1f90a02786` |
| LR09/prompts/ctx5_few.txt | `8423aeb8015a58169a14476633f7d78c2720569a67c2c0cddd8e81e34d9d4c29` |
| LR09/prompts/ctx5_step.txt | `5932ab40433aaef0ed109ffbc2245fd4a875b830c7388aeb52cc8bb0c216d79b` |
| LR09/prompts/ctx5_zero.txt | `9d8cd28b77491b0d542bdb767a7b9ad74290d1c753a00b086c166d52531f3c9a` |
| LR09/src/lr09_part2_score.py | `b0da1feeb1a6a9faca07b5b717f96be86077b537072eaa323c085473f12aac04` |
| LR09/src/LR09_variant27.jl | `5fb2efa81b64349116f81c18f79eba9d09bce84a080795859c4399a1f6e96e77` |
| LR09/src/lr09_variant27.py | `99550fecb6460126cbab682df65e49ba276e59af2f56c9de2d6f4d9bf6cd9118` |
| LR09/assignment/src/demo9_llm.py | `0dd037fa4f43803d0ae30be56e56be173bc0189b5438b1a0d2b419e77ede9f22` |
| LR09/assignment/src/lab09_lib.py | `cc4d233de574e47a73d2126234ee0b8e9f5d80aa0ed6d4a2fac9748ac0f7b062` |
| LR09/assignment/src/lab09_llm.py | `5eabb31fd8ba76f103020177acfb04cdb2127352cbddf22e67f2c0b4835abcb5` |
| LR09/assignment/src/run_lr09.py | `a962a37b7cd06caab3b837f37a97ea8d8500271cc528b127844ca127696d2507` |
| LR09/assignment/src/summarize9.py | `482d9666607bfad960ce2a2099324057d3851613d13c2eba1c6c9ba6d94bbd15` |
| LR09/reports/figures/Engee_screenshot_1.png | `4e7fd6cb355a86fb324a441522c36ae6eb72ef3e946978ba7404dc7d585ff7b8` |
| LR09/reports/k1k4.json | `e3365c3f15b5ef71d02dc4af2451c87d3c215d76e8d602ceba737544e80baaca` |
