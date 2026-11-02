# ЛР №2. Карточка модели, лицензии, происхождение данных и анализ рисков

**Котов Дэвид Арсенович · вариант 27 · выполнена**

[Отчёт DOCX](Котов_Дэвид_Арсенович_Вариант_27_ЛР_2.docx) · [журнал](reports/journal.md)

Сценарий — электронный каталог фотоархива, публикация оригиналов без коммерческого использования. Профиль — NoDerivatives. Политика: `commercial_use=false`, `redistribution=true`, `derivatives=false`, `share_alike_acceptable=false`.

## Результаты

| Проверка | Результат |
| --- | --- |
| Аудит 12 записей | 0 ошибок, 1 предупреждение R9 |
| Решение по item09 | карантин: сумма совпадает с item06, сведения о правах различаются |
| После решения | 11 учебных кандидатов, 1 запись в карантине |
| Паспорт данных | 7 заполненных разделов |
| Карточка модели | 9 заполненных разделов |
| Реестр рисков | 6 рисков, 5 категорий, RESULT: PASS |
| Контрольная ошибка | неверная категория отклонена валидатором |

Три ND-объекта (item07, item08, item11) не конфликтуют с публикацией оригиналов. При диагностическом включении производных правило R4 даёт три ошибки.

Порядок повторного выполнения — в [PLAN.md](PLAN.md).

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

Паспорт расположен в `reports/passport.md` по правилам этого проекта. Данные вымышлены, медиафайлов нет; суммы в исходном CSV вычислены из строк. Методические материалы и выданные скрипты не покрываются MIT собственного кода.
