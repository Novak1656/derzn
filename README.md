# Древо знания
Общественно-политический проект. Создание концентрата знаний в форме дерева (графа) знаний.


**Дополнительное знание** - это знание, не являющееся основным. У такого знания поле "Категория" пусто.

**Знание**, Знание - запись в сущности "Знания", имеющая один из статусов: 
- Знание в работе 
- Завершенное Знание 
- Архивное предЗнание 
- Знание на редактировании 
- Опубликованное Знание

**Категория**, Категория - запись в сущности "Категории", имеющая один из статусов: 
- Создана категория 
- - Категория опубликована

**Метка**, Метка - запись в сущности "Метки", у которой реквизит "Метка" = True.

**Основное знание**, Основное знание - это знание, непосредственно связанное с категорией. У такого знания поле "Категория" не пусто!

**ПредЗнание**, Предзнание - запись в сущности "Знания", имеющая один из статусов: 
- ПредЗнание в работе 
- Завершенное предЗнание 
- Экспертиза предЗнания 
- Архивное предЗнание

**ПредКатегория**, ПредКатегория - запись в сущности "Категории", имеющая статус "Создана ПредКатегория"

**ПредМетка**, ПредМетка - запись в сущности "Метки", у которой реквизит "Метка" = False

**ПредСвязь**, ПредСвязь - запись в сущности "Связи", имеющая один из статусов: 
- ПредСвязь в работе 
- Завершенная предСвязь 
- Экспертиза предСвязи 
- Архивная предСвязь

**Связь**, Связь - запись в сущности "Связи", имеющая один из статусов: 
- Связь в работе 
- Завершенная связь 
- Экспертиза связи 
- Архивная связь 
- Связь на редактировании 
- Опубликованная связь

Информация для новых разработчиков проекта: [старт разработки](https://github.com/lvb555/derzn/blob/develop/DEVELOPER_GUIDE.md)