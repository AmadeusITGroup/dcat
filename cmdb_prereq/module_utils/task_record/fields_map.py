class FieldsMap:

    def system_category_map(self, system_category):

        category_map={
        "test": "T",
        "production": "P",
        "T": "T",
        "P": "P"
        }
        return category_map[system_category]

    def change_type_map(self, change_type):

        change_type_map={
            "PAAS": "PAAS",
            "automation": "AUTO",
            "software": "SW",
            "infrastructure": "IS"
        }
        return change_type_map[change_type]

    def sub_type_map(self, sub_type):

        sub_type_map = {
                "storage_svc": "STOSVC",
                "vmware_guest": "VMWG",
                "dns": "DNS",
                "dhcp": "DHCP",
                "network": "NW"
            }
        return sub_type_map[sub_type]

    def action_type(self, action_type):

            action_type_map={
                        "monitoring_config": "MOCO",
                        "user_mgmt": "UMG",
                        "pen_test": "PT",
                        "os_upgrade": "TECOS"
                        }
            return action_type_map[action_type]
