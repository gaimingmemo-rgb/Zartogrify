import os
import customtkinter as ctk
from tkinter import messagebox

from modules.auth import AuthEngine
from modules.ai_engine import AIEngine
from modules.pc_scanner import PCScanner
from modules.executor import LocalExecutor
from modules.guardrails import GuardrailsEngine

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ZartogrifyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Zartogrify v2.2 - Open Source AI PC Controller (ZarTo's Studios)")
        self.geometry("1150x750")

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

        ctk.CTkLabel(container, text="⚡ ZARTOGRIFY ⚡", font=ctk.CTkFont(size=30, weight="bold"), text_color="#cba6f7").pack(pady=10)
        ctk.CTkLabel(container, text="Open-source local PC controller. Zero limits. Real Python power.", font=ctk.CTkFont(size=12), text_color="#a6adc8").pack(pady=5)

        card = ctk.CTkFrame(container, fg_color="#181825", corner_radius=14, border_width=1, border_color="#313244")
        card.pack(padx=20, pady=10, ipadx=25, ipady=20)

        ctk.CTkLabel(card, text="LOCAL AUTHENTICATION", font=ctk.CTkFont(size=12, weight="bold"), text_color="#89b4fa").pack(anchor="w", padx=5, pady=(0, 14))

        self.email_ent = ctk.CTkEntry(card, width=340, height=44, placeholder_text="Email address", fg_color="#1e1e2e", border_color="#45475a")
        self.email_ent.insert(0, "zarto@zartostudios.local")
        self.email_ent.pack(pady=6)

        self.pass_ent = ctk.CTkEntry(card, width=340, height=44, placeholder_text="Password", show="*", fg_color="#1e1e2e", border_color="#45475a")
        self.pass_ent.bind("<Return>", lambda event: self.handle_login())
        self.email_ent.bind("<Return>", lambda event: self.handle_login())
        self.pass_ent.insert(0, "password")
        self.pass_ent.pack(pady=6)

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(pady=15)

        ctk.CTkButton(btn_row, text="Register", fg_color="#a6e3a1", hover_color="#94e2d5", text_color="#11111b", font=ctk.CTkFont(weight="bold"), width=165, height=40, command=self.handle_register).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="Log In", fg_color="#89b4fa", hover_color="#b4befe", text_color="#11111b", font=ctk.CTkFont(weight="bold"), width=165, height=40, command=self.handle_login).pack(side="left", padx=5)

    def handle_register(self):
        email = self.email_ent.get()
        pwd = self.pass_ent.get()
        code = self.auth.register_email(email, pwd)
        
        ver = ctk.CTkToplevel(self)
        ver.title("Verification Code")
        ver.geometry("340x200")
        ver.attributes("-topmost", True)
        
        ctk.CTkLabel(ver, text=f"Enter 6-digit code sent to {email}:", font=ctk.CTkFont(size=11)).pack(pady=15)
        code_box = ctk.CTkEntry(ver, width=220, justify="center", font=ctk.CTkFont(size=14))
        code_box.pack(pady=5)
        
        def verify():
            if self.auth.verify_code(email, code_box.get()):
                messagebox.showinfo("Success", "Account verified successfully!")
                ver.destroy()
            else:
                messagebox.showerror("Error", "Invalid verification code.")

        ctk.CTkButton(ver, text="Verify Code", command=verify, fg_color="#a6e3a1", text_color="#11111b", font=ctk.CTkFont(weight="bold")).pack(pady=15)

    def handle_login(self):
        email = self.email_ent.get()
        pwd = self.pass_ent.get()
        if self.auth.login_email(email, pwd):
            self.build_workspace()
        else:
            messagebox.showerror("Error", "Invalid credentials or unverified email.")

    # --- 2. MAIN WORKSPACE ---
    def build_workspace(self):
        self.scanner.scan_installed_apps()
        self.clear_screen()

        # Sidebar
        sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#11111b")
        sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(sidebar, text="⚡ Zartogrify", font=ctk.CTkFont(size=18, weight="bold"), text_color="#cba6f7").pack(anchor="w", padx=20, pady=20)
        
        ctk.CTkButton(sidebar, text="+ New Session", fg_color="#313244", text_color="#fff", hover_color="#45475a", command=self.build_workspace).pack(fill="x", padx=15, pady=5)

        settings_btn = ctk.CTkButton(sidebar, text="⚙️ Settings & Models", fg_color="transparent", text_color="#89b4fa", hover_color="#313244", anchor="w", command=self.build_settings_page)
        settings_btn.pack(side="bottom", fill="x", padx=15, pady=20)

        # Main Workspace Panel
        main = ctk.CTkFrame(self, fg_color="#1e1e2e", corner_radius=0)
        main.pack(side="right", fill="both", expand=True)

        # Top Info Bar
        top = ctk.CTkFrame(main, height=50, fg_color="#181825", corner_radius=0)
        top.pack(fill="x")

        cfg = self.engine.config
        status_text = f"Provider: {cfg.get('active_provider', 'openrouter').upper()} | Model: {cfg.get('active_model', 'Default')}"
        self.status_lbl = ctk.CTkLabel(top, text=status_text, font=ctk.CTkFont(size=12, weight="bold"), text_color="#89b4fa")
        self.status_lbl.pack(side="left", padx=20, pady=12)

        ctk.CTkLabel(top, text=f"Indexed Apps: {len(self.scanner.indexed_apps)}", text_color="#a6adc8").pack(side="right", padx=20, pady=12)

        # Execution Step Console Output
        self.chat_box = ctk.CTkTextbox(main, fg_color="#181825", text_color="#cdd6f4", font=("Consolas", 11), corner_radius=10)
        self.chat_box.pack(fill="both", expand=True, padx=20, pady=15)
        self.chat_box.insert("end", "🤖 Zartogrify Engine v2.2 active.\nPress Enter or click Execute to run tasks directly on your PC sandbox.\n" + "="*70 + "\n\n")

        # Bottom Entry Bar
        input_frame = ctk.CTkFrame(main, fg_color="#181825", height=70, corner_radius=12)
        input_frame.pack(fill="x", padx=20, pady=20)

        self.prompt_ent = ctk.CTkEntry(input_frame, placeholder_text="Ask Zartogrify to code an app or control your PC...", height=48, font=ctk.CTkFont(size=13))
        self.prompt_ent.pack(side="left", fill="x", expand=True, padx=15, pady=12)
        
        # Enter key trigger
        self.prompt_ent.bind("<Return>", lambda event: self.run_prompt())

        send_btn = ctk.CTkButton(input_frame, text="Execute ⚡", width=120, height=48, fg_color="#89b4fa", text_color="#11111b", font=ctk.CTkFont(weight="bold"), command=self.run_prompt)
        send_btn.pack(side="right", padx=15, pady=12)

    # --- 3. SETTINGS & DYNAMIC MODEL SELECTOR ---
    def build_settings_page(self):
        self.clear_screen()

        container = ctk.CTkFrame(self, fg_color="#1e1e2e", corner_radius=0)
        container.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(container, text="⚙️ AI Provider & Model Configuration", font=ctk.CTkFont(size=22, weight="bold"), text_color="#cba6f7").pack(anchor="w", pady=(0, 20))

        cfg = self.engine.config

        ctk.CTkLabel(container, text="Select AI Provider:", font=ctk.CTkFont(weight="bold"), text_color="#89b4fa").pack(anchor="w", pady=5)
        
        providers = ["openrouter", "groq", "openai"]
        self.prov_menu = ctk.CTkOptionMenu(container, values=providers, command=self.on_provider_change, width=320, height=35)
        self.prov_menu.set(cfg.get("active_provider", "openrouter"))
        self.prov_menu.pack(anchor="w", pady=5)

        ctk.CTkLabel(container, text="Select or Type Model Identifier:", font=ctk.CTkFont(weight="bold"), text_color="#89b4fa").pack(anchor="w", pady=(15, 5))
        
        self.model_menu = ctk.CTkComboBox(container, values=self.get_models_for_provider(self.prov_menu.get()), width=480, height=38)
        self.model_menu.set(cfg.get("active_model", "google/gemini-2.0-flash-exp:free"))
        self.model_menu.pack(anchor="w", pady=5)

        ctk.CTkLabel(container, text="API Keys (Saved locally to config.json):", font=ctk.CTkFont(weight="bold"), text_color="#89b4fa").pack(anchor="w", pady=(20, 5))

        self.key_inputs = {}
        for p in ["openrouter", "groq", "openai"]:
            row = ctk.CTkFrame(container, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=f"{p.capitalize()} Key:", width=130, anchor="w", text_color="#a6adc8").pack(side="left")
            ent = ctk.CTkEntry(row, width=360, show="*", height=34)
            ent.insert(0, cfg.get("keys", {}).get(p, ""))
            ent.pack(side="left")
            self.key_inputs[p] = ent

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(anchor="w", pady=30)

        def save_settings():
            new_cfg = {
                "active_provider": self.prov_menu.get(),
                "active_model": self.model_menu.get(),
                "keys": {p: self.key_inputs[p].get() for p in self.key_inputs}
            }
            self.engine.save_config(new_cfg)
            messagebox.showinfo("Saved", "Settings successfully updated in config.json!")
            self.build_workspace()

        ctk.CTkButton(btn_row, text="Save Settings", fg_color="#a6e3a1", text_color="#11111b", font=ctk.CTkFont(weight="bold"), width=150, height=40, command=save_settings).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_row, text="Back to Workspace", fg_color="#313244", text_color="#fff", width=150, height=40, command=self.build_workspace).pack(side="left")

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
        self.log(f"\n👤 Prompt: {prompt}")

        # Step 1: Safety Filter
        safe, reason = GuardrailsEngine.inspect_prompt(prompt)
        if not safe:
            self.log(f"❌ {reason}")
            messagebox.showerror("Blocked by Guardrails", reason)
            return

        self.log("*Step 1/3: Security parameters verified.* 🟢")
        self.log("*Step 2/3: Querying AI Provider for runnable Python code...*")

        # Heavy App Generation System Prompt
        system_prompt = (
            "You are Zartogrify, an elite Python software builder and local PC controller. "
            "When asked to create an app (like a Notepad, calculator, utility, or dashboard), "
            "write a COMPLETE, FULL-FEATURED, non-stub Python program using tkinter/customtkinter. "
            "For example, a Notepad MUST include: main window, scrolled text area, File Menu (New, Open, Save As, Exit), "
            "active file writing/reading via tkinter.filedialog, and status feedback. "
            "Always wrap runnable code in clean ```python ... ``` blocks. Do not produce incomplete pseudocode."
        )

        ai_response = self.engine.generate_response(system_prompt, prompt)
        
        # Step 3: Subprocess Sandbox Run
        self.log("*Step 3/3: Running code syntax checks & launching local process...*")
        success, output = self.executor.execute_python_code(ai_response, self.log)
        
        if success:
            self.log(f"🎉 Execution Output:\n{output}\n" + "-"*70)
        else:
            self.log(f"❌ Execution Error:\n{output}\n" + "-"*70)

if __name__ == "__main__":
    app = ZartogrifyApp()
    app.mainloop()
