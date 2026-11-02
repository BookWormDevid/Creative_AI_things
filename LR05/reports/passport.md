# Паспорт эксперимента — ЛР №5, вариант 27

| Поле | Значение |
| --- | --- |
| Работа | Запуск открытой модели text-to-image |
| Дата | 02.11.2026, основной манифест 16:05:59.028154 UTC / 19:05:59 МСК |
| Вариант | 27 = (бриф 5 − 1) · 6 + условие 3 |
| Площадка | Google Colab, Tesla T4, 14,6 ГиБ |
| Платформа | Linux-6.6.159+-x86_64-with-glibc2.39 |
| Python | 3.13.16 |
| torch / CUDA / cuDNN | 2.11.0+cu130 / 13.0 / 92700 |
| Драйвер NVIDIA | 580.82.07 |
| Пакеты | diffusers 0.40.0; transformers 5.16.1; Pillow 11.3.0; numpy 2.1.3; accelerate 1.15.0; safetensors 0.8.0 |
| Модель | stabilityai/sd-turbo |
| Ревизия | b261bac6fd2cf515557d5d0707481eafa0485ec2 |
| Файлы весов | fp16, safetensors |
| Конвейер / планировщик | StableDiffusionPipeline / EulerDiscreteScheduler |
| Лицензия | Stability AI Community License Agreement, 5 июля 2024 г.; учебное некоммерческое использование; применима Acceptable Use Policy |
| Запрос | cover art for an electronic music release, brushed metal surface with iridescent reflections, macro photography style, strong contrast, no text, no logo, no people |
| Seed | 1027 в A и B; прогрев 1; демонстрационная серия 20260919 |
| Условие | A — генератор CPU, B — CUDA; модель в обоих случаях cuda:0, float16 |
| Шаги / guidance / размер | 1 / 0,0 / 512×512 RGB |
| Библиотека | LR05/src/lab05_lib.py, 6447 байт, без изменений |
| Метрики | SHA-256 PNG, равенство пикселей RGB, max_abs_diff, MSE, PSNR с maxval=255 |
| Допуск | identical — равны пиксели; close — PSNR≥40 дБ; different — PSNR<40 дБ; запись до запуска 02.11.2026 15:57:52 UTC |
| SHA-256 A по выводу | `30bdc1a4b905e91934e24b2ba7830a625449149dd9eaef949a33a69557bbc51f` |
| SHA-256 B по выводу | `747691d2648d94414f966c46c2a9962e7ecdc2fefc1afa35e78d23163b90bf0e` |
| Результат | пиксели различны; максимум 231; MSE 3225,7793172200522; PSNR 13,044457078558441 дБ; different |
| Причина | начальный шум разный; готовые тензоры воспроизвели A/B; общий тензор дал одинаковые SHA при разных устройствах Generator |
| Повтор внутри сеанса | свежий генератор CPU: SHA совпал; повторно сохранённые A/B совпали со сводкой |
| Новый сеанс | не проверен |
| Намеренная ошибка | общий генератор: первое изображение равно базовому, второе отличается; PSNR 13,91 дБ |
| Демонстрационная серия | SHA 7daa342ac2719f616aac75a42b836315c54ac5491fd3e56768f541ae48a1bf52; повтор совпал; с методическими указаниями SHA различается |
| Время | загрузка 26,0 с; прогрев 4,7 с; базовая генерация 0,33 с; пара 0,77 с; блокнот около 2 минут |
| Визуальная оценка | радужная блестящая фактура главная на обоих; узнаваемость именно металла неоднозначна |
| Ограничения | один seed и бриф, один сеанс; PSNR не оценивает красоту и узнаваемость материала |

Лицензия модели: https://huggingface.co/stabilityai/sd-turbo/blob/b261bac6fd2cf515557d5d0707481eafa0485ec2/LICENSE.md. Выходные изображения отдельно оговорены в IV(c)(iii) и исключены из определения производного произведения. Powered by Stability AI.

Фактические данные взяты из сохранённых выводов блокнота. Предварительные просмотры не являются исходными PNG из манифестов; по областям пары независимо проверены PSNR и максимум различия. Все 14 сумм основного опыта проверены по SHA256SUMS; хеши PNG A/B совпадают с манифестами. PSNR и максимум различия также пересчитаны по исходным PNG. Демонстрационные файлы сохранены в LR05/artifacts/demo/run_001/.

**Контрольные суммы сохранённых материалов:**

| Файл | SHA-256 |
| --- | --- |
| LR05/Котов_Дэвид_Арсенович_Вариант_27_ЛР_5.ipynb | `f0efedfc142d9445a84c1c741dea6c8de885c7cb3b593db986905a1d7d80e70a` |
| LR05/src/lab05_lib.py | `4eb176506585ffcda1702605a767309fb451808229c3622f80ce882b7fa2ce1a` |
| LR05/src/lab05_demo.py | `53b3b13f19e6754bda1cde58ef09f1e45b1595d1c4dab2a9b02bd4d99d731ce4` |
| LR05/reports/figures/base_preview.png | `231eb47aa94b71817347c171e73d4cf98af5d670c81427fb5d0d656dd33ead53` |
| LR05/reports/figures/pair_preview.png | `a08df23ea7c49520d47c70c2ded496fa1d4c2c295f04da4bf418f7ec85b393d8` |
| LR05/artifacts/cause_check.json | `103e652a87cf8817f748600118e833813eb4ce3a9074712c735daa0452f51d9c` |
| LR05/artifacts/condition_A/manifest.json | `909c261a1f6f59d809736a5c3f450de4a7ec4b9cce414c02464a004e6ca9ff03` |
| LR05/artifacts/condition_A/result.png | `30bdc1a4b905e91934e24b2ba7830a625449149dd9eaef949a33a69557bbc51f` |
| LR05/artifacts/condition_B/manifest.json | `1837e2b5f11558e79995a1ffc18ef6179c244e8413fb8c536f5c072b145947f7` |
| LR05/artifacts/condition_B/result.png | `747691d2648d94414f966c46c2a9962e7ecdc2fefc1afa35e78d23163b90bf0e` |
| LR05/artifacts/demo/run_001/manifest.json | `00b26fa7b116cb59fab07a411547b922a61ff5c9d1e80a0154eeac2a877963d4` |
| LR05/artifacts/demo/run_001/result.png | `7daa342ac2719f616aac75a42b836315c54ac5491fd3e56768f541ae48a1bf52` |
| LR05/artifacts/error_shared_generator/result.json | `909534e0a100f5b52b20a11891e72d2a906b212a67ced712b7fdb34a778e2cce` |
| LR05/artifacts/error_shared_generator/run1.png | `30bdc1a4b905e91934e24b2ba7830a625449149dd9eaef949a33a69557bbc51f` |
| LR05/artifacts/error_shared_generator/run2.png | `aaf54fabd18ec043aa77abdb2cb67b95ef352a53f5246e3e5ea6dce66c25f3d5` |
| LR05/artifacts/pair/A_cpu_seed1027.png | `30bdc1a4b905e91934e24b2ba7830a625449149dd9eaef949a33a69557bbc51f` |
| LR05/artifacts/pair/B_cuda_seed1027.png | `747691d2648d94414f966c46c2a9962e7ecdc2fefc1afa35e78d23163b90bf0e` |
| LR05/artifacts/pair/comparison.png | `4aba611c2b6b1237ec764a77657e8615d391ce5796c68421f4aebbfd1c170292` |
| LR05/artifacts/run_001/manifest.json | `36e49bb22eb2609745157e28e7bd95f603344056ea32de88b6e853016585ebcf` |
| LR05/artifacts/run_001/result.png | `30bdc1a4b905e91934e24b2ba7830a625449149dd9eaef949a33a69557bbc51f` |
| LR05/artifacts/SHA256SUMS | `ff5b6d4ce6977d134813ae8b33e0f50a4b37ec7a36f4f2b3e91c3c6463c334aa` |
| LR05/artifacts/variant_27_summary.json | `acbfcc3c2769dea4b30e4d429cc41dd3ddb6b08a3def04cbd981622eb22dbe7c` |
