На основе анализа документации Shotstack, вот оптимальная структура JSON для Reels с табличным импортом:

📋 Основная структура JSON


```json
{
  "timeline": {
    "soundtrack": {
      "src": "https://.../music.mp3",
      "effect": "fadeIn",
      "volume": 0.5
    },
    "background": "#000000",
    "tracks": [
      {
        "clips": [
          {
            "asset": {
              "type": "video",
              "src": "{{ VIDEO_URL }}",
              "trim": 0,
              "volume": 1.0
            },
            "start": 0.0,
            "length": 3.0,
            "fit": "cover",
            "transition": {
              "in": "fadeFast",
              "out": "slideLeftFast"
            },
            "effect": "zoomIn",
            "filter": "boost"
          }
        ]
      }
    ]
  },
  "output": {
    "format": "mp4",
    "resolution": "hd",
    "aspectRatio": "9:16",
    "fps": 30,
    "thumbnail": {
      "capture": 1
    }
  },
  "merge": [
    {"find": "VIDEO_URL", "replace": ""}
  ]
}

```

🎬 Популярные переходы для Reels


```
| Переход  | In                                        | Out                           | Рекомендация                    |
| -------- | ----------------------------------------- | ----------------------------- | ------------------------------- |
| Fade     | fade / fadeFast / fadeSlow                | fade / fadeFast               | Универсальный, для начала/конца |
| Slide    | slideLeft, slideRight, slideUp, slideDown | slideLeftFast, slideRightFast | Динамичные смены сцен           |
| Wipe     | wipeLeft, wipeRight                       | wipeLeftFast                  | Чёткие границы между клипами    |
| Carousel | carouselLeft, carouselRight               | carouselUpFast                | 3D-эффект вращения              |
| Shuffle  | shuffleTopRight, shuffleLeftBottom        | —                             | Карточный эффект (свежие)       |
| Reveal   | reveal, revealFast                        | revealSlow                    | Раскрытие сцены                 |
| Zoom     | zoom, zoomFast                            | zoomSlow                      | Приближение/отдаление           |

```

**Для Reels рекомендую:**

• `fadeFast` (0.5с) — между клипами 2-3 сек
• `slideLeftFast` / `slideRightFast` — динамика
• `zoom` — акцент на ключевых моментах

✨ Effects (эффекты клипов)


```
| Effect   | Описание                  |
| -------- | ------------------------- |
| zoomIn   | Плавное приближение       |
| zoomOut  | Плавное отдаление         |
| kenBurns | Панорама + зум (классика) |

```

🎨 Filters (фильтры)


```
| Filter           | Эффект                  |
| ---------------- | ----------------------- |
| boost            | Контраст + насыщенность |
| greyscale        | Ч/Б                     |
| contrast         | Повышенный контраст     |
| muted            | Приглушённые тона       |
| negative         | Инверсия                |
| darken / lighten | Яркость                 |

```
