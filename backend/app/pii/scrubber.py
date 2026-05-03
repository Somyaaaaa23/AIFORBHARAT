import re

class PIIScrubber:
    def __init__(self):
        # Sensitive patterns
        self.patterns = {
            "email": r"[\w\.-]+@[\w\.-]+\.\w+",
            "phone": r"\b\d{10}\b",
            "aadhaar": r"\b\d{4}\s\d{4}\s\d{4}\b"
        }

    def scrub(self, data: dict) -> dict:
        """Recursively scrub PII from a dictionary"""
        scrubbed = {}
        for key, value in data.items():
            if isinstance(value, str):
                for label, pattern in self.patterns.items():
                    value = re.sub(pattern, f"[{label.upper()}_MASKED]", value)
                scrubbed[key] = value
            elif isinstance(value, dict):
                scrubbed[key] = self.scrub(value)
            else:
                scrubbed[key] = value
        return scrubbed

scrubber = PIIScrubber()
