"""
Graphical User Interface for the Mental Health Chatbot (Aura).
Built using Python's standard Tkinter with a modern dark theme,
message styling, scroll support, and quick actions.
"""

from datetime import datetime
import tkinter as tk
from tkinter import font as tkfont
from chat import get_response, bot_name

# Aesthetic Color Palette (Calming Midnight / Slate)
COLOR_BG = "#0F172A"         # Main background (Deep Slate)
COLOR_HEADER = "#1E293B"     # Header container
COLOR_BORDER = "#334155"     # Subtle border lines
COLOR_CHAT_BG = "#090D16"    # Chat conversation canvas
COLOR_TEXT_MAIN = "#F1F5F9"  # High contrast crisp text
COLOR_TEXT_MUTED = "#94A3B8" # Secondary info / timestamps
COLOR_ACCENT_USER = "#38BDF8"# Cyan accent for user
COLOR_ACCENT_BOT = "#A78BFA" # Soft lavender accent for Aura
COLOR_BTN_PRIMARY = "#6366F1"# Indigo primary button
COLOR_BTN_HOVER = "#4F46E5"  # Button hover state
COLOR_BTN_MUTED = "#334155"  # Secondary button
COLOR_STATUS_GREEN = "#10B981" # Online dot indicator


class ChatApplication:
    """Modern Tkinter GUI for chatting with Aura."""

    def __init__(self):
        self.window = tk.Tk()
        self._setup_window_geometry(width=620, height=780)
        self._setup_styles()
        self._build_header()
        self._build_chat_display()
        self._build_input_bar()
        self._display_welcome_message()

    def run(self):
        """Start the Tkinter event loop."""
        self.window.mainloop()

    def _setup_window_geometry(self, width: int, height: int):
        """Center the window on the user's desktop."""
        self.window.title(f"{bot_name} - Mental Health Companion")
        self.window.configure(bg=COLOR_BG)
        self.window.resizable(True, True)
        self.window.minsize(500, 600)

        # Calculate coordinates to center window
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        pos_x = max(0, (screen_w - width) // 2)
        pos_y = max(0, (screen_h - height) // 2)
        self.window.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

    def _setup_styles(self):
        """Define scalable typography."""
        self.font_title = tkfont.Font(family="Segoe UI", size=13, weight="bold")
        self.font_subtitle = tkfont.Font(family="Segoe UI", size=9)
        self.font_msg_bold = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.font_msg = tkfont.Font(family="Segoe UI", size=10)
        self.font_meta = tkfont.Font(family="Segoe UI", size=8)
        self.font_input = tkfont.Font(family="Segoe UI", size=11)
        self.font_btn = tkfont.Font(family="Segoe UI", size=10, weight="bold")

    def _build_header(self):
        """Construct the top header banner with status and action buttons."""
        header_frame = tk.Frame(self.window, bg=COLOR_HEADER, height=70, padx=16, pady=12)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        header_frame.pack_propagate(False)

        # Title & Status Subtitle
        info_frame = tk.Frame(header_frame, bg=COLOR_HEADER)
        info_frame.pack(side=tk.LEFT, fill=tk.Y)

        title_label = tk.Label(
            info_frame,
            text=f"🌿 {bot_name}",
            bg=COLOR_HEADER,
            fg=COLOR_TEXT_MAIN,
            font=self.font_title,
            anchor="w",
        )
        title_label.pack(anchor="w")

        status_frame = tk.Frame(info_frame, bg=COLOR_HEADER)
        status_frame.pack(anchor="w")

        status_dot = tk.Label(
            status_frame,
            text="●",
            bg=COLOR_HEADER,
            fg=COLOR_STATUS_GREEN,
            font=self.font_subtitle,
        )
        status_dot.pack(side=tk.LEFT, padx=(0, 4))

        status_label = tk.Label(
            status_frame,
            text="Online & Ready to listen",
            bg=COLOR_HEADER,
            fg=COLOR_TEXT_MUTED,
            font=self.font_subtitle,
        )
        status_label.pack(side=tk.LEFT)

        # Quick Actions (Clear Chat button)
        actions_frame = tk.Frame(header_frame, bg=COLOR_HEADER)
        actions_frame.pack(side=tk.RIGHT, fill=tk.Y)

        clear_btn = tk.Button(
            actions_frame,
            text="Clear Chat",
            bg=COLOR_BTN_MUTED,
            fg=COLOR_TEXT_MAIN,
            font=self.font_subtitle,
            activebackground=COLOR_BORDER,
            activeforeground=COLOR_TEXT_MAIN,
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._clear_chat,
        )
        clear_btn.pack(side=tk.RIGHT, pady=6)

        # Thin divider line
        divider = tk.Frame(self.window, bg=COLOR_BORDER, height=1)
        divider.pack(side=tk.TOP, fill=tk.X)

    def _build_chat_display(self):
        """Construct scrollable chat text pane with custom tag formatting."""
        container = tk.Frame(self.window, bg=COLOR_CHAT_BG, padx=12, pady=12)
        container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chat_display = tk.Text(
            container,
            bg=COLOR_CHAT_BG,
            fg=COLOR_TEXT_MAIN,
            font=self.font_msg,
            wrap=tk.WORD,
            bd=0,
            padx=10,
            pady=10,
            yscrollcommand=scrollbar.set,
            cursor="arrow",
        )
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.chat_display.yview)

        # Configure custom text tags for formatted conversation bubbles
        self.chat_display.tag_config(
            "user_sender",
            foreground=COLOR_ACCENT_USER,
            font=self.font_msg_bold,
            spacing3=2,
        )
        self.chat_display.tag_config(
            "user_body",
            foreground=COLOR_TEXT_MAIN,
            font=self.font_msg,
            lmargin1=12,
            lmargin2=12,
            spacing3=14,
        )
        self.chat_display.tag_config(
            "bot_sender",
            foreground=COLOR_ACCENT_BOT,
            font=self.font_msg_bold,
            spacing3=2,
        )
        self.chat_display.tag_config(
            "bot_body",
            foreground=COLOR_TEXT_MAIN,
            font=self.font_msg,
            lmargin1=12,
            lmargin2=12,
            spacing3=14,
        )
        self.chat_display.tag_config(
            "meta_time",
            foreground=COLOR_TEXT_MUTED,
            font=self.font_meta,
        )
        self.chat_display.tag_config(
            "system_welcome",
            foreground=COLOR_TEXT_MUTED,
            font=self.font_subtitle,
            justify=tk.CENTER,
            spacing3=16,
        )

        self.chat_display.configure(state=tk.DISABLED)

    def _build_input_bar(self):
        """Construct the bottom input entry and Send button."""
        input_container = tk.Frame(self.window, bg=COLOR_HEADER, padx=12, pady=12)
        input_container.pack(side=tk.BOTTOM, fill=tk.X)

        # Message Entry Box
        self.entry_var = tk.StringVar()
        self.msg_entry = tk.Entry(
            input_container,
            textvariable=self.entry_var,
            bg="#0B132B",
            fg=COLOR_TEXT_MAIN,
            insertbackground=COLOR_TEXT_MAIN,
            font=self.font_input,
            bd=1,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
            highlightcolor=COLOR_BTN_PRIMARY,
        )
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=8)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>", lambda event: self._on_send())

        # Send Button
        self.send_btn = tk.Button(
            input_container,
            text="Send  ➤",
            bg=COLOR_BTN_PRIMARY,
            fg=COLOR_TEXT_MAIN,
            font=self.font_btn,
            activebackground=COLOR_BTN_HOVER,
            activeforeground=COLOR_TEXT_MAIN,
            relief=tk.FLAT,
            padx=18,
            pady=6,
            cursor="hand2",
            command=self._on_send,
        )
        self.send_btn.pack(side=tk.RIGHT)

    def _display_welcome_message(self):
        """Insert intro message explaining Aura's role."""
        welcome_text = (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "✨ Welcome to Aura — Your Compassionate Mental Health Companion.\n"
            "Feel free to talk about anxiety, depression, stress, sleep, or daily feelings.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, welcome_text, "system_welcome")

        intro_response = (
            f"Hello! I'm {bot_name}. I'm here to support your mental well-being, "
            "offer coping strategies, or just listen whenever you need a safe space. "
            "How are you feeling right now?"
        )
        self._insert_chat_bubble(bot_name, intro_response, is_user=False)
        self.chat_display.configure(state=tk.DISABLED)

    def _on_send(self):
        """Trigger message dispatch on Enter key or Send button click."""
        msg = self.entry_var.get().strip()
        if not msg:
            return

        self.entry_var.set("")
        self._insert_chat_bubble("You", msg, is_user=True)

        # Generate response from inference engine
        bot_reply = get_response(msg)
        self._insert_chat_bubble(bot_name, bot_reply, is_user=False)

    def _insert_chat_bubble(self, sender: str, text: str, is_user: bool):
        """Append formatted message bubble to chat transcript."""
        time_str = datetime.now().strftime("%I:%M %p")
        sender_tag = "user_sender" if is_user else "bot_sender"
        body_tag = "user_body" if is_user else "bot_body"
        prefix = "👤 " if is_user else "🌿 "

        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{prefix}{sender} ", sender_tag)
        self.chat_display.insert(tk.END, f"• {time_str}\n", "meta_time")
        self.chat_display.insert(tk.END, f"{text}\n\n", body_tag)
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def _clear_chat(self):
        """Reset chat log and redisplay welcome prompt."""
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.configure(state=tk.DISABLED)
        self._display_welcome_message()


if __name__ == "__main__":
    app = ChatApplication()
    app.run()