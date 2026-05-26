# Agent Workflows

These recordings show Claude Code working inside the Q-agent workspace — editing strategy files, running backtests, and navigating the LEAN CLI.

<p class="mdx-recording-label">▶ Strategy development with Claude Code</p>
<div class="mdx-recording">
<asciinema-player src="../recordings/agent-workflow.cast" cols="120" rows="20" preload="true" idle-time-limit="2" theme="monokai"></asciinema-player>
</div>

---

## How to record your own session

Recordings are plain text files (`.cast`) stored in `docs/recordings/`. Record with [asciinema](https://asciinema.org/):

```bash
# Install
pip install asciinema

# Record — press Ctrl+D or type exit when done
asciinema rec docs/recordings/my-session.cast --title "My workflow"
```

Then embed the player in any docs page:

```html
<p class="mdx-recording-label">▶ My session title</p>
<div class="mdx-recording">
<asciinema-player
  src="../recordings/my-session.cast"
  cols="120"
  rows="24"
  preload="true"
  idle-time-limit="2"
  theme="monokai">
</asciinema-player>
</div>
```

### Useful player options

| Attribute | Effect |
|---|---|
| `cols` / `rows` | Terminal dimensions |
| `theme` | `monokai`, `solarized-dark`, `dracula`, `nord` |
| `autoplay="true"` | Starts playing on load |
| `loop="true"` | Loops the recording |
| `idle-time-limit="2"` | Collapses idle gaps to 2 seconds |
| `speed="1.5"` | Playback speed multiplier |

### Tips for clean recordings

- Set your terminal width to 120 columns before recording: `export COLUMNS=120`
- Use `idle-time-limit` to cut out pauses while typing
- Record short, focused sessions (< 3 minutes) — one concept per recording
- Avoid scrolling large log outputs; pipe to `head` or `tail` instead
