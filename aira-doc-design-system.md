# AIRA | DOC — Design System & Layout Specification

Use this specification to generate executive operational documents with the exact same visual language.

---

## TYPOGRAPHY

- Primary: `Amazon Ember` (fallback: `Inter`, `-apple-system`, `sans-serif`)
- Project title in header: Amazon Ember Heavy (font-weight 900), 1.8rem, white
- Header label ("WHS BRAZIL"): 0.6rem, uppercase, letter-spacing 0.2em, rgba(255,255,255,0.5), weight 500
- Section pills: 0.78rem, weight 600, white
- Body text: 0.84rem, weight 400, justified, line-height 2, color #1a1a1a
- Card labels: 0.7rem, weight 700, uppercase, letter-spacing 0.04em, color #4CAF50
- KPI values: 1.6rem, weight 800, color #4CAF50
- KPI labels: 0.6rem, uppercase, letter-spacing 0.06em, color #777
- Table headers: 0.65rem, uppercase, weight 600, color #4CAF50
- Table body: 0.8rem, color #555
- Page subheader: 0.72rem, weight 200, color #999
- Page numbers: 0.7rem, color #aaa, weight 500

---

## COLOR PALETTE

| Token | Value | Usage |
|-------|-------|-------|
| green | #4CAF50 | Accents, icons, KPIs, borders, card labels |
| green-light | #edf5ee | Card backgrounds, KPI backgrounds, table headers |
| green-border | #d4e8d5 | Card borders, table borders |
| dark1 | #15181c | Header gradient start |
| dark2 | #1f2328 | Header gradient mid |
| dark3 | #2e3136 | Header gradient end |
| text | #1a1a1a | Body text |
| text-sec | #777 | Secondary text, labels |
| bg | #f2f2f2 | Page background |
| surface | #ffffff | Page/card surface |

### Badge Colors
- High/Critical: bg #fde8e8, color #c62828
- Medium: bg #fff3e0, color #e65100
- Low/Done: bg #e8f5e9, color #2e7d32
- Pending: bg #e3f2fd, color #1565c0

---

## LAYOUT STRUCTURE

### Global
- Max-width: 920px, centered
- Background: #f2f2f2
- Pages are separate containers with margin-bottom 2.5rem

### Page Container
- Background: white
- Border-radius: 24px
- Box-shadow: 0 2px 16px rgba(0,0,0,0.05)
- Min-height: 1300px (A4 proportion)
- Position: relative
- Padding-bottom: 4rem (space for footer)

---

## HEADER (Page 1 only)

- Background: linear-gradient(135deg, #15181c 0%, #1f2328 40%, #2e3136 100%)
- Padding: 1.75rem 2.5rem
- Min-height: 130px
- Flexbox: space-between, align-items center
- Border-radius: inherits from page (top corners only)

### Left side:
1. Shield icon (Asset 93.png) — 80px × 80px, border-radius 50%
2. Text block:
   - Label: "WHS BRAZIL" (specs above)
   - Title: Project name (Amazon Ember Heavy, 1.8rem, white)
   - Gap between label and title: 0

### Right side:
- Safe to Go logo (Asset 79.png) — height 16px, position relative top -6px
- Amazon logo (Asset 94.png) — height 20px
- Gap between logos: 1.5rem

---

## SUBHEADER (Pages 2+ only)

- Padding: 0.6rem 2.5rem
- Font: 0.72rem, weight 200, color #999
- Border-bottom: 1px solid #eee
- Flexbox: space-between
- Left: project name
- Right: "Rev X.X · alias" (0.65rem, color #bbb, weight 300)

---

## LINE NUMBERS

- Position: absolute, left -8px, top 2rem
- Content: numbers 1–50 separated by \A (newline)
- White-space: pre
- Font: 0.6rem, color #aaa, tabular-nums
- Width: 2rem, text-align right, padding-right 0.4rem
- Vertical separator line: 1px solid #eee at left calc(2.3rem - 8px)

---

## CONTENT AREA

- Margin-left: 4.5rem (clears line numbers)
- Margin-right: 2.5rem
- Spacing between elements: 1rem
- Spacing between sections (spacer): 2rem

---

## SECTION PILLS

- Display: inline-block
- Background: linear-gradient(135deg, #3a3a3a, #4a4a4a)
- Color: white
- Font: 0.78rem, weight 600
- Padding: 0.45rem 1.3rem
- Border-radius: 20px
- Box-shadow: 0 2px 8px rgba(0,0,0,0.1)
- Margin-bottom: 12px

---

## KPI CARDS

- Grid: 4 columns, gap 1rem
- Background: linear-gradient(145deg, #f7fcf7, #edf5ee)
- Border: 1px solid #d4e8d5
- Border-radius: 18px
- Padding: 1.25rem 1rem
- Text-align: center

---

## CONTENT CARDS (highlight cards)

- Grid: 2 columns, gap 1.5rem
- Display: flex, gap 1rem
- Background: #edf5ee
- Border: 1px solid #d4e8d5
- Border-radius: 18px
- Padding: 1.5rem
- Hover: translateY(-1px), box-shadow 0 4px 16px rgba(0,0,0,0.06)

### Card Icon:
- 34px × 34px circle
- Background: rgba(76,175,80,0.12)
- SVG: 16px, stroke #4CAF50, fill none, stroke-width 1.8

---

## TABLES

- Wrapped in .table-wrap: border-radius 18px, overflow hidden, border 1px solid #d4e8d5
- TH: background #edf5ee, color #4CAF50, padding 0.75rem 1rem
- TD: padding 0.7rem 1rem, border-top 1px solid #d4e8d5, line-height 1.6

---

## DECISION BOX

- Background: white
- Border: 2px solid #4CAF50
- Border-radius: 18px
- Padding: 1.75rem
- Paragraphs: 0.83rem, color #555, margin-bottom 0.5rem, line-height 1.8

---

## FOOTER (all pages)

- Position: absolute, bottom 0, left 0, right 0
- Padding: 1rem 2.5rem
- Border-top: 1px solid #eee
- Flexbox: space-between
- Left: page number (0.7rem, #aaa)
- Right: WHS logo (Asset 90.png), height 36px, opacity 0.4

---

## ASSETS

| File | Usage | Size |
|------|-------|------|
| Asset 90.png | WHS logo (footer, bottom-right) | height 36px, opacity 0.4 |
| Asset 79.png | Safe to Go logo (header right) | height 16px |
| Asset 93.png | WHS Shield icon (header left) | 80px circle |
| Asset 94.png | Amazon logo (header right) | height 20px |

---

## DOCUMENT SECTIONS (in order)

1. Executive Summary (KPIs + 4 cards: Problem, Impact, Recommendation, Risk)
2. Business Context (editorial text, justified)
3. Problem Statement & Investigation Logic (text + cards: Questions, Hypotheses)
4. Data & Signals (KPIs + observations)
5. Options & Decision Model (table)
6. Recommendation (editorial text with bold labels)
7. Risk Matrix (table with severity badges)
8. Next Steps (table with status badges and dates)
9. Decision Required (decision box)
10. Async Collaboration (editorial text)

---

## INTERACTIVE FEATURES (Editor mode)

- All text content: `contenteditable="true"`
- Section hover: shows action buttons (position absolute, top-right)
- "✨ Melhorar com IA" button: copies section text as prompt to clipboard
- Top bar: fixed, dark (#1a1a1a), with Save and Export PDF buttons
- Export PDF: opens clean version (hides editor UI) and triggers print
```

---

Cola isso no outro agente e ele vai ter toda a spec. Ele também vai precisar dos assets (imagens) — se quiser, sobe pelo upload do outro space também."
                }
              ],
              "meta": {
                "timestamp": 1779323270
              }
            }
          },
          "message_ids": [
            "3147b3ba-f5c9-4267-80c8-681d19c5b159",
            "eaa30ebc-82ef-4ac0-8ec3-12d764de24b6",
            "f64beced-4c05-4b96-bfe9-1c5c82474141",
            "decf3d0e-2dd6-4034-a1b5-f0d2b1677e2a"
          ],
          "total_request_count": 2,
          "number_of_cycles": 1,
          "builtin_tool_uses": 1,
          "turn_duration": {
            "secs": 24,
            "nanos": 608105434
          },
          "end_reason": "UserTurnEnd",
          "end_timestamp": "2026-05-21T00:27:50.680850853Z",
          "input_token_count": 0,
          "output_token_count": 0,
          "context_usage_percentage": 19.3789,
          "metering_usage": [
            {
              "value": 0.3353909048092869,
              "unit": "credit",
              "unitPlural": "credits"
            },
            {
              "value": 0.6142029742951908,
              "unit": "credit",
              "unitPlural": "credits"
            }
          ]
        }
      ],
      "user_turn_start_request": null,
      "last_request": null
    },
    "rts_model_state": {
      "conversation_id": "5ec170c6-e77d-4eb5-abcf-73c5f05fff9c",
      "model_info": {
        "model_id": "auto",
        "context_window_tokens": 200000
      },
      "context_usage_percentage": 19.3789
    },
    "permissions": {
      "filesystem": {
        "allowed_read_paths": [
          "/home/paulosjr/.workspace"
        ],
        "allowed_write_paths": [],
        "denied_read_paths": [],
        "denied_write_paths": []
      },
      "trusted_tools": [
        {
          "BuiltIn": "executeCmd"
        }
      ],
      "denied_tools": [],
      "allowed_commands": []
    },
    "agent_name": "chat"
  }
}