from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import (
    Header,
    Footer,
    Input,
    Button,
    Static,
    Select,
    Label,
    Checkbox,
)

from gigasecond.core import parse_dob, BILLION
from gigasecond.utils import breakdown


class ResultPanel(Static):
    """Shows static computation results with progress visualization."""

    def show_results(self, dob: datetime, milestone_seconds: int):
        now = datetime.now()
        age_td = now - dob
        _, _, _, _, total_seconds = breakdown(age_td)
        milestone_time = dob + timedelta(seconds=milestone_seconds)
        
        # Calculate progress percentage
        progress = min(100, (total_seconds / milestone_seconds) * 100)
        
        # Create visual progress bar
        bar_length = 30
        filled = int(bar_length * progress / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        # Color coding based on proximity
        if progress < 50:
            color = "#22c55e"  # green
        elif progress < 90:
            color = "#fbbf24"  # yellow
        else:
            color = "#ef4444"  # red
        
        text = (
            f"[bold #8b7ff4]📅 Date of Birth[/]\n"
            f"[#a8b2d1]   {dob.strftime('%B %d, %Y at %H:%M')}[/]\n\n"
            
            f"[bold #ec4899]⏱️  Current Age[/]\n"
            f"[#a8b2d1]   {total_seconds:,} seconds[/]\n\n"
            
            f"[bold {color}]🎯 Milestone Progress[/]\n"
            f"[{color}]   {bar}[/] [bold]{progress:.1f}%[/]\n"
            f"[#6b7280]   Target: {milestone_seconds:,} seconds[/]\n\n"
            
            f"[bold #3b82f6]🎉 Milestone Date[/]\n"
            f"[#a8b2d1]   {milestone_time.strftime('%B %d, %Y at %H:%M:%S')}[/]\n"
        )
        self.update(text)


class LivePanel(Static):
    """Shows real-time age & countdown with visual flair."""

    def update_live(self, dob: Optional[datetime], milestone_seconds: Optional[int]):
        now = datetime.now()
        
        if dob is None:
            self.update(
                "[dim #6b7280]💭 Enter your date of birth to see\n"
                "   your age ticking in real-time...[/]"
            )
            return

        age_td = now - dob
        ad, ah, am, asec, atot = breakdown(age_td)

        # Build age section
        age_text = (
            "[bold #22c55e]⚡ Live Age Counter[/]\n"
            f"   [#8b7ff4]{ad:,}[/] days  "
            f"[#22c55e]{ah:02d}[/]:[#22c55e]{am:02d}[/]:[#22c55e]{asec:02d}[/]\n"
        )

        # Build countdown section
        if milestone_seconds is None:
            countdown_text = "\n[bold #fbbf24]🎯 Countdown[/]\n   [dim #6b7280]Select a milestone above[/]"
        else:
            milestone_time = dob + timedelta(seconds=milestone_seconds)
            remaining_td = milestone_time - now
            rd, rh, rm, rs, rtot = breakdown(remaining_td)
            
            if remaining_td.total_seconds() > 0:
                # Calculate urgency color
                days_left = remaining_td.days
                if days_left > 365:
                    urgency_color = "#22c55e"
                    icon = "🟢"
                elif days_left > 30:
                    urgency_color = "#fbbf24"
                    icon = "🟡"
                else:
                    urgency_color = "#ef4444"
                    icon = "🔴"
                
                countdown_text = (
                    f"\n[b {urgency_color}]⏳ Countdown to Milestone[/] {icon}\n"
                    f"   [bold]{rd:,}[/] days, "
                    f"[bold]{rh:02d}[/]:[bold]{rm:02d}[/]:[bold]{rs:02d}[/]\n"
                    f"   [dim #6b7280]({rtot:,} seconds remaining)[/]"
                )
            else:
                seconds_past = -int(remaining_td.total_seconds())
                countdown_text = (
                    "\n[b #ec4899]🎊 Milestone Achieved![/]\n"
                    f"   Passed {seconds_past:,} seconds ago\n"
                    f"   [dim #6b7280]on {milestone_time.strftime('%b %d, %Y')}[/]"
                )

        self.update(age_text + countdown_text)


class InlineError(Static):
    """Inline error message with auto-dismiss."""
    
    DEFAULT_CSS = """
    InlineError {
        color: $error;
        background: $error 20%;
        border: solid $error;
        padding: 1 2;
        margin: 1 0;
        display: none;
    }
    
    InlineError.visible {
        display: block;
    }
    """
    
    def show(self, message: str):
        self.update(f"⚠️  {message}")
        self.add_class("visible")
        self.set_timer(5.0, lambda: self.remove_class("visible"))


class GigasecondApp(App):
    CSS = """
    Screen {
        align: center middle;
        # background: $background;
    }

    /* Modern color palette */
    * {
        scrollbar-background: #1a1a2e;
        scrollbar-color: #6c63ff;
    }

    /* Input styling */
    Input {
        border: solid $primary;
        margin: 1 0;
    }

    Input:focus {
        border: heavy #8b7ff4;
        background: #1a2744;
    }

    /* Select styling */
    Select {
        border: round #6c63ff;
        background: #16213e;
        color: #e8e8e8;
        padding: 1 2;
        margin: 1 0;
        width: 100%;
    }

    Select:focus {
        border: heavy #8b7ff4;
    }

    /* Button styling */
    Button {
        border: round #22c55e;
        background: #16a34a;
        color: white;
        margin: 1 0;
        width: 100%;
    }

    Button:hover {
        background: #22c55e;
        border: heavy #4ade80;
    }

    Button:focus {
        border: heavy #86efac;
    }

    /* Checkbox styling */
    Checkbox {
        border: round #6c63ff;
        background: #16213e;
        padding: 1;
        margin: 1 0;
    }

    Checkbox:focus {
        border: heavy #8b7ff4;
    }

    /* Panel containers */
    .panel {
        border: round #3d5a80;
        background: #0f1419;
        padding: 2;
        height: auto;
        margin: 1;
    }

    .controls {
        min-width: 38%;
        max-width: 48%;
    }

    .results {
        min-width: 52%;
    }

    /* Labels */
    Label {
        color: #a8b2d1;
        padding-bottom: 1;
        text-style: bold;
    }

    /* Result panels */
    #result_panel {
        border: round #6c63ff;
        background: #16213e;
        padding: 2;
        margin-bottom: 1;
        min-height: 12;
    }

    #live_panel {
        border: round #22c55e;
        background: #16213e;
        padding: 2;
        min-height: 8;
    }

    /* Inline error styling */
    InlineError {
        color: #fca5a5;
        background: #7f1d1d;
        border: round #dc2626;
        padding: 1 2;
        margin: 1 0;
        display: none;
    }

    InlineError.visible {
        display: block;
    }

    /* Custom milestone input - hidden by default */
    #custom_milestone {
        display: none;
    }

    #custom_milestone.visible {
        display: block;
    }

    /* Header and Footer */
    Header {
        background: #6c63ff;
        color: white;
    }

    Footer {
        background: #1a1a2e;
    }

    /* Horizontal container spacing */
    Horizontal {
        height: auto;
        margin: 1 2;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "reset", "Reset"),
        ("c", "calculate", "Calculate"),
        ("escape", "clear_errors", "Clear"),
    ]

    def action_reset(self) -> None:
        """Reset the form."""
        self.query_one("#dob_input", Input).value = ""
        self.query_one("#result_panel", ResultPanel).update("")
        self.dob = None
        self.milestone_seconds = BILLION
        self.query_one("#milestone_select", Select).value = "1"
    
    def action_calculate(self) -> None:
        """Trigger calculation."""
        self._handle_calculate()
    
    def action_clear_errors(self) -> None:
        """Clear error messages."""
        error = self.query_one("#inline_error", InlineError)
        error.remove_class("visible")

    dob: Optional[datetime] = reactive(None)
    milestone_seconds: Optional[int] = reactive(None)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()

        with Horizontal():
            with Vertical(classes="panel controls"):
                yield Label("Enter your date & time of birth:")
                yield Input(placeholder="YYYY-MM-DD or YYYY-MM-DD HH:MM", id="dob_input")
                yield InlineError(id="inline_error")
                yield Button("Calculate", id="calc_btn")
                yield Label("Pick a milestone (billions) or enter custom:")
                yield Select(
                    options=[
                        ("1 (1,000,000,000)", "1"),
                        ("2 (2,000,000,000)", "2"),
                        ("3 (3,000,000,000)", "3"),
                        ("Custom", "custom"),
                    ],
                    id="milestone_select",
                )
                yield Input(placeholder="Enter billions (e.g. 1.5)", id="custom_milestone")
                yield Checkbox(label="Show real-time age counter", id="live_age_chk", value=True)
                yield Checkbox(label="Show live countdown", id="live_countdown_chk", value=True)

            with Vertical(classes="panel results"):
                yield ResultPanel(id="result_panel")
                yield LivePanel(id="live_panel")

    def on_mount(self) -> None:
        self.set_interval(1.0, self._periodic_update)
        self.milestone_seconds = BILLION

    def _show_error(self, message: str) -> None:
        error = self.query_one("#inline_error", InlineError)
        error.show(message)

    def _hide_error(self) -> None:
        error = self.query_one("#inline_error", InlineError)
        error.remove_class("visible")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "calc_btn":
            self._handle_calculate()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "dob_input":
            self._handle_calculate()
        elif event.input.id == "custom_milestone":
            self._apply_custom_milestone(event.value)

    def on_select_changed(self, event: Select.Changed) -> None:
        custom_input = self.query_one("#custom_milestone", Input)
    
        if event.value == "custom":
            custom_input.add_class("visible")
            custom_input.focus()
        else:
            custom_input.remove_class("visible")
            try:
                billions = float(event.value)
                self.milestone_seconds = int(billions * BILLION)
            except Exception:
                self.milestone_seconds = BILLION

    def _apply_custom_milestone(self, text: str) -> None:
        try:
            b = float(text.strip())
            if b <= 0:
                raise ValueError
            self.milestone_seconds = int(b * BILLION)
        except Exception:
            self._show_error("Invalid custom milestone. Enter a positive number like 1.5")

    def _handle_calculate(self) -> None:
        dob_input = self.query_one("#dob_input", Input).value
        if not dob_input.strip():
            self._show_error("Please enter your date of birth.")
            return
        try:
            dob = parse_dob(dob_input)
        except ValueError as e:
            self._show_error(str(e))
            return

        self.dob = dob

        select = self.query_one("#milestone_select", Select)
        if select.value == "custom":
            custom = self.query_one("#custom_milestone", Input).value
            if custom.strip():
                self._apply_custom_milestone(custom)

        self.query_one("#result_panel", ResultPanel).show_results(
            self.dob, self.milestone_seconds or BILLION
        )

    def _periodic_update(self) -> None:
        live_age = self.query_one("#live_age_chk", Checkbox).value
        live_count = self.query_one("#live_countdown_chk", Checkbox).value
        live_panel = self.query_one("#live_panel", LivePanel)

        if self.dob is None:
            live_panel.update_live(None, None)
            return

        ms = self.milestone_seconds if live_count else None
        dob = self.dob if live_age else None

        live_panel.update_live(dob, ms)

    def on_key(self, event) -> None:
        if event.key == "escape":
            error = self.query_one("#inline_error", InlineError)
            error.remove_class("visible")

