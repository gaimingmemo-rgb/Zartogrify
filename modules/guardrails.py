class GuardrailsEngine:
    BANNED_KEYWORDS = [
        "encrypt", "ransomware", "keylogger", "payload", 
        "format c:", "rmdir /s /q c:\\", "wipe disk", "wiper", 
        "disable defender", "stop antivirus", "shadowcopy delete"
    ]

    @staticmethod
    def inspect_prompt(prompt: str) -> tuple[bool, str]:
        p_lower = prompt.lower()
        for kw in GuardrailsEngine.BANNED_KEYWORDS:
            if kw in p_lower:
                return False, f"Blocked: Request contains unsafe keyword ('{kw}'). Malware/ransomware is forbidden."
        return True, "Safe"
