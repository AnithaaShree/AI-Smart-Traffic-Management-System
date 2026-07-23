# gui.py
# Tkinter GUI dashboard for the AI Smart Traffic Management System.
# Includes: live video, signal lights, dashboard cards, scenario selector,
# and a real-time status log.

import tkinter as tk
from PIL import Image, ImageTk
import cv2
from config import VIDEO_DISPLAY_WIDTH, VIDEO_DISPLAY_HEIGHT, WINDOW_SIZE, VIDEOS


# ── Colour palette ─────────────────────────────────────────────────────────
BG_DEEP    = "#0d1117"
BG_CARD    = "#161b22"
BG_HEADER  = "#0d1117"
BG_VIDEO   = "#010409"
ACCENT     = "#e34c26"       # red-orange accent
ACCENT2    = "#58a6ff"       # blue accent
TEXT_MAIN  = "#c9d1d9"
TEXT_DIM   = "#8b949e"
GREEN_COL  = "#3fb950"
YELLOW_COL = "#d29922"
RED_COL    = "#f85149"
FONT_MONO  = "Courier"


class TrafficGUI:
    """
    Main GUI window. Exposes update methods called from main.py every frame.
    """

    def __init__(self, root, scenario_change_callback):
        self.root = root
        self.root.title("AI Smart Traffic Management System")
        self.root.configure(bg=BG_DEEP)
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(False, False)

        self._scenario_cb = scenario_change_callback
        self._build_ui()

    # ──────────────────────────────────────────────────────────────────────
    # UI Construction
    # ──────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()

        body = tk.Frame(self.root, bg=BG_DEEP)
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))

        self._build_video_panel(body)
        self._build_dashboard(body)

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=BG_HEADER, height=52)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        # Red dot icon
        tk.Label(hdr, text="●", font=(FONT_MONO, 20),
                 bg=BG_HEADER, fg=ACCENT).pack(side=tk.LEFT, padx=(18, 6))

        tk.Label(
            hdr,
            text="AI Smart Traffic Management System",
            font=(FONT_MONO, 16, "bold"),
            bg=BG_HEADER, fg=TEXT_MAIN
        ).pack(side=tk.LEFT, pady=8)

        # Scenario selector on the right
        tk.Label(hdr, text="Scenario:", font=(FONT_MONO, 10),
                 bg=BG_HEADER, fg=TEXT_DIM).pack(side=tk.RIGHT, padx=(0, 6))

        self._scenario_var = tk.StringVar(value=list(VIDEOS.keys())[0])
        scenario_menu = tk.OptionMenu(
            hdr, self._scenario_var, *VIDEOS.keys(),
            command=self._on_scenario_change
        )
        scenario_menu.config(
            font=(FONT_MONO, 9), bg="#21262d", fg=TEXT_MAIN,
            activebackground="#30363d", activeforeground=TEXT_MAIN,
            highlightthickness=0, relief="flat", width=18
        )
        scenario_menu["menu"].config(
            font=(FONT_MONO, 9), bg="#21262d", fg=TEXT_MAIN
        )
        scenario_menu.pack(side=tk.RIGHT, padx=(0, 16), pady=10)

    def _build_video_panel(self, parent):
        panel = tk.Frame(parent, bg=BG_VIDEO, bd=0,
                         highlightbackground="#30363d", highlightthickness=1)
        panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=6)

        # Sub-header
        subhdr = tk.Frame(panel, bg="#161b22")
        subhdr.pack(fill=tk.X)
        tk.Label(subhdr, text="●", font=(FONT_MONO, 10),
                 bg="#161b22", fg=ACCENT).pack(side=tk.LEFT, padx=(10, 4), pady=6)
        tk.Label(subhdr, text="Live Traffic Feed",
                 font=(FONT_MONO, 10, "bold"),
                 bg="#161b22", fg=TEXT_MAIN).pack(side=tk.LEFT, pady=6)

        # REC indicator
        self._rec_var = tk.StringVar(value="⏺ REC")
        tk.Label(subhdr, textvariable=self._rec_var,
                 font=(FONT_MONO, 8), bg="#161b22", fg=RED_COL).pack(side=tk.RIGHT, padx=12)

        # Video canvas
        self.video_label = tk.Label(
            panel, bg="#000000",
            width=VIDEO_DISPLAY_WIDTH, height=VIDEO_DISPLAY_HEIGHT
        )
        self.video_label.pack(padx=6, pady=(4, 6))

        # Bottom bar: frame info
        bot = tk.Frame(panel, bg="#161b22")
        bot.pack(fill=tk.X)
        self._frame_info_var = tk.StringVar(value="Frame: 0")
        tk.Label(bot, textvariable=self._frame_info_var,
                 font=(FONT_MONO, 8), bg="#161b22", fg=TEXT_DIM).pack(
            side=tk.LEFT, padx=10, pady=4)

        self._scenario_label_var = tk.StringVar(value="")
        tk.Label(bot, textvariable=self._scenario_label_var,
                 font=(FONT_MONO, 8, "bold"), bg="#161b22", fg=ACCENT2).pack(
            side=tk.RIGHT, padx=10, pady=4)

    def _build_dashboard(self, parent):
        dash = tk.Frame(parent, bg=BG_CARD, width=310,
                        highlightbackground="#30363d", highlightthickness=1)
        dash.pack(side=tk.RIGHT, fill=tk.Y, pady=6)
        dash.pack_propagate(False)

        # Header
        dh = tk.Frame(dash, bg="#161b22")
        dh.pack(fill=tk.X)
        tk.Label(dh, text="■", font=(FONT_MONO, 10),
                 bg="#161b22", fg=ACCENT).pack(side=tk.LEFT, padx=(10, 4), pady=6)
        tk.Label(dh, text="Dashboard",
                 font=(FONT_MONO, 11, "bold"),
                 bg="#161b22", fg=TEXT_MAIN).pack(side=tk.LEFT)

        self._build_signal_widget(dash)
        self._build_info_cards(dash)
        self._build_log(dash)
        self._build_stop_button(dash)

    def _build_signal_widget(self, parent):
        box = tk.Frame(parent, bg="#0d1117",
                       highlightbackground="#30363d", highlightthickness=1)
        box.pack(fill=tk.X, padx=10, pady=(8, 4))

        tk.Label(box, text="Traffic Signal",
                 font=(FONT_MONO, 9, "bold"),
                 bg="#0d1117", fg=TEXT_DIM).pack(pady=(6, 2))

        lights = tk.Frame(box, bg="#0d1117")
        lights.pack(pady=4)

        # Three canvases for the three lights
        self._red_cv    = tk.Canvas(lights, width=56, height=56,
                                    bg="#0d1117", highlightthickness=0)
        self._yellow_cv = tk.Canvas(lights, width=56, height=56,
                                    bg="#0d1117", highlightthickness=0)
        self._green_cv  = tk.Canvas(lights, width=56, height=56,
                                    bg="#0d1117", highlightthickness=0)

        for cv in (self._red_cv, self._yellow_cv, self._green_cv):
            cv.pack(side=tk.LEFT, padx=6)

        self._rc = self._red_cv.create_oval(    4, 4, 52, 52, fill="#3d0000", outline="#30363d", width=1)
        self._yc = self._yellow_cv.create_oval( 4, 4, 52, 52, fill="#3d3000", outline="#30363d", width=1)
        self._gc = self._green_cv.create_oval(  4, 4, 52, 52, fill="#003d00", outline="#30363d", width=1)

        # Labels under lights
        lbl_row = tk.Frame(box, bg="#0d1117")
        lbl_row.pack()
        for txt in ("R", "Y", "G"):
            tk.Label(lbl_row, text=txt, font=(FONT_MONO, 8),
                     bg="#0d1117", fg=TEXT_DIM, width=5).pack(side=tk.LEFT, padx=6)

        # State text + timer
        self._signal_state_var = tk.StringVar(value="● RED")
        self._signal_lbl = tk.Label(
            box, textvariable=self._signal_state_var,
            font=(FONT_MONO, 13, "bold"),
            bg="#0d1117", fg=RED_COL
        )
        self._signal_lbl.pack(pady=(4, 2))

        self._timer_var = tk.StringVar(value="Timer: --s")
        tk.Label(box, textvariable=self._timer_var,
                 font=(FONT_MONO, 10),
                 bg="#0d1117", fg=TEXT_DIM).pack(pady=(0, 8))

    def _build_info_cards(self, parent):
        """Build the four info cards."""
        cards_data = [
            ("vehicle_count", "🚗 Vehicle Count",  "0",   TEXT_MAIN),
            ("density",       "📊 Traffic Density", "Low", GREEN_COL),
            ("ambulance",     "🚑 Ambulance",       "No",  TEXT_MAIN),
            ("violation",     "⚠  Violation",       "No",  TEXT_MAIN),
        ]
        for attr, label, default, color in cards_data:
            self._make_card(parent, label, attr, default, color)

    def _make_card(self, parent, label_text, attr, default, init_color):
        card = tk.Frame(parent, bg="#161b22",
                        highlightbackground="#30363d", highlightthickness=1)
        card.pack(fill=tk.X, padx=10, pady=3)

        tk.Label(card, text=label_text,
                 font=(FONT_MONO, 8), bg="#161b22", fg=TEXT_DIM).pack(
            anchor="w", padx=10, pady=(5, 0))

        var = tk.StringVar(value=default)
        setattr(self, f"_{attr}_var", var)

        lbl = tk.Label(card, textvariable=var,
                       font=(FONT_MONO, 14, "bold"),
                       bg="#161b22", fg=init_color)
        lbl.pack(anchor="w", padx=10, pady=(0, 5))
        setattr(self, f"_{attr}_lbl", lbl)

    def _build_log(self, parent):
        log_frame = tk.Frame(parent, bg="#0d1117",
                             highlightbackground="#30363d", highlightthickness=1)
        log_frame.pack(fill=tk.X, padx=10, pady=(4, 4))

        hdr = tk.Frame(log_frame, bg="#161b22")
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="■", font=(FONT_MONO, 8),
                 bg="#161b22", fg=ACCENT).pack(side=tk.LEFT, padx=(8, 3), pady=3)
        tk.Label(hdr, text="Status Log",
                 font=(FONT_MONO, 8, "bold"),
                 bg="#161b22", fg=TEXT_DIM).pack(side=tk.LEFT)

        self.log_text = tk.Text(
            log_frame, height=5, width=30,
            bg="#010409", fg="#3fb950",
            font=(FONT_MONO, 8),
            state=tk.DISABLED, relief="flat",
            insertbackground=TEXT_MAIN
        )
        self.log_text.pack(padx=6, pady=(4, 6))

    def _build_stop_button(self, parent):
        tk.Button(
            parent,
            text="⏹  STOP SYSTEM",
            font=(FONT_MONO, 9, "bold"),
            bg="#21262d", fg=RED_COL,
            activebackground=RED_COL, activeforeground="white",
            relief="flat", bd=0, pady=8,
            cursor="hand2",
            command=self.root.destroy
        ).pack(fill=tk.X, padx=10, pady=(2, 10))

    # ──────────────────────────────────────────────────────────────────────
    # Public Update Methods (called from main.py every frame)
    # ──────────────────────────────────────────────────────────────────────

    def update_video(self, frame, frame_number):
        """Display a new OpenCV frame in the video panel."""
        rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img   = Image.fromarray(rgb)
        img   = img.resize((VIDEO_DISPLAY_WIDTH, VIDEO_DISPLAY_HEIGHT), Image.LANCZOS)
        imgtk = ImageTk.PhotoImage(image=img)

        self.video_label.imgtk = imgtk          # Prevent GC
        self.video_label.configure(image=imgtk)

        self._frame_info_var.set(f"Frame: {frame_number}")
        # Blink REC indicator
        self._rec_var.set("⏺ REC" if (frame_number // 15) % 2 == 0 else "   REC")

    def update_signal(self, state, timer):
        """Update the traffic light circles and text."""
        # Dim all
        self._red_cv.itemconfig(   self._rc, fill="#3d0000")
        self._yellow_cv.itemconfig(self._yc, fill="#3d3000")
        self._green_cv.itemconfig( self._gc, fill="#003d00")

        if state == "Red":
            self._red_cv.itemconfig(self._rc, fill="#ff3333")
            self._signal_state_var.set("● RED")
            self._signal_lbl.config(fg=RED_COL)

        elif state == "Yellow":
            self._yellow_cv.itemconfig(self._yc, fill="#ffd700")
            self._signal_state_var.set("● YELLOW")
            self._signal_lbl.config(fg=YELLOW_COL)

        elif state == "Green":
            self._green_cv.itemconfig(self._gc, fill="#00e676")
            self._signal_state_var.set("● GREEN")
            self._signal_lbl.config(fg=GREEN_COL)

        self._timer_var.set(f"Timer: {timer}s")

    def update_dashboard(self, vehicle_count, density, ambulance, violation, scenario):
        """Refresh all four info cards."""
        # Vehicle count
        self._vehicle_count_var.set(str(vehicle_count))

        # Density with colour coding
        density_fg = {"Low": GREEN_COL, "Medium": YELLOW_COL, "High": RED_COL}
        self._density_var.set(density)
        self._density_lbl.config(fg=density_fg.get(density, TEXT_MAIN))

        # Ambulance
        if ambulance:
            self._ambulance_var.set("YES — EMERGENCY!")
            self._ambulance_lbl.config(fg=RED_COL)
        else:
            self._ambulance_var.set("No")
            self._ambulance_lbl.config(fg=TEXT_MAIN)

        # Violation
        if violation:
            self._violation_var.set("YES — ALERT!")
            self._violation_lbl.config(fg=RED_COL)
        else:
            self._violation_var.set("No")
            self._violation_lbl.config(fg=TEXT_MAIN)

        # Scenario label at bottom of video
        self._scenario_label_var.set(f"Scenario: {scenario}")

    def log_message(self, msg):
        """Append a timestamped line to the status log."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"› {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def set_scenario_label(self, name):
        self._scenario_var.set(name)

    # ──────────────────────────────────────────────────────────────────────
    # Internal callbacks
    # ──────────────────────────────────────────────────────────────────────

    def _on_scenario_change(self, selected):
        """Called when user picks a new scenario from the dropdown."""
        self._scenario_cb(selected)
        self.log_message(f"Scenario → {selected}")