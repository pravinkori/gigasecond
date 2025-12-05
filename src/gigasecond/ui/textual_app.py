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
    """Shows static computation results."""

    def show_results(self, dob: datetime, milestone_seconds: int):
        now = datetime.now()
        age_td = now - dob
        _, _, _, _, total_seconds = breakdown(age_td)
        milestone_time = dob + timedelta(seconds=milestone_seconds)
        text = (
            f"[b]Date of Birth:[/] {dob}\n\n"
            f"[b]Total seconds lived:[/] {total_seconds:,}\n\n"
            f"[b]Milestone:[/] {milestone_seconds:,} seconds\n"
            f"[b]Milestone occurs on:[/] {milestone_time}\n"
        )
        self.update(text)


class LivePanel(Static):
    """Shows real-time age & countdown."""

    def update_live(self, dob: Optional[datetime], milestone_seconds: Optional[int]):
        now = datetime.now()
        if dob is None:
            self.update("[i]No DOB entered yet.[/]")
            return

        age_td = now - dob
        ad, ah, am, asec, atot = breakdown(age_td)

        if milestone_seconds is None:
            countdown_text = "Select a milestone"
        else:
            milestone_time = dob + timedelta(seconds=milestone_seconds)
            remaining_td = milestone_time - now
            rd, rh, rm, rs, rtot = breakdown(remaining_td)
            if remaining_td.total_seconds() > 0:
                countdown_text = f"{rd}d {rh}h {rm}m {rs}s remaining"
            else:
                countdown_text = f"Passed {( -int(remaining_td.total_seconds()) ):,} seconds ago"

        text = (
            "[b green]Real-time age[/]\n"
            f" • {ad} days, {ah} hours, {am} minutes, {asec} seconds\n\n"
            "[b cyan]Countdown[/]\n"
            f" • {countdown_text}\n"
        )
        self.update(text)


class ErrorModal(Static):
    """Error overlay modal."""

    DEFAULT_CSS = """
    ErrorModal {
        layer: overlay;
        background: #1c1c1c;
        border: heavy red;
        padding: 2 2;
        width: 60%;
        content-align: center middle;
    }
    """

    def show(self, message: str):
        self.update(f"[b red]Error:[/] {message}\n\nPress any key to dismiss")
        self.styles.display = "block"

    def hide(self):
        self.styles.display = "none"


class GigasecondApp(App):
    CSS = """
    Screen {
        align: center middle;
        padding: 1;
    }

    Input, Select {
        width: 100%;
    }

    .panel {
        border: round #666;
        padding: 1 1;
        height: auto;
        width: 1fr;
    }

    .controls {
        min-width: 38%;
        max-width: 48%;
    }

    .results {
        min-width: 52%;
    }

    Label {
        padding-bottom: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
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

        modal = ErrorModal(id="error_modal")
        modal.hide()
        yield modal

    def on_mount(self) -> None:
        self.set_interval(1.0, self._periodic_update)
        self.milestone_seconds = BILLION

    def _show_error(self, message: str) -> None:
        modal = self.query_one("#error_modal", ErrorModal)
        modal.show(message)
        self.set_focus(modal)

    def _hide_error(self) -> None:
        modal = self.query_one("#error_modal", ErrorModal)
        modal.hide()
        self.set_focus(self.query_one("#dob_input", Input))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "calc_btn":
            self._handle_calculate()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "dob_input":
            self._handle_calculate()
        elif event.input.id == "custom_milestone":
            self._apply_custom_milestone(event.value)

    def on_select_changed(self, event: Select.Changed) -> None:
        value = event.value
        if value == "custom":
            self.query_one("#custom_milestone", Input).focus()
        else:
            try:
                billions = float(value)
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
        modal = self.query_one("#error_modal", ErrorModal)
        if modal.styles.display == "block":
            self._hide_error()
