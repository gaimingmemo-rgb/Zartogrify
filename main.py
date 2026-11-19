import os
import customtkinter as ctk
from tkinter import messagebox

from modules.auth import AuthEngine
from modules.ai_engine import AIEngine
from modules.pc_scanner import PCScanner
from modules.executor import LocalExecutor
from modules.guardrails import GuardrailsEngine

# Theme: Project Revision Noir & Tactical Crimson
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Revision Color Palette
CLR_BG_VOID    = "#08090c"   # Pure dark void
CLR_PANEL      = "#0f131a"   # Deep slate panel
CLR_CARD       = "#141923"   # Card background
CLR_INPUT      = "#0b0e14"   # Input background
CLR_BORDER     = "#8f0e1e"   # Tactical crimson border
CLR_BORDER_DIM = "#202738"   # Subtle panel border
CLR_CRIMSON    = "#ff1e38"   # Vivid crimson accent
CLR_HOVER_RED  = "#ff3b52"   # Button hover red
CLR_GREEN      = "#00ff88"   # Tactical mesh green
CLR_CYAN       = "#00f0ff"   # Cyber telemetry cyan
CLR_TEXT_MAIN  = "#ffffff"   # Clean white text
CLR_TEXT_MUTED = "#8b949e"   # Secondary muted text
CLR_BTN_MUTED  = "#1a212e"   # Dark slate button
CLR_BTN_HOVER  = "#252f42"   # Slate button hover

class RevisionAIApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Revision-Ai v2.2 // Project Revision (Autonomous PC Controller)")
        self.geometry("1180x760")
        self.configure(fg_color=CLR_BG_VOID)

        # Core Engines (Preserved 100%)
        self.auth = AuthEngine()
        self.engine = AIEngine()
        self.scanner = PCScanner()
        self.executor = LocalExecutor()

        self.build_login_screen()

    def clear_screen(self):
        for w in self.winfo_children():
            w.destroy()

    # --- 1. LOCAL AUTHENTICATION SCREEN ---
    def build_login_screen(self):
        self.clear_screen()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True)

        ctk.CTkLabel(
            container, 
            text="⚡ REVISION-AI ⚡", 
            font=ctk.CTkFont(family="Consolas", size=32, weight="bold"), 
            text_color=CLR_CRIMSON
        ).pack(pady=(0, 6))

        ctk.CTkLabel(
            container, 
            text="Autonomous Local PC Controller & Automation Suite // Project Revision", 
            font=ctk.CTkFont(size=12), 
            text_color=CLR_TEXT_MUTED
        ).pack(pady=(0, 20))

        card = ctk.CTkFrame(
            container, 
            fg_color=CLR_CARD, 
            corner_radius=10, 
            border_width=2, 
            border_color=CLR_BORDER
        )
        card.pack(padx=20, pady=10, ipadx=30, ipady=24)

        ctk.CTkLabel(
            card, 
            text="OPERATOR AUTHENTICATION", 
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"), 
            text_color=CLR_CRIMSON
        ).pack(anchor="w", padx=5, pady=(0, 16))

        self.email_ent = ctk.CTkEntry(
            card, 
            width=360, 
            height=44, 
            placeholder_text="Operator email", 
            fg_color=CLR_INPUT, 
            border_color=CLR_BORDER_DIM,
            text_color=CLR_TEXT_MAIN
        )
        self.email_ent.insert(0, "operator@revision.local")
        self.email_ent.pack(pady=7)

        self.pass_ent = ctk.CTkEntry(
            card, 
            width=360, 
            height=44, 
            placeholder_text="Access key / Password", 
            show="*", 
            fg_color=CLR_INPUT, 
            border_color=CLR_BORDER_DIM,
            text_color=CLR_TEXT_MAIN
        )
        self.pass_ent.bind("<Return>", lambda event: self.handle_login())
        self.email_ent.bind("<Return>", lambda event: self.handle_login())
        self.pass_ent.insert(0, "password")
        self.pass_ent.pack(pady=7)

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(pady=(16, 5))

        ctk.CTkButton(
            btn_row, 
            text="Register Node", 
            fg_color=CLR_BTN_MUTED, 
            hover_color=CLR_BTN_HOVER, 
            text_color=CLR_TEXT_MUTED, 
            font=ctk.CTkFont(weight="bold"), 
            width=175, 
            height=42, 
            command=self.handle_register
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_row, 
            text="Authorize ➔", 
            fg_color=CLR_CRIMSON, 
            hover_color=CLR_HOVER_RED, 
            text_color="#ffffff", 
            font=ctk.CTkFont(weight="bold"), 
            width=175, 
            height=42, 
            command=self.handle_login
        ).pack(side="left", padx=5)

    def handle_register(self):
        email = self.email_ent.get()
        pwd = self.pass_ent.get()
        code = self.auth.register_email(email, pwd)
        
        ver = ctk.CTkToplevel(self)
        ver.title("Revision-Ai Node Verification")
        ver.geometry("360x220")
        ver.configure(fg_color=CLR_BG_VOID)
        ver.attributes("-topmost", True)
        
        ctk.CTkLabel(
            ver, 
            text=f"Enter 6-digit verification code sent to:\n{email}", 
            font=ctk.CTkFont(size=11),
            text_color=CLR_TEXT_MUTED
        ).pack(pady=15)

        code_box = ctk.CTkEntry(
            ver, 
            width=220, 
            justify="center", 
            font=ctk.CTkFont(family="Consolas", size=16),
            fg_color=CLR_INPUT,
            border_color=CLR_BORDER
        )
        code_box.pack(pady=5)
        
        def verify():
            if self.auth.verify_code(email, code_box.get()):
                messagebox.showinfo("Success", "Node verified successfully! You may now log in.")
                ver.destroy()
            else:
                messagebox.showerror("Error", "Invalid verification code.")

        ctk.CTkButton(
            ver, 
            text="Verify Node", 
            command=verify, 
            fg_color=CLR_CRIMSON, 
            hover_color=CLR_HOVER_RED, 
            text_color="#ffffff", 
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=15)

    def handle_login(self):
        email = self.email_ent.get()
        pwd = self.pass_ent.get()
        if self.auth.login_email(email, pwd):
            self.build_workspace()
        else:
            messagebox.showerror("Access Denied", "Invalid credentials or unverified node.")

    # --- 2. MAIN WORKSPACE ---
    def build_workspace(self):
        self.scanner.scan_installed_apps()
        self.clear_screen()

        # Sidebar
        sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=CLR_PANEL, border_width=1, border_color=CLR_BORDER_DIM)
        sidebar.pack(side="left", fill="y")

        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(anchor="w", padx=20, pady=(25, 20))

        ctk.CTkLabel(
            logo_frame, 
            text="⚡ REVISION-AI", 
            font=ctk.CTkFont(family="Consolas", size=18, weight="bold"), 
            text_color=CLR_CRIMSON
        ).pack(anchor="w")

        ctk.CTkLabel(
            logo_frame, 
            text="Project Revision Core v2.2", 
            font=ctk.CTkFont(size=10), 
            text_color=CLR_TEXT_MUTED
        ).pack(anchor="w")
        
        ctk.CTkButton(
            sidebar, 
            text="+ New Operation", 
            fg_color=CLR_BTN_MUTED, 
            text_color=CLR_TEXT_MAIN, 
            hover_color=CLR_BTN_HOVER, 
            command=self.build_workspace,
            height=36,
            corner_radius=6
        ).pack(fill="x", padx=16, pady=8)

        # Quick Links / Info in sidebar
        mesh_box = ctk.CTkFrame(sidebar, fg_color=CLR_CARD, corner_radius=8, border_width=1, border_color=CLR_BORDER_DIM)
        mesh_box.pack(fill="x", padx=16, pady=16, ipady=8)

        ctk.CTkLabel(
            mesh_box, 
            text="● ECO MESH ACTIVE", 
            font=ctk.CTkFont(family="Consolas", size=10, weight="bold"), 
            text_color=CLR_GREEN
        ).pack(anchor="w", padx=12, pady=(8, 2))

        ctk.CTkLabel(
            mesh_box, 
            text="Port 8766 // Shared Gateway\nRev-Network Distribution Bay", 
            font=ctk.CTkFont(size=9), 
            text_color=CLR_TEXT_MUTED,
            justify="left"
        ).pack(anchor="w", padx=12, pady=(0, 8))

        settings_btn = ctk.CTkButton(
            sidebar, 
            text="⚙️ Engine & Models", 
            fg_color="transparent", 
            text_color=CLR_CYAN, 
            hover_color=CLR_BTN_HOVER, 
            anchor="w", 
            command=self.build_settings_page,
            height=38
        )
        settings_btn.pack(side="bottom", fill="x", padx=16, pady=20)

        # Main Workspace Panel
        main = ctk.CTkFrame(self, fg_color=CLR_BG_VOID, corner_radius=0)
        main.pack(side="right", fill="both", expand=True)

        # Top Info Bar
        top = ctk.CTkFrame(main, height=52, fg_color=CLR_PANEL, corner_radius=0, border_width=1, border_color=CLR_BORDER_DIM)
        top.pack(fill="x")

        cfg = self.engine.config
        prov = cfg.get('active_provider', 'openrouter').upper()
        model_name = cfg.get('active_model', 'Default')
        status_text = f"PROVIDER: {prov}  |  ACTIVE MODEL: {model_name}"
        
        self.status_lbl = ctk.CTkLabel(
            top, 
            text=status_text, 
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"), 
            text_color=CLR_CYAN
        )
        self.status_lbl.pack(side="left", padx=20, pady=14)

        ctk.CTkLabel(
            top, 
            text=f"Indexed PC Apps: {len(self.scanner.indexed_apps)}", 
            font=ctk.CTkFont(size=11),
            text_color=CLR_GREEN
        ).pack(side="right", padx=20, pady=14)

        # Execution Step Console Output
        self.chat_box = ctk.CTkTextbox(
            main, 
            fg_color=CLR_INPUT, 
            text_color="#e6edf3", 
            font=("Consolas", 11), 
            corner_radius=8,
            border_width=1,
            border_color=CLR_BORDER_DIM
        )
        self.chat_box.pack(fill="both", expand=True, padx=20, pady=16)
        
        welcome_msg = (
            "===========================================================================\n"
            "       ⚡ REVISION-AI // AUTONOMOUS PC CONTROLLER (v2.2) ⚡\n"
            "===========================================================================\n"
            "[*] Status: Connected to Project Revision Network\n"
            "[*] Engine: Autonomous Python Execution Sandbox Active\n"
            "[*] Type any task below to build applications, automate workflows, or scan files.\n"
            "===========================================================================\n\n"
        )
        self.chat_box.insert("end", welcome_msg)

        # Bottom Entry Bar
        input_frame = ctk.CTkFrame(
            main, 
            fg_color=CLR_PANEL, 
            height=72, 
            corner_radius=10, 
            border_width=1, 
            border_color=CLR_BORDER
        )
        input_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.prompt_ent = ctk.CTkEntry(
            input_frame, 
            placeholder_text="Command Revision-Ai to create apps, write code, or automate PC tasks...", 
            height=48, 
            font=ctk.CTkFont(size=13),
            fg_color=CLR_INPUT,
            border_color=CLR_BORDER_DIM,
            text_color=CLR_TEXT_MAIN
        )
        self.prompt_ent.pack(side="left", fill="x", expand=True, padx=15, pady=12)
        
        self.prompt_ent.bind("<Return>", lambda event: self.run_prompt())

        send_btn = ctk.CTkButton(
            input_frame, 
            text="EXECUTE ⚡", 
            width=130, 
            height=46, 
            fg_color=CLR_CRIMSON, 
            hover_color=CLR_HOVER_RED, 
            text_color="#ffffff", 
            font=ctk.CTkFont(weight="bold"), 
            command=self.run_prompt
        )
        send_btn.pack(side="right", padx=15, pady=12)

    # --- 3. SETTINGS & DYNAMIC MODEL SELECTOR ---
    def build_settings_page(self):
        self.clear_screen()

        container = ctk.CTkFrame(self, fg_color=CLR_BG_VOID, corner_radius=0)
        container.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(
            container, 
            text="⚙️ Revision-Ai Engine & Model Configuration", 
            font=ctk.CTkFont(family="Consolas", size=22, weight="bold"), 
            text_color=CLR_CRIMSON
        ).pack(anchor="w", pady=(0, 20))

        cfg = self.engine.config

        ctk.CTkLabel(container, text="Active AI Provider:", font=ctk.CTkFont(weight="bold"), text_color=CLR_CYAN).pack(anchor="w", pady=5)
        
        providers = ["openrouter", "groq", "openai"]
        self.prov_menu = ctk.CTkOptionMenu(
            container, 
            values=providers, 
            command=self.on_provider_change, 
            width=320, 
            height=36,
            fg_color=CLR_CARD,
            button_color=CLR_BORDER,
            button_hover_color=CLR_CRIMSON
        )
        self.prov_menu.set(cfg.get("active_provider", "openrouter"))
        self.prov_menu.pack(anchor="w", pady=5)

        ctk.CTkLabel(container, text="Model Identifier:", font=ctk.CTkFont(weight="bold"), text_color=CLR_CYAN).pack(anchor="w", pady=(15, 5))
        
        self.model_menu = ctk.CTkComboBox(
            container, 
            values=self.get_models_for_provider(self.prov_menu.get()), 
            width=480, 
            height=38,
            fg_color=CLR_INPUT,
            border_color=CLR_BORDER_DIM
        )
        self.model_menu.set(cfg.get("active_model", "google/gemini-2.0-flash-exp:free"))
        self.model_menu.pack(anchor="w", pady=5)

        ctk.CTkLabel(container, text="API Keys (Stored locally in config.json):", font=ctk.CTkFont(weight="bold"), text_color=CLR_CYAN).pack(anchor="w", pady=(20, 5))

        self.key_inputs = {}
        for p in ["openrouter", "groq", "openai"]:
            row = ctk.CTkFrame(container, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=f"{p.capitalize()} Key:", width=130, anchor="w", text_color=CLR_TEXT_MUTED).pack(side="left")
            ent = ctk.CTkEntry(row, width=380, show="*", height=36, fg_color=CLR_INPUT, border_color=CLR_BORDER_DIM, text_color=CLR_TEXT_MAIN)
            ent.insert(0, cfg.get("keys", {}).get(p, ""))
            ent.pack(side="left")
            self.key_inputs[p] = ent

        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack(anchor="w", pady=30)

        def save_settings():
            new_cfg = {
                "active_provider": self.prov_menu.get(),
                "active_model": self.model_menu.get(),
                "keys": {p: self.key_inputs[p].get() for p in self.key_inputs}
            }
            self.engine.save_config(new_cfg)
            messagebox.showinfo("Configuration Updated", "Revision-Ai settings successfully saved!")
            self.build_workspace()

        ctk.CTkButton(
            btn_row, 
            text="Save Settings", 
            fg_color=CLR_CRIMSON, 
            hover_color=CLR_HOVER_RED, 
            text_color="#ffffff", 
            font=ctk.CTkFont(weight="bold"), 
            width=160, 
            height=42, 
            command=save_settings
        ).pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            btn_row, 
            text="Return to Workspace", 
            fg_color=CLR_BTN_MUTED, 
            hover_color=CLR_BTN_HOVER, 
            text_color=CLR_TEXT_MAIN, 
            width=170, 
            height=42, 
            command=self.build_workspace
        ).pack(side="left")

    def on_provider_change(self, choice):
        models = self.get_models_for_provider(choice)
        self.model_menu.configure(values=models)
        if models:
            self.model_menu.set(models[0])

    def get_models_for_provider(self, provider):
        if provider == "openrouter":
            return [
                "google/gemini-2.0-flash-exp:free",
                "google/gemini-flash-1.5",
                "meta-llama/llama-3.3-70b-instruct",
                "anthropic/claude-3.5-sonnet",
                "deepseek/deepseek-chat"
            ]
        elif provider == "groq":
            return [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "mixtral-8x7b-32768"
            ]
        elif provider == "openai":
            return [
                "gpt-4o-mini",
                "gpt-4o",
                "o3-mini"
            ]
        return ["default-model"]

    def log(self, text):
        self.chat_box.insert("end", text + "\n")
        self.chat_box.see("end")
        self.update_idletasks()

    def run_prompt(self):
        prompt = self.prompt_ent.get()
        if not prompt:
            return

        self.prompt_ent.delete(0, 'end')
        self.log(f"\n👤 Operator: {prompt}")

        # Step 1: Safety Filter
        safe, reason = GuardrailsEngine.inspect_prompt(prompt)
        if not safe:
            self.log(f"❌ {reason}")
            messagebox.showerror("Blocked by Guardrails", reason)
            return

        self.log("[*] Security parameters verified. 🟢")
        self.log("[*] Synthesizing execution model via AI Provider...")

        system_prompt = (
            "You are Revision-Ai, an elite autonomous Python systems builder and local PC controller "
            "for Project Revision. When asked to create an application (like a Notepad, calculator, utility, or dashboard), "
            "write a COMPLETE, FULL-FEATURED, non-stub Python program using tkinter or customtkinter. "
            "For example, a Notepad MUST include: main window, scrolled text area, File Menu (New, Open, Save As, Exit), "
            "active file writing/reading via tkinter.filedialog, and status feedback. "
            "Always wrap runnable code in clean ```python ... ``` blocks. Do not produce incomplete pseudocode."
        )

        ai_response = self.engine.generate_response(system_prompt, prompt)
        
        # Step 3: Subprocess Sandbox Run
        self.log("[*] Verifying AST syntax & executing process in local sandbox...")
        success, output = self.executor.execute_python_code(ai_response, self.log)
        
        if success:
            self.log(f"🎉 Process Output:\n{output}\n" + "-"*75)
        else:
            self.log(f"❌ Execution Traceback:\n{output}\n" + "-"*75)

if __name__ == "__main__":
    try:
        from modules.mesh_node import start_mesh_node
        start_mesh_node(app_name="Revision-Ai-v2.2")
    except Exception:
        pass
    app = RevisionAIApp()
    app.mainloop()
