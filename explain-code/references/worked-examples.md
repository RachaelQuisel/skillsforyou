# Worked Examples

Three full-length explanations following the skill's pattern. Each one is an example you can crib from directly.

---

## Example 1: a JavaScript debounce function

The code:
```js
function debounce(fn, delay) {
  let timer;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}
```

### The reader's question
You're reading a search box that calls an API on every keystroke, except it doesn't. Someone wrapped it in `debounce` and now it waits. How does `debounce` decide when to actually fire?

### Mental model
Debounce is an elevator door. Every time someone walks through the sensor, the "about to close" timer resets. The door only closes when nobody has walked through for a few seconds.

Three rules:
1. Each call starts a fresh timer.
2. If a new call comes in before the timer ends, the old timer is cancelled.
3. The wrapped function only runs when a timer finishes without being cancelled.

### Diagram
```
keystrokes:   k---k--k-------k---------------|
                                             ^ fn fires here, 300ms after last k
timer:        [t1] [t2] [t3] [t4]
                              ^^^^ runs to completion
cancellations: ^^   ^^   ^^   (t1, t2, t3 cancelled by the next keystroke)
```

### Walkthrough
Call `const search = debounce(apiCall, 300)` to set up. The closure captures `timer` (currently `undefined`) and `apiCall`.

Now the user types "h":
1. `search("h")` runs.
2. `clearTimeout(undefined)` is a no-op; no timer to cancel yet.
3. `setTimeout(..., 300)` schedules `apiCall("h")` to run in 300ms. `timer` now holds that timeout ID.

User types "he" 50ms later:
1. `search("he")` runs.
2. `clearTimeout(timer)` cancels the pending `apiCall("h")`. It will never run.
3. A new timeout is scheduled for `apiCall("he")`. `timer` is reassigned.

User stops typing. 300ms passes without another call:
1. The timer completes.
2. `apiCall("he")` runs with whatever `this` and arguments were captured on the final call.

### Gotcha
Debounce delays the FIRST call too. If you want "fire immediately, then ignore further calls for N ms", that's throttle, not debounce. Writers mix them up constantly. The difference is which end of the window fires: debounce fires at the END of a quiet period, throttle fires at the START and locks out the rest.

A second, subtler one: `this` and the arguments come from the LAST call, not the first. If you expected the first call's values to be preserved, you'll be confused when you log them.

### Now you can read the rest
With the model in hand, you can predict what happens if you call `search("x")` and then call `search.cancel()` (there's no cancel in this version; adding one would null out `timer` after a `clearTimeout`). You can also predict what breaks if `fn` is async and you call it faster than it resolves (nothing special, because debounce doesn't know or care about the return value).

---

## Example 2: a React useEffect cleanup

The code:
```jsx
useEffect(() => {
  const id = setInterval(() => setCount(c => c + 1), 1000);
  return () => clearInterval(id);
}, []);
```

### The reader's question
You see the `return () => clearInterval(id)` and wonder why `useEffect` returns a function at all. What runs it? When?

### Mental model
`useEffect` is a janitor on a shift. Each time the component renders, React says "here's your shift, and here's how to clean up when you leave." The returned function is the cleanup; React runs it before the next shift starts, and when the component unmounts.

Two rules:
1. The function you pass TO `useEffect` runs AFTER React commits the render to the DOM.
2. The function you RETURN from that function runs BEFORE the next effect runs, and when the component unmounts.

The empty dependency array `[]` means "only start one shift, at mount, and clean up at unmount."

### Diagram
```
mount                                              unmount
  |                                                  |
  v                                                  v
  [effect runs]   ...component lives...   [cleanup runs]
   |                                         ^
   +---- setInterval returns id -------------+
                                             cleanup uses id to stop the interval
```

### Walkthrough
Component mounts. React commits the DOM. React then calls the effect function:
1. `setInterval(..., 1000)` schedules a tick every second. It returns an opaque `id`.
2. The effect returns `() => clearInterval(id)`. React stores this cleanup, paired with THIS effect's `id`.

Component lives for 5 seconds. The interval fires five times; each call bumps `count`.

Component unmounts (parent stops rendering it):
1. React runs the stored cleanup.
2. `clearInterval(id)` stops the ticker. If this didn't happen, the interval would keep calling `setCount` on a dead component and leak memory.

### Gotcha
If you write the dependency array as `[count]` instead of `[]`, you get a new interval EVERY time `count` changes. The old one is cleaned up (so no leak), but the ticker effectively restarts every tick, which is a subtle bug that only shows up when the delay matters. The lesson is: the dep array says "when should the effect tear down and set up again?" not "what values should I use inside it."

### Now you can read the rest
With the janitor model, you can predict what happens with any effect: when does it run, when does it clean up, what state does each cleanup close over. You can also predict why `useEffect(() => fetch(url), [])` is dangerous if the component unmounts mid-fetch (the response arrives and tries to `setState` on a gone component; the cleanup needs to abort the fetch).

---

## Example 3: an Airtable formula

The formula, on a `Days Since Last Contact` field:
```
IF({Last Contact Date}, DATETIME_DIFF(TODAY(), {Last Contact Date}, 'days'), BLANK())
```

### The reader's question
You see rows where this field is empty and rows where it's a number. Why does it sometimes have a value and sometimes not, and what's the `BLANK()` doing?

### Mental model
An Airtable formula is a tiny calculator that runs once per row, for every row, every time any input changes. There is no loop and no state. If the formula references `{Last Contact Date}` and that field is empty for a row, the formula still runs for that row; it just sees an empty value.

Rule to remember: `IF(x, a, b)` returns `a` if `x` is truthy, `b` otherwise. In Airtable, an empty date field is falsy.

### Diagram
```
for each row:
  input: {Last Contact Date}
         |
         v
  IF date exists?
     yes -> DATETIME_DIFF(today, date, days) -> integer
     no  -> BLANK() -> empty cell
```

### Walkthrough
Row A has `Last Contact Date = 2026-11-10`. Today is 2026-11-20.
1. The formula sees `{Last Contact Date}` is truthy (a real date).
2. It takes the `then` branch.
3. `DATETIME_DIFF(TODAY(), 2026-11-10, 'days')` returns `10`.
4. The cell displays `10`.

Row B has `Last Contact Date` empty.
1. The formula sees `{Last Contact Date}` is empty (falsy).
2. It takes the `else` branch.
3. `BLANK()` returns an empty value.
4. The cell displays nothing.

### Gotcha
`BLANK()` is not the same as `""` (empty string) or `0`. If you downstream this field into another formula that checks `IF({Days Since Last Contact}, ...)`, `BLANK()` is falsy; but if you check `{Days Since Last Contact} = ""`, that comparison is false (because `BLANK()` is not a string). If a downstream automation condition keeps missing rows that look empty, this is why; use `{field}` alone or a null check, not `= ""`.

### Now you can read the rest
With this model, you can predict how any Airtable formula handles empties: every function propagates blanks in its own way, and the safest pattern is always `IF({field}, do_thing, BLANK())` at the outer level. You can also predict that changing `TODAY()` to `NOW()` would silently change the field type to datetime and could break downstream filters.
