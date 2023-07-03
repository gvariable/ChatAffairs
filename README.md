# Hackday
## Crawler
### Developer Notes
#### Browser Automation
1. items: `class="mulu_item"` (item list)
2. click
3. subitems: `class="ywblxItem"` (subitem list)
   1. click: another window
   2. parse
   3. kill window
4. pagination
   1. button: `class="downPage"`
   2. click until has no clickable button

#### JavaScript Rendering
Selemium is shit, use [playwright](https://playwright.dev/python/docs/intro) instead.  
1. Much more rubost system.
2. Auto waiting for Ajax response.
3. Asynchronous io support.