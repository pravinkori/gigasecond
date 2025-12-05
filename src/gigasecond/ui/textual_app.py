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
            color = "green"
        elif progress < 90:
            color = "yellow"
        else:
            color = "red"
        
        text = (
            f"[b cyan]📅 Date of Birth[/]\n"
            f"   {dob.strftime('%B %d, %Y at %H:%M')}\n\n"
            
            f"[b magenta]⏱️  Current Age[/]\n"
            f"   {total_seconds:,} seconds\n\n"
            
            f"[b {color}]🎯 Milestone Progress[/]\n"
            f"   [{color}]{bar}[/] {progress:.1f}%\n"
            f"   Target: {milestone_seconds:,} seconds\n\n"
            
            f"[b blue]🎉 Milestone Date[/]\n"
            f"   {milestone_time.strftime('%B %d, %Y at %H:%M:%S')}\n"
        )
        self.update(text)


class LivePanel(Static):
    """Shows real-time age & countdown with visual flair."""

    def update_live(self, dob: Optional[datetime], milestone_seconds: Optional[int]):
        now = datetime.now()
        
        if dob is None:
            self.update(
                "[dim]   Enter your date of birth to see\n"
                "   your age ticking in real-time...[/]"
            )
            return

        age_td = now - dob
        ad, ah, am, asec, atot = breakdown(age_td)

        # Build age section
        age_text = (
            "[b green]⚡ Live Age Counter[/]\n"
            f"   [cyan]{ad:,}[/] days  "
            f"[cyan]{ah:02d}[/]:[cyan]{am:02d}[/]:[cyan]{asec:02d}[/]\n"
        )

        # Build countdown section
        if milestone_seconds is None:
            countdown_text = "\n[b yellow]🎯 Countdown[/]\n   [dim]Select a milestone above[/]"
        else:
            milestone_time = dob + timedelta(seconds=milestone_seconds)
            remaining_td = milestone_time - now
            rd, rh, rm, rs, rtot = breakdown(remaining_td)
            
            if remaining_td.total_seconds() > 0:
                # Calculate urgency color
                days_left = remaining_td.days
                if days_left > 365:
                    urgency_color = "green"
                    icon = "🟢"
                elif days_left > 30:
                    urgency_color = "yellow"
                    icon = "🟡"
                else:
                    urgency_color = "red"
                    icon = "🔴"
                
                countdown_text = (
                    f"\n[b {urgency_color}]⏳ Countdown to Milestone[/] {icon}\n"
                    f"   [bold]{rd:,}[/] days, "
                    f"[bold]{rh:02d}[/]:[bold]{rm:02d}[/]:[bold]{rs:02d}[/]\n"
                    f"   [dim]({rtot:,} seconds remaining)[/]"
                )
            else:
                seconds_past = -int(remaining_td.total_seconds())
                countdown_text = (
                    "\n[b magenta]🎊 Milestone Achieved![/]\n"
                    f"   Passed {seconds_past:,} seconds ago\n"
                    f"   [dim]on {milestone_time.strftime('%b %d, %Y')}[/]"
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
    }

    /* Improved panel styling with depth */
    .panel {
        border: heavy $accent;
        padding: 2;
        height: auto;
        background: $surface;
    }

    .panel-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    /* Better input styling */
    Input {
        border: solid $primary;
        margin: 1 0;
    }

    Input:focus {
        border: heavy $accent;
    }

    /* Hide custom input by default */
    #custom_milestone {
        display: none;
    }

    #custom_milestone.visible {
        display: block;
    }

    /* Smooth animations */
    .fade-in {
        transition: opacity 300ms;
    }
    """
    # BINDINGS = [
    #     ("q", "quit", "Quit"),
    # ]
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "reset", "Reset"),
        ("c", "calculate", "Calculate"),
        ("escape", "clear_errors", "Clear"),
    ]

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

