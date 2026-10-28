# ЛР №2. Карточка модели, лицензии, происхождение данных и анализ рисков

**Котов Дэвид Арсенович · вариант 27 · выполнена**

[Отчёт DOCX](Котов_Дэвид_Арсенович_Вариант_27_ЛР_2.docx) · [журнал](reports/journal.md)

Сценарий — электронный каталог фотоархива, публикация оригиналов без коммерческого использования. Профиль — NoDerivatives. Политика: `commercial_use=false`, `redistribution=true`, `derivatives=false`, `share_alike_acceptable=false`.

## План и результаты

1. Создать 12 синтетических записей и до аудита записать ожидания — выполнено.
2. Провести аудит и принять решения — **0 ошибок, 1 предупреждение R9**. Item09 в карантине из-за совпадения суммы с item06 при разных сведениях о правах; 11 учебных кандидатов.
3. Заполнить паспорт данных и карточку генератора ЛР 1 — **7 и 9 разделов**, пустых нет.
4. Описать риски — **6 рисков, 5 категорий**, включая Data Privacy и Intellectual Property; `RESULT: PASS`. Контрольная ошибка категории отклонена.
5. Оформить DOCX и проверить комплект — выполнено. PDF экспортируется вручную.

Три ND-объекта (item07, item08, item11) не конфликтуют с публикацией оригиналов. При диагностическом включении производных правило R4 даёт три ошибки.

## Как повторить

Из корня репозитория, Python 3.10+, сторонние пакеты не нужны:

```powershell
python LR02/src/lab02_make_variant.py --variant 27 --out LR02/artifacts/v27
python LR02/src/lab02_audit.py --manifest LR02/artifacts/v27/manifest.csv --policy LR02/artifacts/v27/policy.json --out LR02/artifacts/v27
python LR02/src/lab02_model_card.py --passport LR01/artifacts/fresh_run/v27_n5/passport.json --out LR02/artifacts/model_card_before_decisions.md
python LR02/src/lab02_risks.py --csv LR02/artifacts/risk_register_broken.csv --out LR02/artifacts/risk_ranking_broken.md
python LR02/src/lab02_risks.py --csv LR02/artifacts/risk_register.csv --out LR02/artifacts/risk_ranking.md
```

Проверка сломанного реестра ожидаемо завершается кодом 1, основного — кодом 0. Аудит перезаписывает заготовки: после повторения нужно снова перенести решение по item09 из журнала в таблицу аудита. Итоговый паспорт и карточка дополнены вручную и сохраняются отдельно от заготовок.

## Что где лежит

| Путь | Содержимое |
| --- | --- |
| [reports/passport.md](reports/passport.md) | паспорт данных, 7 разделов |
| [artifacts/model_card.md](artifacts/model_card.md) | карточка генератора, 9 разделов |
| [artifacts/model_card_before_decisions.md](artifacts/model_card_before_decisions.md) | карточка до уточнения пробелов |
| [artifacts/risk_register.csv](artifacts/risk_register.csv), [risk_ranking.md](artifacts/risk_ranking.md) | риски и ранжирование |
| [artifacts/risk_register_broken.csv](artifacts/risk_register_broken.csv), [risk_ranking_broken.md](artifacts/risk_ranking_broken.md) | контрольная ошибка |
| [artifacts/v27/](artifacts/v27) | исходные данные и аудит с решением |
| [reports/journal.md](reports/journal.md) | ожидания, ход работы, решения и источники |
| [reports/error_demo.log](reports/error_demo.log) | фактические команды, FAIL и PASS |
| [reports/report_data.json](reports/report_data.json) | среда, хеши, самопроверка, решения и дополнительные проверки |
| [assignment/](assignment) | выданные материалы |
| [src/](src) | пять неизменённых скриптов преподавателя |

Структура повторяет [образец LR02](https://github.com/ykvnkm/ai-in-creative-industries/tree/main/LR02); паспорт расположен в `reports/passport.md` по правилам этого проекта. Данные вымышлены, медиафайлов нет; суммы в исходном CSV вычислены из строк. Методические материалы и выданные скрипты не покрываются MIT собственного кода.
