# YAMLProject — Конфигуратор учебного языка в YAML

## Описание

Этот проект реализует инструмент командной строки для учебного конфигурационного языка (вариант №13).  
Он принимает на вход текст конфигурации в учебном формате и выводит эквивалент в формате **YAML**.  

Проект поддерживает:

- Числа (`\d+`)  
- Строки через `q(...)`  
- Словари с вложенностью (`{ ключ -> значение. ... }`)  
- Объявление и вычисление констант (`имя = значение;`, `^[имя]`)  
- Синтаксическую проверку и информативные сообщения об ошибках  

---

## Примеры использования

### Пример конфигурации (input.txt)

```text
name = q(ProStrelok);
server = 222;

network -> {
    name -> ^[name].
    server -> ^[server].
    game -> {
        name -> q(WoTB).
        players -> {
            player1 -> {
                name -> q(player1).
                level -> q(one).
            }.
        }.
    }.
}.
```
### Вывод
```yaml
name: ProStrelok
server: 222
network:
  name: ProStrelok
  server: 222
  game:
    name: WoTB
    players:
      player:
        name: player1
        level: odin
```


## Запуск
```python main.py input.txt > output.yml```\
or\
```Get-Content input.txt -Raw | python main.py > output.yml```

## Запуск тестов
```python -m unittest test_parser.py```

## Примеры input.txt
### Пример 1
```
name = q(ProStrelok);
server = q(localhost);

network -> {
    name -> ^[name].
    server -> ^[server].
    game -> {
        name -> q(WoTB).
        players -> {
            player -> {
                name -> q(player1).
                level -> q(odin).
            }.
        }.
    }.
}
```
### Пример 2
```
defaultAge = 18;
defaultRole = q(User);

user -> {
    name -> q(Alex).
    age -> ^[defaultAge].
    role -> ^[defaultRole].
    preferences -> {
        theme -> q(Dark).
        notifications -> q(Enabled).
    }.
}
```
### Пример 3
```
baseDamage = 50;
baseWeight = 12;

weapon -> {
    title -> q(Sword).
    stats -> {
        damage -> ^[baseDamage].
        weight -> ^[baseWeight].
        rarity -> q(Rare).
    }.
    owner -> {
        name -> q(Player1).
        level -> 5.
    }.
}
```
