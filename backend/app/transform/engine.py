class TransformEngine:
    def __init__(self):
        # Mappings for different departments
        self.mappings = {
            "FACTORIES": {
                "address": "factory_location",
                "ubid": "uuid_key"
            },
            "LABOUR": {
                "address": "reg_office_address",
                "ubid": "emp_id_ref"
            }
        }

    def transform(self, payload: dict, target_dept: str) -> dict:
        mapping = self.mappings.get(target_dept, {})
        transformed = {}
        for k, v in payload.items():
            new_key = mapping.get(k, k)
            transformed[new_key] = v
        return transformed

transformer = TransformEngine()
